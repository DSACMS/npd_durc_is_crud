#!/usr/bin/env python3
"""
DURC Mine Foreign Keys CLI Tool

A standalone command-line tool that generates PostgreSQL foreign key statements 
from the relational model JSON output produced by durc_mine.
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Set, Any, Optional

# Import the shared data loader
try:
    from ..shared.durc_data_loader import DurcDataLoader
except ImportError:
    # Handle case when running as standalone script
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from shared.durc_data_loader import DurcDataLoader


class ForeignKeyGenerator:
    """Generates PostgreSQL foreign key statements from DURC relational model."""
    
    @staticmethod
    def generate_foreign_keys(input_json_file: str, output_sql_file: str) -> None:
        """
        Main method to generate foreign key statements.
        
        Args:
            input_json_file (str): Path to input JSON file
            output_sql_file (str): Path to output SQL file
        """
        print(f"Loading relational model from: {input_json_file}")
        
        # Load the relational model using shared data loader
        data_loader = DurcDataLoader()
        try:
            relational_model = data_loader.load_relational_model(input_json_file)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Generate foreign key statements
        foreign_key_statements = ForeignKeyGenerator._generate_foreign_key_statements(relational_model)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_sql_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write SQL file
        ForeignKeyGenerator._write_sql_file(output_sql_file, foreign_key_statements, input_json_file)
        
        print(f"Successfully generated {len(foreign_key_statements)} foreign key statements")
        print(f"Output written to: {output_sql_file}")
    
    @staticmethod
    def _generate_foreign_key_statements(relational_model: Dict[str, Any]) -> List[str]:
        """
        Generate foreign key statements from the relational model.
        
        Args:
            relational_model (dict): The loaded JSON relational model
            
        Returns:
            list: List of SQL foreign key statements
        """
        foreign_key_statements = []
        processed_constraints: Set[str] = set()
        
        # Process each database in the model
        for db_name, schemas_or_tables in relational_model.items():
            if not isinstance(schemas_or_tables, dict):
                continue
                
            print(f"Processing database: {db_name}")
            
            # Check if this is a schema-based structure or direct table structure
            for schema_or_table_name, schema_or_table_info in schemas_or_tables.items():
                if not isinstance(schema_or_table_info, dict):
                    continue
                
                # Check if this looks like a schema (contains tables) or a direct table
                if 'table_name' in schema_or_table_info:
                    # This is a direct table
                    table_name = schema_or_table_name
                    table_info = schema_or_table_info
                    print(f"  Processing table: {table_name}")
                    ForeignKeyGenerator._process_table(db_name, table_name, table_info, foreign_key_statements, processed_constraints, None)
                else:
                    # This is a schema containing tables
                    schema_name = schema_or_table_name
                    print(f"  Processing schema: {schema_name}")
                    
                    for table_name, table_info in schema_or_table_info.items():
                        if not isinstance(table_info, dict):
                            continue
                        
                        print(f"    Processing table: {table_name}")
                        ForeignKeyGenerator._process_table(db_name, table_name, table_info, foreign_key_statements, processed_constraints, schema_name)
        
        return foreign_key_statements
    
    @staticmethod
    def _process_table(db_name: str, table_name: str, table_info: Dict[str, Any], 
                      foreign_key_statements: List[str], processed_constraints: Set[str],
                      schema_name: Optional[str] = None) -> None:
        """
        Process a single table for foreign key relationships.
        
        Args:
            db_name (str): Database name
            table_name (str): Table name
            table_info (dict): Table information from JSON
            foreign_key_statements (list): List to append generated statements to
            processed_constraints (set): Set of processed constraints to avoid duplicates
            schema_name (str): Schema name (optional)
        """
        # Process belongs_to relationships (foreign keys in this table)
        belongs_to = table_info.get('belongs_to', {})
        print(f"    Found {len(belongs_to)} belongs_to relationships")
        for relationship_name, relationship_info in belongs_to.items():
            print(f"    Processing relationship: {relationship_name} -> {relationship_info}")
            try:
                fk_statement = ForeignKeyGenerator._create_foreign_key_statement(
                    db_name, table_name, relationship_info, processed_constraints, schema_name
                )
                if fk_statement:
                    foreign_key_statements.append(fk_statement)
                    print(f"    Generated FK: {relationship_name}")
            except Exception as e:
                print(f"    Warning: Skipping relationship {relationship_name}: {e}")
        
        # Also process existing foreign keys from column metadata
        column_data = table_info.get('column_data', [])
        print(f"    Found {len(column_data)} columns")
        for column in column_data:
            # Check for both is_foreign_key and is_linked_key
            is_fk = column.get('is_foreign_key', False)
            is_linked = column.get('is_linked_key', False)
            has_foreign_table = column.get('foreign_table') is not None
            print(f"    Column {column.get('column_name')}: is_foreign_key={is_fk}, is_linked_key={is_linked}, foreign_table={column.get('foreign_table')}")
            
            if (is_fk or is_linked) and has_foreign_table:
                try:
                    fk_statement = ForeignKeyGenerator._create_foreign_key_from_column(
                        db_name, table_name, column, processed_constraints, schema_name
                    )
                    if fk_statement:
                        foreign_key_statements.append(fk_statement)
                        print(f"    Generated FK from column: {column['column_name']}")
                except Exception as e:
                    print(f"    Warning: Skipping column FK {column.get('column_name')}: {e}")
    
    @staticmethod
    def _create_foreign_key_statement(db_name: str, table_name: str, 
                                    relationship_info: Dict[str, Any], 
                                    processed_constraints: Set[str],
                                    schema_name: Optional[str] = None) -> Optional[str]:
        """
        Create a foreign key statement from relationship information.
        
        Args:
            db_name (str): Source database name
            table_name (str): Source table name
            relationship_info (dict): Relationship information from JSON
            processed_constraints (set): Set of already processed constraints to avoid duplicates
            
        Returns:
            str: SQL ALTER TABLE statement or None if invalid/duplicate
        """
        # Extract relationship details
        local_key = relationship_info.get('local_key')
        to_table = relationship_info.get('to_table')
        to_db = relationship_info.get('to_db', db_name)
        to_schema = relationship_info.get('to_schema')
        
        if not local_key or not to_table:
            raise ValueError(f"Missing local_key or to_table in relationship")
        
        # Determine target column (assume 'id' if not specified)
        target_column = 'id'  # Most foreign keys reference the primary key 'id'
        
        # Create unique identifier for this foreign key relationship to avoid duplicates
        # Use source table, column, and target table to identify unique relationships
        if schema_name:
            source_table_ref = f"{schema_name}.{table_name}"
        else:
            source_table_ref = f"{db_name}.{table_name}"
        
        # Build target table reference for uniqueness check
        if to_schema:
            target_table_ref = f"{to_schema}.{to_table}"
        elif schema_name:
            target_table_ref = f"{schema_name}.{to_table}"
        else:
            target_table_ref = f"{to_db}.{to_table}"
        
        # Create unique relationship identifier
        relationship_id = f"{source_table_ref}.{local_key} -> {target_table_ref}.{target_column}"
        
        # Check if this exact relationship already exists
        if relationship_id in processed_constraints:
            return None
        processed_constraints.add(relationship_id)
        
        # Create constraint name using standard convention
        constraint_name = f"fk_{table_name}_{local_key}"
        
        # Build source table reference - use schema_name if available, otherwise db_name
        if schema_name:
            source_table_ref = f"{schema_name}.{table_name}"
        else:
            source_table_ref = f"{db_name}.{table_name}"
        
        # Build target table reference - use to_schema if available, otherwise use schema_name or db_name
        if to_schema:
            target_table_ref = f"{to_schema}.{to_table}"
        elif schema_name:
            # If no to_schema specified but we have a schema_name, assume same schema
            target_table_ref = f"{schema_name}.{to_table}"
        else:
            target_table_ref = f"{to_db}.{to_table}"
        
        # Generate the ALTER TABLE statement
        sql_statement = (
            f"ALTER TABLE {source_table_ref} "
            f"ADD CONSTRAINT {constraint_name} "
            f"FOREIGN KEY ({local_key}) "
            f"REFERENCES {target_table_ref}({target_column});"
        )
        
        return sql_statement
    
    @staticmethod
    def _create_foreign_key_from_column(db_name: str, table_name: str, 
                                      column: Dict[str, Any], 
                                      processed_constraints: Set[str],
                                      schema_name: Optional[str] = None) -> Optional[str]:
        """
        Create a foreign key statement from column metadata.
        
        Args:
            db_name (str): Source database name
            table_name (str): Source table name
            column (dict): Column information from JSON
            processed_constraints (set): Set of already processed constraints to avoid duplicates
            
        Returns:
            str: SQL ALTER TABLE statement or None if invalid/duplicate
        """
        column_name = column.get('column_name')
        foreign_table = column.get('foreign_table')
        foreign_db = column.get('foreign_db', db_name)
        
        if not column_name or not foreign_table:
            raise ValueError(f"Missing column_name or foreign_table in column")
        
        # Create a relationship info dict to reuse existing logic
        relationship_info = {
            'local_key': column_name,
            'to_table': foreign_table,
            'to_db': foreign_db
        }
        
        return ForeignKeyGenerator._create_foreign_key_statement(
            db_name, table_name, relationship_info, processed_constraints, schema_name
        )
    
    @staticmethod
    def _write_sql_file(output_sql_file: str, foreign_key_statements: List[str], 
                       input_json_file: str) -> None:
        """
        Write the foreign key statements to a SQL file.
        
        Args:
            output_sql_file (str): Output file path
            foreign_key_statements (list): List of SQL statements
            input_json_file (str): Input file path for documentation
        """
        with open(output_sql_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("-- Generated PostgreSQL Foreign Key Statements\n")
            f.write("-- Source: DURC relational model\n")
            f.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Command: durc-mine-fkeys --input_json_file {input_json_file} --output_sql_file {output_sql_file}\n")
            f.write("\n")
            
            if not foreign_key_statements:
                f.write("-- No foreign key relationships found\n")
                return
            
            # Group statements by database for better organization
            statements_by_db = {}
            for statement in foreign_key_statements:
                # Extract database name from the ALTER TABLE statement
                db_name = statement.split('.')[0].replace('ALTER TABLE ', '')
                if db_name not in statements_by_db:
                    statements_by_db[db_name] = []
                statements_by_db[db_name].append(statement)
            
            # Write statements grouped by database
            for db_name, statements in statements_by_db.items():
                f.write(f"-- Database: {db_name}\n")
                for statement in statements:
                    f.write(f"{statement}\n")
                f.write("\n")


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description='Generate PostgreSQL foreign key statements from DURC relational model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  durc-mine-fkeys
  durc-mine-fkeys --input_json_file custom/model.json
  durc-mine-fkeys --input_json_file model.json --output_sql_file fkeys.sql
        """
    )
    
    parser.add_argument(
        '--input_json_file',
        type=str,
        default='durc_config/DURC_relational_model.json',
        help='Input DURC relational model JSON file (default: durc_config/DURC_relational_model.json)'
    )
    
    parser.add_argument(
        '--output_sql_file',
        type=str,
        default='durc_config/foreign_keys.sql',
        help='Output SQL file for foreign key statements (default: durc_config/foreign_keys.sql)'
    )
    
    args = parser.parse_args()
    
    # Create and run the foreign key generator
    ForeignKeyGenerator.generate_foreign_keys(args.input_json_file, args.output_sql_file)


if __name__ == '__main__':
    main()
