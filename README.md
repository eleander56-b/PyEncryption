# PyEncryption

File encryption tool with AES-256-GCM.

## Features

- **AES-256-GCM** authenticated encryption with PBKDF2 key derivation (600k iterations)
- **Single file** and **folder** encryption/decryption
- **CLI** with `click` and **GUI** with Tkinter
- Cross-platform (Windows, macOS, Linux)

## Installation

```bash
# Core (CLI only)
pip install .

# With GUI support
pip install ".[gui]"

# Development
pip install -e ".[dev]"
```

## Usage

### CLI

```bash
# Encrypt a file (will prompt for password)
python -m pyencryption encrypt myfile.txt

# Encrypt with password flag
python -m pyencryption encrypt myfile.txt -p "my-password"

# Decrypt
python -m pyencryption decrypt myfile.txt.enc -p "my-password"

# Encrypt an entire folder
python -m pyencryption encrypt ./my-folder -r -p "my-password"

# Decrypt a folder
python -m pyencryption decrypt ./my-folder_encrypted -r -p "my-password"

# Launch GUI
python -m pyencryption gui
```

### GUI

Launch with `python -m pyencryption gui`. The GUI provides:
- File or folder mode
- Password entry with show/hide toggle
- Progress bar for folder operations
- Log output

## Security

- Uses the `cryptography` library
- Key derivation: PBKDF2-HMAC-SHA256 with 600,000 iterations and random salt
- Encryption: AES-256-GCM with random 12-byte nonce
- Authentication: GCM tag detects tampering and wrong passwords
- File format: `[PYEN magic][version][salt][nonce][ciphertext][GCM tag]`
- Original files are preserved; encrypted output has `.enc` extension

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linter
ruff check src/ tests/

# Run type checker
mypy src/pyencryption/

# Run tests with coverage
pytest tests/ -m "not gui" --cov=pyencryption --cov-report=term-missing
```

## License

MIT
