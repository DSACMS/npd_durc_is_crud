# DURC Is CRUD

DURC (Database to CRUD) is a Python package that simplifies the process of generating CRUD (Create, Read, Update, Delete) operations from database schemas. It automatically extracts relational models from your database and generates the necessary code artifacts.

## Features

- **Database Schema Extraction**: Automatically extract database schema information including tables, columns, primary keys, foreign keys, and relationships.
- **Relationship Detection**: Automatically detect relationships between tables based on foreign keys and naming conventions.
- **Code Generation**: Generate code artifacts based on the extracted relational model (currently a placeholder, with full implementation coming soon).
- **PostgreSQL Support**: Currently optimized for PostgreSQL databases, with plans to support other database systems in the future.
- **Django Integration**: Seamlessly integrates with Django projects through management commands.

## Installation

```bash
# Basic installation (includes testing capabilities)
pip install durc-is-crud

# Installation with development dependencies (for contributors)
pip install durc-is-crud[dev]
```

For detailed installation instructions, see the [Installation Guide](docs/installation.md).

## Quick Start

1. Add `durc_is_crud` to your `INSTALLED_APPS` in your Django settings:

   ```python
   INSTALLED_APPS = [
       # ...
       'durc_is_crud',
       # ...
   ]
   ```

2. Extract the relational model from your database:

   ```bash
   python manage.py durc_mine --include mydb.public
   ```

3. Compile the relational model into code artifacts:

   ```bash
   python manage.py durc_compile
   ```

4. Run tests for the DURC package:

   ```bash
   # Run all tests (both standalone and Django-dependent)
   python manage.py durc_test

   # Run only standalone tests that don't require Django
   python manage.py durc_test --standalone-only

   # Run only tests that require Django
   python manage.py durc_test --django-only
   ```

For more detailed usage instructions, see the [Usage Guide](docs/usage.md).

## Documentation

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Testing Guide](tests/README.md)

## Requirements

- Python 3.6+
- Django 3.0+

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
