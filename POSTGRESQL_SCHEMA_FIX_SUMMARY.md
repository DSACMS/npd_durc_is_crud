# PostgreSQL Schema Layer Fix for durc_mine Command

## Problem
The `durc_mine` management command was not creating a schema layer inside the mined JSON schema when working with PostgreSQL databases. PostgreSQL has three layers (database, schema, table) while MySQL only has two (database, table). The command was treating PostgreSQL databases like MySQL, resulting in missing schema information.

## Solution
Modified the `DURC_RelationalModelExtractor` class in `durc_is_crud/management/commands/durc_utils/relational_model_extractor.py` to:

### 1. Database Type Detection
Added logic to detect PostgreSQL databases by checking the database engine:
```python
is_postgresql = 'postgresql' in conn.settings_dict['ENGINE'].lower() or 'psycopg' in conn.settings_dict['ENGINE'].lower()
```

### 2. Schema Layer Structure
For PostgreSQL databases, the JSON structure now follows the proper hierarchy:
- **MySQL**: `database -> table`
- **PostgreSQL**: `database -> schema -> table`

### 3. Schema Information in Table Metadata
Added schema field to table information for PostgreSQL tables:
```python
if is_postgresql and schema_name:
    table_info['schema'] = schema_name
```

### 4. Cross-Schema Relationship Handling
Enhanced relationship detection to properly handle cross-schema foreign key relationships.

## Changes Made

### Files Modified:
1. `durc_is_crud/management/commands/durc_utils/relational_model_extractor.py`
   - Added PostgreSQL detection logic
   - Modified JSON structure creation for PostgreSQL
   - Enhanced relationship detection for cross-schema references
   - Added schema information to table metadata

2. `tests/test_commands/test_durc_mine.py`
   - Added test case for PostgreSQL schema structure
   - Fixed test cleanup to handle directory removal properly

### Files Added:
1. `example_postgresql_schema_output.py` - Demonstration script showing the difference between MySQL and PostgreSQL output structures

## Output Structure Examples

### Before (MySQL-style, incorrect for PostgreSQL):
```json
{
  "blog_db": {
    "users": {
      "table_name": "users",
      "db": "blog_db",
      "column_data": [...]
    }
  }
}
```

### After (PostgreSQL-style, correct):
```json
{
  "blog_db": {
    "public": {
      "users": {
        "table_name": "users",
        "db": "blog_db",
        "schema": "public",
        "column_data": [...]
      }
    },
    "auth": {
      "permissions": {
        "table_name": "permissions",
        "db": "blog_db",
        "schema": "auth",
        "column_data": [...]
      }
    }
  }
}
```

## Usage Examples

### Mine all tables from a specific PostgreSQL schema:
```bash
python manage.py durc_mine --include mydb.public
```

### Mine a specific table from a PostgreSQL schema:
```bash
python manage.py durc_mine --include mydb.public.users
```

### Mine multiple schemas:
```bash
python manage.py durc_mine --include mydb.public mydb.auth
```

## Testing
- All existing tests continue to pass
- New test added specifically for PostgreSQL schema structure validation
- Test verifies that the output includes the proper three-layer structure for PostgreSQL

## Backward Compatibility
- MySQL databases continue to work with the existing two-layer structure
- No breaking changes to existing functionality
- The change is automatically detected based on the database engine type

## Benefits
1. **Accurate Schema Representation**: PostgreSQL databases now properly represent their three-layer structure
2. **Cross-Schema Relationships**: Foreign key relationships across schemas are properly detected and represented
3. **Better Organization**: Multiple schemas within a database are clearly separated in the output
4. **Improved Metadata**: Each table now includes schema information when applicable
