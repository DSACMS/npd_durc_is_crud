# DURC Tests

This directory contains tests for the DURC (Database to CRUD) package. The tests are organized into two categories:

## Tests that can run without Django

These tests can be run directly with pytest or unittest without requiring a Django context:

- `test_utils/test_data_type_mapper.py`: Tests for the data type mapping utility.

To run these tests:

```bash
# pytest is included in the basic installation of durc-is-crud
cd /path/to/durc_is_crud
python -m pytest tests/test_utils/test_data_type_mapper.py -v
```

## Tests that require Django

These tests require a Django context to run, as they depend on Django components:

- `test_utils/test_include_pattern_parser.py`: Tests for the include pattern parser (imports CommandError from django.core.management.base).
- `test_utils/test_relational_model_extractor.py`: Tests for the relational model extractor (imports TestCase from django.test, connection from django.db, and CommandError from django.core.management.base).
- `test_commands/test_durc_mine.py`: Tests for the durc_mine management command (imports call_command from django.core.management and CommandError from django.core.management.base).
- `test_commands/test_durc_compile.py`: Tests for the durc_compile management command (imports call_command from django.core.management and CommandError from django.core.management.base).

These tests should be run after the package has been installed in a Django project.

## Running Tests with the durc_test Command

The DURC package provides a custom management command to run all tests, both standalone and Django-dependent:

```bash
# Run all tests (both standalone and Django-dependent)
python manage.py durc_test

# Run only standalone tests that don't require Django
python manage.py durc_test --standalone-only

# Run only tests that require Django
python manage.py durc_test --django-only

# Run with increased verbosity
python manage.py durc_test -v 2
```

## Alternative: Running Tests with Django's Test Runner

You can also use Django's built-in test runner:

```bash
# Run all DURC tests
python manage.py test durc_is_crud.tests

# Run specific test modules
python manage.py test durc_is_crud.tests.test_utils.test_include_pattern_parser
python manage.py test durc_is_crud.tests.test_utils.test_relational_model_extractor
python manage.py test durc_is_crud.tests.test_commands.test_durc_mine
python manage.py test durc_is_crud.tests.test_commands.test_durc_compile
```
