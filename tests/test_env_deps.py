import pytest
from envault.env_deps import parse_deps, DepGraph, format_graph
from envault.vault import init_vault
from envault.commands import cmd_push
import argparse
import os


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / '.envault')
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / '.env'
    p.write_text('HOST=localhost\nPORT=5432\nDB_URL=${HOST}:${PORT}/mydb\nSECRET=abc\n')
    return str(p)


def push(vault_dir, env_file, password='pass'):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_parse_deps_finds_references():
    text = 'HOST=localhost\nDB_URL=${HOST}:5432/db\n'
    graph = parse_deps(text)
    assert 'HOST' in graph.dependencies_of('DB_URL')


def test_parse_deps_ignores_self_reference():
    text = 'KEY=${KEY}\n'
    graph = parse_deps(text)
    assert 'KEY' not in graph.dependencies_of('KEY')


def test_parse_deps_no_deps():
    text = 'A=1\nB=2\n'
    graph = parse_deps(text)
    assert not graph.edges


def test_dependents_of():
    text = 'HOST=localhost\nURL1=${HOST}/a\nURL2=${HOST}/b\n'
    graph = parse_deps(text)
    dependents = graph.dependents_of('HOST')
    assert 'URL1' in dependents
    assert 'URL2' in dependents


def test_dependencies_of_missing_key():
    graph = DepGraph()
    assert graph.dependencies_of('MISSING') == set()


def test_format_graph_empty():
    graph = DepGraph()
    result = format_graph(graph)
    assert 'no dependencies' in result


def test_format_graph_shows_edges():
    text = 'HOST=localhost\nDB_URL=${HOST}:5432\n'
    graph = parse_deps(text)
    result = format_graph(graph)
    assert 'DB_URL' in result
    assert 'HOST' in result


def test_deps_for_version(vault_dir, env_file):
    push(vault_dir, env_file)
    from envault.env_deps import deps_for_version
    graph = deps_for_version(vault_dir, 1, 'pass')
    assert isinstance(graph, DepGraph)
    assert 'DB_URL' in graph.edges


def test_deps_for_version_invalid(vault_dir, env_file):
    push(vault_dir, env_file)
    from envault.env_deps import deps_for_version
    with pytest.raises(ValueError, match='not found'):
        deps_for_version(vault_dir, 999, 'pass')
