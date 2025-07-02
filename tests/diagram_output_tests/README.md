# DURC Diagram Generator Test Outputs

This directory contains test outputs and example files for the DURC Diagram Generator.

## Files

### Test SQL Files
- `test_with_sections.sql` - Example SQL file with diagram section comments demonstrating the sectioning feature

### Generated Diagrams
- `test_durc_database_diagram.md` - Diagram generated from the actual DURC test SQL files (DURC_aaa.postgres.sql and DURC_bbb.postgres.sql)
- `test_sections_diagram.md` - Diagram generated from test_with_sections.sql showing colored sections

## Running Tests

To run the complete test suite and regenerate these outputs:

```bash
cd tests
python3 test_durc_diagram.py
```

This will:
1. Run all unit tests for SQL parsing and Mermaid generation
2. Run integration tests
3. Generate fresh diagram outputs in this directory

## Test Coverage

The test suite covers:
- SQL parsing of CREATE TABLE statements
- Foreign key relationship detection using DURC naming conventions
- Diagram section comment parsing
- Mermaid diagram generation with and without sections
- End-to-end workflow from SQL files to markdown output
- Integration with actual DURC test SQL files

## Example Usage

The generated diagrams demonstrate:
- **Basic functionality**: Parsing tables and relationships from real SQL files
- **Section grouping**: Organizing tables into colored sections with proper styling
- **DURC conventions**: Automatic foreign key detection using `_id` suffix naming
- **Visual styling**: Light pastel colors for tables, darker colors for section backgrounds
