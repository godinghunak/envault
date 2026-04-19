import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_copy import copy_keys, copy_all_keys, CopyError
from envault.crypto import decrypt_file
from envault.vault import load_manifest
from envault.diff import parse_env
import types

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    init_vault(str(d))
    return str(d)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("A=1\nB=2\nC=3\n")
    return str(f)


def push(vault_dir, env_file, content=None, tmp_path=None):
    args = types.SimpleNamespace(
        vault_dir=vault_dir,
        env_file=env_file,
        password=PASSWORD,
    )
    if content is not None:
        Path(env_file).write_text(content)
    cmd_push(args)


def test_copy_keys_creates_new_version(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    Path(env_file).write_text("A=10\nD=4\n")
    push(vault_dir, env_file)

    new_v = copy_keys(vault_dir, 1, 2, ["B", "C"], PASSWORD)
    assert new_v == 3


def test_copy_keys_content_merged(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    Path(env_file).write_text("A=10\nD=4\n")
    push(vault_dir, env_file)

    copy_keys(vault_dir, 1, 2, ["B"], PASSWORD)

    manifest = load_manifest(vault_dir)
    v3 = next(v for v in manifest["versions"] if v["version"] == 3)
    text = decrypt_file(v3["path"], PASSWORD)
    env = parse_env(text)
    assert env["B"] == "2"
    assert env["A"] == "10"
    assert env["D"] == "4"


def test_copy_keys_missing_key_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    Path(env_file).write_text("X=9\n")
    push(vault_dir, env_file)

    with pytest.raises(CopyError, match="Keys not found"):
        copy_keys(vault_dir, 1, 2, ["MISSING"], PASSWORD)


def test_copy_keys_conflict_no_overwrite_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    Path(env_file).write_text("A=99\n")
    push(vault_dir, env_file)

    with pytest.raises(CopyError, match="already exist"):
        copy_keys(vault_dir, 1, 2, ["A"], PASSWORD, overwrite=False)


def test_copy_keys_conflict_overwrite_succeeds(vault_dir, env_file):
    push(vault_dir, env_file)
    Path(env_file).write_text("A=99\n")
    push(vault_dir, env_file)

    new_v = copy_keys(vault_dir, 1, 2, ["A"], PASSWORD, overwrite=True)
    manifest = load_manifest(vault_dir)
    v3 = next(v for v in manifest["versions"] if v["version"] == new_v)
    text = decrypt_file(v3["path"], PASSWORD)
    env = parse_env(text)
    assert env["A"] == "1"


def test_copy_all_keys(vault_dir, env_file):
    push(vault_dir, env_file)
    Path(env_file).write_text("X=9\n")
    push(vault_dir, env_file)

    new_v = copy_all_keys(vault_dir, 1, 2, PASSWORD, overwrite=True)
    manifest = load_manifest(vault_dir)
    v3 = next(v for v in manifest["versions"] if v["version"] == new_v)
    text = decrypt_file(v3["path"], PASSWORD)
    env = parse_env(text)
    assert "A" in env and "B" in env and "C" in env


def test_copy_invalid_src_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(CopyError, match="Source version"):
        copy_keys(vault_dir, 99, 1, ["A"], PASSWORD)


def test_copy_invalid_dst_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(CopyError, match="Destination version"):
        copy_keys(vault_dir, 1, 99, ["A"], PASSWORD)
