# DURC Is CRUD

DURC (Database to CRUD) is a Python package that simplifies the process of generating CRUD (Create, Read, Update, Delete) operations from database schemas. It automatically extracts relational models from your database and generates the necessary code artifacts.

## Features

- **Database Schema Extraction**: Automatically extract database schema information including tables, columns, primary keys, foreign keys, and relationships.
- **Relationship Detection**: Automatically detect relationships between tables based on foreign keys and naming conventions.
- **Code Generation**: Generate code artifacts based on the extracted relational model (currently a placeholder, with full implementation coming soon).
- **PostgreSQL Support**: Currently optimized for PostgreSQL databases, with plans to support other database systems in the future.
- **Django Integration**: Seamlessly integrates with Django projects through management commands.

## Installation

### For End Users

1. After installing and initially setting up your Django instance, use pip to install durc with: 

```bash
# Basic installation (includes testing capabilities)
pip install durc-is-crud

# Installation with development dependencies (for contributors)
pip install durc-is-crud[dev]
```

2. Add `durc_is_crud` to your `INSTALLED_APPS` in your Django settings:

   ```python
   INSTALLED_APPS = [
       # ...
       'durc_is_crud',
       # ...
   ]
   ```

### For Local Development

If you want to contribute to DURC or set up a local development environment, follow these steps:

#### Prerequisites

- Python 3.9+ (required by pyproject.toml)
- Django 3.0+
- PostgreSQL (for database operations)
- Git

#### Step 1: Clone and Set Up Virtual Environment

```bash
# Clone the repository
git clone https://github.com/ftrotter/durc_is_crud.git
cd durc_is_crud

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or use the provided script
source source_me_to_get_venv.sh
```

#### Step 2: Install Dependencies

```bash
# Install the package in development mode with all dependencies
pip install -e .

# Or install with development dependencies
pip install -e .[dev]

# Or use the build script
./scripts/build_and_install.sh
```

#### Step 3: Verify Installation

```bash
# Test that all commands are available
python -c "import durc_is_crud; print('Package imported successfully')"

# Test standalone CLI command
durc-mine-fkeys --help

# If you have a Django project, test Django commands
python manage.py durc_mine --help
python manage.py durc_compile --help
python manage.py durc_diagram --help
python manage.py durc_mine_fkeys --help
python manage.py durc_test --help
```

## Usage

### Django Management Commands

Once installed, DURC provides several Django management commands:

1. **Extract the relational model from your database:**

   ```bash
   python manage.py durc_mine --include mydb.public
   
   # Multiple patterns
   python manage.py durc_mine --include mydb.public mydb.private
   
   # Custom output file
   python manage.py durc_mine --include mydb.public --output_json_file custom/model.json
   ```

2. **Compile the relational model into code artifacts:**

   ```bash
   python manage.py durc_compile
   ```

3. **Generate database diagrams from SQL files:**

   ```bash
   python manage.py durc_diagram --sql_files schema.sql --output_md_file diagram.md
   
   # Multiple SQL files
   python manage.py durc_diagram --sql_files file1.sql file2.sql --output_md_file combined_diagram.md
   ```

4. **Generate foreign key statements:**

   ```bash
   python manage.py durc_mine_fkeys --include mydb.public
   ```

5. **Run tests for the DURC package:**

   ```bash
   # Run all tests (both standalone and Django-dependent)
   python manage.py durc_test

   # Run only standalone tests that don't require Django
   python manage.py durc_test --standalone-only

   # Run only tests that require Django
   python manage.py durc_test --django-only
   
   # Verbose output
   python manage.py durc_test -v 2
   ```

### Standalone CLI Commands

DURC also provides standalone CLI commands that don't require Django:

1. **Generate foreign key statements from existing relational model:**

   ```bash
   # Use default paths
   durc-mine-fkeys
   
   # Custom input/output files
   durc-mine-fkeys --input_json_file custom/model.json --output_sql_file custom/fkeys.sql
   ```

### Development Workflow

For developers working on DURC:

1. **Set up development environment** (see installation steps above)

2. **Run tests before making changes:**
   ```bash
   python manage.py durc_test
   # Or use pytest directly
   pytest tests/
   ```

3. **Make your changes**

4. **Run tests again to ensure nothing broke:**
   ```bash
   python manage.py durc_test -v 2
   ```

5. **Test with a real database:**
   ```bash
   # Mine a database schema
   python manage.py durc_mine --include your_db.your_schema
   
   # Generate foreign keys
   python manage.py durc_mine_fkeys --include your_db.your_schema
   
   # Create diagrams
   python manage.py durc_diagram --sql_files your_schema.sql --output_md_file test_diagram.md
   ```

6. **Build and test the package:**
   ```bash
   ./scripts/build_and_install.sh
   ```

### File Structure

After running DURC commands, you'll typically see these files created:

```
durc_config/
├── DURC_relational_model.json    # Generated by durc_mine
├── foreign_keys.sql              # Generated by durc_mine_fkeys
└── other_output_files...
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'durc_is_crud'`

**Solution:**
```bash
# Make sure you're in the right directory and virtual environment is activated
source venv/bin/activate  # or source source_me_to_get_venv.sh

# Reinstall in development mode
pip install -e .
```

#### 2. Django Commands Not Found

**Problem:** `Unknown command: 'durc_mine'`

**Solution:**
```bash
# Ensure durc_is_crud is in your INSTALLED_APPS
# Check your Django settings.py file

# Verify Django can find the commands
python manage.py help | grep durc
```

#### 3. Database Connection Issues

**Problem:** Database connection errors when running `durc_mine`

**Solution:**
```bash
# Ensure your Django database settings are correct
# Test Django database connection first
python manage.py dbshell

# Check your database credentials and permissions
```

#### 4. Permission Issues with Scripts

**Problem:** `Permission denied` when running shell scripts

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/build_and_install.sh
chmod +x source_me_to_get_venv.sh

# Then run them
./scripts/build_and_install.sh
```

#### 5. Virtual Environment Issues

**Problem:** Commands not working or wrong Python version

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python3.9 -m venv venv  # Use Python 3.9+ as required
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -e .[dev]
```

#### 6. Test Failures

**Problem:** Tests failing during development

**Solution:**
```bash
# Run tests with verbose output to see details
python manage.py durc_test -v 2

# Run specific test categories
python manage.py durc_test --standalone-only
python manage.py durc_test --django-only

# Use pytest directly for more control
pytest tests/ -v
pytest tests/test_utils/ -v
```

#### 7. CLI Command Not Found

**Problem:** `durc-mine-fkeys: command not found`

**Solution:**
```bash
# Ensure package is installed correctly
pip install -e .

# Check if command is in PATH
which durc-mine-fkeys

# If not found, try running directly
python -m durc_is_crud.cli.durc_mine_fkeys --help
```

### Getting Help

If you encounter issues not covered here:

1. Check the [tests/](tests/) directory for examples of how commands should work
2. Look at the [AI_Instructions/](AI_Instructions/) directory for detailed documentation
3. Run commands with verbose output (`-v 2`) to get more debugging information
4. Check that all prerequisites are installed and up to date

For more detailed usage instructions, see the [Usage Guide](docs/usage.md).

## Documentation

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Testing Guide](tests/README.md)

## Requirements

- Python 3.9+ (for development)
- Python 3.6+ (for end users, but 3.9+ recommended)
- Django 3.0+
- PostgreSQL (for database operations)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
