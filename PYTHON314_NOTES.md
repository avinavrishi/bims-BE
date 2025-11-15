# Python 3.14 Compatibility Notes

## SQLAlchemy Compatibility Issue

If you're using **Python 3.14**, you may encounter this error when running the server:

```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly but has additional attributes {'__static_attributes__', '__firstlineno__'}.
```

## Solution

Python 3.14 is very new, and SQLAlchemy 2.0.44 (stable) has compatibility issues with it. 

### Option 1: Use Setup Script (Easiest - Recommended)

Run the automated setup script:

```bash
python setup_sqlalchemy.py
```

This will:
- Detect Python 3.14
- Install the development version of SQLAlchemy
- Verify the installation works

### Option 2: Manual Installation

Install the development version of SQLAlchemy manually:

```bash
pip install --upgrade --force-reinstall git+https://github.com/sqlalchemy/sqlalchemy.git
```

This installs SQLAlchemy 2.1.0b1.dev0 (development version) which works with Python 3.14.

### Option 3: Use Python 3.11 or 3.12 (Recommended for Production)

For production environments, it's recommended to use Python 3.11 or 3.12, which are:
- More stable
- Better tested with all dependencies
- Widely supported

You can install Python 3.12 and create a new virtual environment:

```bash
# Create new venv with Python 3.12
python3.12 -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Current Status

- ✅ **Development SQLAlchemy (2.1.0b1.dev0)**: Works with Python 3.14
- ⚠️ **Stable SQLAlchemy (2.0.44)**: Has compatibility issues with Python 3.14
- ✅ **Python 3.11/3.12**: Fully compatible with stable SQLAlchemy

## Future Updates

When SQLAlchemy releases a stable version (2.1.0+) with full Python 3.14 support, you can switch back to the stable version:

```bash
pip install sqlalchemy>=2.1.0
```

