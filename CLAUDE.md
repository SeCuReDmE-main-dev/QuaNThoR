# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This repository contains multiple projects:

1. **`mizar-devcontainer-Secured_Me-version-0.01/`** - Main Mizar DevContainer environment for formal mathematical verification
2. **`google-proofreader-api/`** - Google Proofreader API documentation and examples

## Mizar DevContainer Project

### Core Components

- **`src/app.py`** - Flask web server providing REST API for Mizar proof verification
- **`verify.py`** - Command-line tool for verifying Mizar proofs
- **`tests/`** - Comprehensive test suite with pytest
- **`.devcontainer/`** - Dev Container configuration with pre-installed Mizar environment

### Common Commands

#### Running the Web Server
```bash
# Start Flask development server on port 5000
python src/app.py

# Alternative platform-specific scripts
./start_server.ps1    # PowerShell
./start_server.bat    # Windows Command Prompt
```

#### Command-Line Verification
```bash
# Verify a Mizar proof file
python verify.py path/to/proof.miz

# Platform-specific verification scripts
./verify.ps1 proof.miz    # PowerShell
./verify.bat proof.miz    # Windows Command Prompt
```

#### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_server.py
python -m pytest tests/test_verify.py
python -m pytest tests/test_integration.py
```

### Development Setup

The project is designed for GitHub Codespaces or VS Code Dev Containers with:
- Python 3.12 environment
- Flask 3.0.3 web framework
- Mizar 8.1.15 formal verification system pre-installed
- MML 5.94.1493 (Mizar Mathematical Library)

### API Endpoints

#### `POST /verify`
Verifies Mizar proofs via JSON API.

**Request:**
```json
{
  "code": "environ\n\nbegin\n\ntheorem T1: 1 = 1;\nproof\n  thus 1 = 1;\nend;"
}
```

**Response:**
```json
{
  "status": "success|failure|error",
  "errors": [{"line": 1, "character": 5, "message": "error description"}],
  "raw_output": "full verifier output"
}
```

### Mizar Verification Process

The system uses `/mizar/verifymain` executable in the dev container environment. For local installations, it may use `mizf`. The verifier processes `.miz` files through temporary file handling with 30-second timeouts.

### Environment Variables

- `MIZFILES` - Path to Mizar library files (typically `/usr/local/share/mizar`)
- `PATH` - Updated to include Mizar executables (`/usr/local/bin`)

### Dependencies

**Runtime:**
- Flask==3.0.3

**Development:**
- pytest
- pytest-mock
- requests

## Google Proofreader API

Documentation and specification for the proposed Web API for real-time proofreading functionality using browser-integrated language models. This is a design proposal, not implementation code.