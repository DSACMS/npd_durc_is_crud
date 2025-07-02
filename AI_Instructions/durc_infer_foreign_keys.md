# DURC Infer Foreign Keys Command Specification

## Overview

Create a new standalone CLI command `durc-mine-fkeys` that generates PostgreSQL foreign key statements from the relational model JSON output produced by `durc_mine`. This command processes inferred relationships and existing foreign key constraints to produce executable SQL statements.

**IMPORTANT**: This should be developed as a totally independent Python CLI command that does NOT require Django or `manage.py` to run. It should be installed as a separate command-line tool that becomes available system-wide after package installation.

## Command Details

### Command Name

`durc-mine-fkeys`

### Purpose

Generate PostgreSQL `ALTER TABLE` statements with `FOREIGN KEY` constraints from the relational model JSON file created by `durc_mine`. This allows users to apply the inferred database relationships as actual foreign key constraints.

### File Location

`durc_is_crud/cli/durc_mine_fkeys.py`

### Installation Setup

The command should be configured as a console script entry point in `setup.py` or `pyproject.toml`:

```python
entry_points={
    'console_scripts': [
        'durc-mine-fkeys=durc_is_crud.cli.durc_mine_fkeys:main',
    ],
}
```

## Command Arguments

The command should be executed as a standalone CLI tool after installation:

```bash
durc-mine-fkeys --input_json_file path/to/input.json --output_sql_file path/to/output.sql
```

### Required Arguments

- `--input_json_file`: Input DURC relational model JSON file
  - Default: `durc_config/DURC_relational_model.json`
- `--output_sql_file`: Output SQL file for foreign key statements
  - Default: `durc_config/foreign_keys.sql`

## Implementation Requirements

### Core Logic Flow

1. **Load JSON file** containing the relational model
2. **Extract relationships** from JSON structure
3. **Generate PostgreSQL ALTER TABLE statements**
4. **Write to single SQL file** with semicolon-separated statements that create the FOREIGN keys in the PostgreSQL syntax

### Relationship Processing

Process relationships from the JSON structure:

#### 1. `belongs_to` Relationships

These represent foreign keys in the current table:

- Extract: `local_key`, `to_table`, `to_db`, `to_schema` (if cross-schema)
- Generate: `ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY ...`

#### 2. Existing Foreign Keys

Include any existing foreign key constraints found in:

- Column metadata where `is_foreign_key: true`

#### 3. Cross-Schema Relationships

Handle cross-schema linking using proper schema qualification:

- Use `to_schema` field when different from current schema
- Format: `schema_name.table_name`

### SQL Generation Strategy

For each relationship, generate PostgreSQL-compatible statements:

```sql
ALTER TABLE schema_name.table_name 
ADD CONSTRAINT fk_table_column 
FOREIGN KEY (local_column) 
REFERENCES target_schema.target_table(target_column);
```

### Standard Naming Convention

Use consistent foreign key constraint naming:

- Pattern: `fk_{source_table}_{column_name}`
- Example: `fk_post_author_id`, `fk_comment_post_id`

When there are more than one foreign key linking two table using the same foreign column, they should get numbers _01, _02, etc.

### Output Format

Generate a single SQL text file with:

```sql
-- Generated PostgreSQL Foreign Key Statements
-- Source: DURC relational model
-- Generated on: [timestamp]
-- Command: durc-mine-fkeys --input_json_file [file] --output_sql_file [file]

-- Database: blog_db
ALTER TABLE blog_db.post ADD CONSTRAINT fk_post_author_id FOREIGN KEY (author_id) REFERENCES blog_db.user(id);
ALTER TABLE blog_db.comment ADD CONSTRAINT fk_comment_post_id FOREIGN KEY (post_id) REFERENCES blog_db.post(id);
ALTER TABLE blog_db.comment ADD CONSTRAINT fk_comment_user_id FOREIGN KEY (user_id) REFERENCES blog_db.user(id);
ALTER TABLE blog_db.comment ADD CONSTRAINT fk_comment_parent_id FOREIGN KEY (parent_id) REFERENCES blog_db.comment(id);
ALTER TABLE blog_db.post_tag ADD CONSTRAINT fk_post_tag_post_id FOREIGN KEY (post_id) REFERENCES blog_db.post(id);
ALTER TABLE blog_db.post_tag ADD CONSTRAINT fk_post_tag_tag_id FOREIGN KEY (tag_id) REFERENCES blog_db.tag(id);
ALTER TABLE blog_db.user ADD CONSTRAINT fk_user_mentor_id FOREIGN KEY (mentor_id) REFERENCES blog_db.user(id);
```

## Technical Implementation Details

### Shared Data Loader Class

**CRITICAL REQUIREMENT**: Create a shared data loader class that can be used by both Django and non-Django components:

#### File Location

`durc_is_crud/shared/durc_data_loader.py`

#### Class Specification

```python
class DurcDataLoader:
    """
    Shared data loader for DURC JSON files.
    
    This class provides a thin layer on top of JSON file loading that can be used
    by both Django management commands (like durc_compile) and standalone CLI tools
    (like durc-mine-fkeys).
    
    For now, this should simply return a dictionary in the same structure as loading
    the JSON directly would. In the future, it may have extra functionality that is
    useful to both Django and non-Django scripts.
    """
    
    def load_relational_model(self, json_file_path: str) -> dict:
        """Load and return the DURC relational model from JSON file."""
        # For now, just load and return the JSON as a dictionary
        # Future enhancements may include validation, transformation, etc.
        pass
```

#### Usage Requirements

- The Django management command `durc_compile` should use this same data loader class
- The standalone CLI tool `durc-mine-fkeys` should use this same data loader class
- This ensures consistent JSON loading behavior across all DURC tools
- Future enhancements to JSON loading will benefit both Django and non-Django components

### Dependencies

- Standard Python libraries only (json, argparse, sys, os)
- No Django dependencies required for the CLI tool
- Should be completely standalone and installable via pip
- Shared data loader should work in both Django and non-Django contexts

### Error Handling

- Handle missing JSON files gracefully
- Use standard Python exception handling
- Provide clear error messages to stdout/stderr

### Features

- **Deduplication**: Avoid generating duplicate foreign key statements
- **Cross-schema support**: Handle relationships across different schemas

### File Structure

Implement as a standalone CLI tool:

- Create `durc_is_crud/cli/` directory for CLI tools
- Create `durc_is_crud/shared/` directory for shared utilities
- Use `argparse` for command-line argument parsing
- Implement a `main()` function as the entry point
- Use standard `print()` for output messages
- Handle exceptions with try/catch blocks
- Use `sys.exit()` for error conditions
- No Django framework dependencies for the CLI tool itself

### Installation Integration

- Add the CLI command to the package's console scripts
- Ensure it's available system-wide after `pip install durc-is-crud`
- The command should work independently of any Django project

## Example Usage

```bash
# After installation with pip install durc-is-crud
# Generate foreign keys from JSON 
durc-mine-fkeys --input_json_file custom/model.json \
  --output_sql_file custom/fkeys.sql

# Use default file locations
durc-mine-fkeys

# Specify only input file (uses default output location)
durc-mine-fkeys --input_json_file my_model.json
```

## Expected Output

The command should generate a clean, executable SQL file that can be run against a PostgreSQL database to establish the foreign key relationships identified by `durc_mine`. The SQL should be properly formatted, commented, and use standard PostgreSQL syntax.
