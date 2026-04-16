# envault

> A CLI tool to encrypt and version-control `.env` files with team-sharing support.

---

## Installation

```bash
pip install envault
```

Or with pipx:

```bash
pipx install envault
```

---

## Usage

**Initialize envault in your project:**
```bash
envault init
```

**Encrypt your `.env` file:**
```bash
envault lock .env
```

**Decrypt and restore your `.env` file:**
```bash
envault unlock .env.vault
```

**Share with your team by committing the `.env.vault` file and distributing the key securely:**
```bash
envault keygen --share teammate@example.com
```

> ⚠️ Never commit your raw `.env` file. Add it to `.gitignore` and commit `.env.vault` instead.

---

## How It Works

1. `envault lock` encrypts your `.env` using AES-256 and saves a `.env.vault` file
2. The `.env.vault` file is safe to commit to version control
3. Team members run `envault unlock` with the shared key to restore the original file

---

## License

This project is licensed under the [MIT License](LICENSE).