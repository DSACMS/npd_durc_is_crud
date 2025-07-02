import os
import json
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from .durc_utils.include_pattern_parser import DURC_IncludePatternParser

class Command(BaseCommand):
    help = 'Generate PostgreSQL foreign key statements from DURC relational model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--include',
            nargs='+',
            type=str,
            help='Specify databases, schemas, or tables to include in the format: db.schema.table, db.schema, or db'
        )
        parser.add_argument(
            '--input_json_file',
            type=str,
            help='Input DURC relational model JSON file (default: durc_config/DURC_relational_model.json)'
        )
        parser.add_argument(
            '--output_sql_file',
            type=str,
            help='Output SQL file for foreign key statements (default: durc_config/foreign_keys.sql)'
        )

    def handle(self, *args, **options):
        include_patterns = options.get('include', [])
        
        if not include_patterns:
            raise CommandError("You must specify at least one database, schema, or table to include using --include")
        
        # Parse the include patterns
        db_schema_table_patterns = DURC_IncludePatternParser.parse_include_patterns(include_patterns)
        
        # Get the input JSON file path
        input_json_file = options.get('input_json_file')
        if not input_json_file:
            input_json_file = os.path.join('durc_config', 'DURC_relational_model.json')
        
        # Check if the input file exists
        if not os.path.exists(input_json_file):
            raise CommandError(f"Input file {input_json_file} does not exist. Run durc_mine first.")
        
        # Get the output SQL file path
        output_sql_file = options.get('output_sql_file')
        if not output_sql_file:
            # Use the default path
            os.makedirs('durc_config', exist_ok=True)
            output_sql_file = os.path.join('durc_config', 'foreign_keys.sql')
        else:
            # Ensure the directory for the custom output path exists
            output_dir = os.path.dirname(output_sql_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
        
        # Load the relational model
        try:
            with open(input_json_file, 'r') as f:
                relational_model = json.load(f)
        except json.JSONDecodeError:
            raise CommandError(f"Failed to parse {input_json_file} as JSON")
        except Exception as e:
            raise CommandError(f"Error reading {input_json_file}: {e}")
        
        # Generate foreign key statements
        foreign_key_statements = self._generate_foreign_key_statements(
            relational_model, 
            db_schema_table_patterns,
            include_patterns
        )
        
        # Write the SQL file
        self._write_sql_file(output_sql_file, foreign_key_statements, include_patterns)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully generated foreign key statements at {output_sql_file}"))
        self.stdout.write(f"Generated {len(foreign_key_statements)} foreign key statements")

    def _generate_foreign_key_statements(self, relational_model, db_schema_table_patterns, include_patterns):
        """
        Generate foreign key statements from the relational model.
        
        Args:
            relational_model (dict): The loaded JSON relational model
            db_schema_table_patterns (list): Parsed include patterns
            include_patterns (list): Original include patterns for reference
            
        Returns:
            list: List of SQL foreign key statements
        """
        foreign_key_statements = []
        processed_constraints = set()  # To avoid duplicates
        
        # Process each database in the model
        for db_name, tables in relational_model.items():
            if not isinstance(tables, dict):
                continue
                
            # Process each table in the database
            for table_name, table_info in tables.items():
                if not isinstance(table_info, dict):
                    continue
                
                # Check if this table matches our include patterns
                if not self._table_matches_patterns(db_name, table_name, db_schema_table_patterns):
                    continue
                
                self.stdout.write(f"Processing table: {db_name}.{table_name}")
                
                # Process belongs_to relationships (foreign keys in this table)
                belongs_to = table_info.get('belongs_to', {})
                for relationship_name, relationship_info in belongs_to.items():
                    try:
                        fk_statement = self._create_foreign_key_statement(
                            db_name, table_name, relationship_info, processed_constraints
                        )
                        if fk_statement:
                            foreign_key_statements.append(fk_statement)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping relationship {relationship_name} in {db_name}.{table_name}: {e}"
                        ))
        
        return foreign_key_statements

    def _table_matches_patterns(self, db_name, table_name, db_schema_table_patterns):
        """
        Check if a table matches the include patterns.
        
        Args:
            db_name (str): Database name
            table_name (str): Table name
            db_schema_table_patterns (list): Parsed include patterns
            
        Returns:
            bool: True if table matches patterns
        """
        for pattern in db_schema_table_patterns:
            pattern_db = pattern.get('db')
            pattern_schema = pattern.get('schema')
            pattern_table = pattern.get('table')
            
            # Check database match
            if pattern_db and pattern_db != db_name:
                continue
            
            # For now, we'll treat schema and db as the same since the JSON structure
            # uses db as the top level. In a real implementation, you might need to
            # handle schema differently based on your database structure.
            
            # Check table match
            if pattern_table and pattern_table != table_name:
                continue
            
            # If we get here, the table matches this pattern
            return True
        
        return False

    def _create_foreign_key_statement(self, db_name, table_name, relationship_info, processed_constraints):
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
        
        # Create constraint name using standard convention
        constraint_name = f"fk_{table_name}_{local_key}"
        
        # Create unique identifier for this constraint to avoid duplicates
        constraint_id = f"{db_name}.{table_name}.{constraint_name}"
        if constraint_id in processed_constraints:
            return None
        processed_constraints.add(constraint_id)
        
        # Build source table reference
        source_table_ref = f"{db_name}.{table_name}"
        
        # Build target table reference
        if to_schema and to_schema != db_name:
            target_table_ref = f"{to_schema}.{to_table}"
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

    def _write_sql_file(self, output_sql_file, foreign_key_statements, include_patterns):
        """
        Write the foreign key statements to a SQL file.
        
        Args:
            output_sql_file (str): Output file path
            foreign_key_statements (list): List of SQL statements
            include_patterns (list): Include patterns for documentation
        """
        with open(output_sql_file, 'w') as f:
            # Write header
            f.write("-- Generated PostgreSQL Foreign Key Statements\n")
            f.write("-- Source: DURC relational model\n")
            f.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Command: python manage.py durc_mine_fkeys --include {' '.join(include_patterns)}\n")
            f.write("\n")
            
            if not foreign_key_statements:
                f.write("-- No foreign key relationships found for the specified patterns\n")
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
