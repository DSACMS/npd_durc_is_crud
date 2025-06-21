# Usage Guide

DURC Is CRUD provides Django management commands to extract database schema information and generate code artifacts based on the extracted model.

## Extracting Database Schema

The `durc_mine` command extracts database schema information and generates a JSON file containing the relational model.

### Basic Usage

```bash
python manage.py durc_mine --include db.schema.table
```

### Parameters

- `--include`: Specify databases, schemas, or tables to include in the format: `db.schema.table`, `db.schema`, or `db`. You can specify multiple patterns.
- `--output_json_file`: Specify a custom output path for the JSON file (default: `durc_config/DURC_relational_model.json`).

### Examples

Extract all tables from a specific schema:

```bash
python manage.py durc_mine --include mydb.public
```

Extract specific tables:

```bash
python manage.py durc_mine --include mydb.public.users mydb.public.posts
```

Extract from multiple databases:

```bash
python manage.py durc_mine --include mydb1.public mydb2.public
```

Specify a custom output file:

```bash
python manage.py durc_mine --include mydb.public --output_json_file custom_path/model.json
```

## Compiling Code Artifacts

The `durc_compile` command compiles the extracted relational model into code artifacts.

### Basic Usage

```bash
python manage.py durc_compile
```

### Parameters

- `--input_json_file`: Specify the input DURC relational model JSON file (default: `durc_config/DURC_relational_model.json`).
- `--output_dir`: Specify the output directory for generated code (default: `durc_generated`).
- `--template_dir`: Specify a custom template directory (default: built-in templates).
- `--config_file`: Specify a custom configuration file for code generation.

### Examples

Compile with default settings:

```bash
python manage.py durc_compile
```

Specify custom input and output paths:

```bash
python manage.py durc_compile --input_json_file custom_path/model.json --output_dir custom_output
```

## Understanding the Relational Model

The relational model JSON file contains information about the database schema, including:

- Tables and their columns
- Primary keys and foreign keys
- Relationships between tables (has_many, belongs_to)

Example structure:

```json
{
  "database_name": {
    "table_name": {
      "table_name": "table_name",
      "db": "database_name",
      "column_data": [
        {
          "column_name": "id",
          "data_type": "int",
          "is_primary_key": true,
          "is_foreign_key": false,
          "is_linked_key": false,
          "is_nullable": false,
          "is_auto_increment": true
        },
        // More columns...
      ],
      "has_many": {
        "related_table": {
          "type": "related_table",
          "from_table": "related_table",
          "from_db": "database_name",
          "from_column": "table_name_id"
        }
      },
      "belongs_to": {
        "parent_table": {
          "type": "parent_table",
          "to_table": "parent_table",
          "to_db": "database_name",
          "local_key": "parent_table_id"
        }
      },
      "create_table_sql": "CREATE TABLE table_name (...);"
    }
  }
}
```

## Customizing Code Generation

Currently, the code generation functionality is a placeholder. Future versions will support customizable templates and configuration options for generating various code artifacts such as:

- Django models
- API views and serializers
- Admin interfaces
- Forms
- And more

Stay tuned for updates!
