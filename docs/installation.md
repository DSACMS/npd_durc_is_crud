# Installation Guide

## Installing from PyPI

Once the package is published to PyPI, you can install it using pip:

```bash
pip install durc-is-crud
```

## Installing from Source

To install the package from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/ftrotter/durc_is_crud.git
   cd durc_is_crud
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Adding to Your Django Project

1. Add `durc_is_crud` to your `INSTALLED_APPS` in your Django settings:

   ```python
   INSTALLED_APPS = [
       # ...
       'durc_is_crud',
       # ...
   ]
   ```

2. Make sure your database settings are properly configured in your Django settings.

## Development Setup

If you want to contribute to the development of durc_is_crud:

1. Clone the repository:
   ```bash
   git clone https://github.com/ftrotter/durc_is_crud.git
   cd durc_is_crud
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   # or
   pip install -r requirements.txt
   ```

4. Run tests:
   ```bash
   pytest
