from django.db import connections, connection
from django.db.utils import OperationalError
from django.core.management.base import CommandError
from .data_type_mapper import DURC_DataTypeMapper

class DURC_RelationalModelExtractor:
    """
    Utility class for extracting relational model information from database schemas.
    """
    
    @staticmethod
    def extract_relational_model(db_schema_table_patterns, stdout_writer, style):
        """
        Extract the relational model based on the specified patterns.
        
        Args:
            db_schema_table_patterns (list): List of dictionaries with db, schema, and table patterns
            stdout_writer: Django stdout writer for output messages
            style: Django style for formatting output messages
            
        Returns:
            dict: A dictionary structured according to the DURC_simplified schema
        """
        relational_model = {}
        
        # Use the default connection if no specific database is provided
        conn = connection
        
        for pattern in db_schema_table_patterns:
            db_name = pattern['db']
            schema_name = pattern['schema']
            table_name = pattern['table']
            
            # Try to get the connection for the specified database
            try:
                if db_name in connections:
                    conn = connections[db_name]
                else:
                    stdout_writer(style.WARNING(f"Database '{db_name}' not found in settings, using default connection"))
            except Exception as e:
                stdout_writer(style.ERROR(f"Error connecting to database '{db_name}': {e}"))
                continue
            
            # Initialize the database in the relational model if not already present
            if db_name not in relational_model:
                relational_model[db_name] = {}
            
            # Get the introspection API for the connection
            introspection = conn.introspection
            
            # Get all table names in the database
            try:
                with conn.cursor() as cursor:
                    # Get all tables in the database/schema
                    if schema_name:
                        # If schema is specified, get tables from that schema
                        cursor.execute(f"""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = %s 
                            AND table_type = 'BASE TABLE'
                            AND table_name NOT LIKE '\\_%%'
                        """, [schema_name])
                    else:
                        # If no schema is specified, use the database name as the schema name
                        # This assumes that the database name is also the schema name
                        schema_name = db_name
                        cursor.execute(f"""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = %s
                            AND table_type = 'BASE TABLE'
                            AND table_name NOT LIKE '\\_%%'
                        """, [schema_name])
                    
                    all_tables = [row[0] for row in cursor.fetchall()]
                    
                    # Filter tables based on the pattern
                    tables_to_process = []
                    if table_name:
                        if table_name in all_tables:
                            tables_to_process.append(table_name)
                        else:
                            stdout_writer(style.WARNING(f"Table '{table_name}' not found in schema '{schema_name or 'default'}'"))
                    else:
                        tables_to_process = all_tables
                    
                    # Process each table
                    for current_table in tables_to_process:
                        # Skip tables that start with underscore
                        if current_table.startswith('_'):
                            continue
                        
                        table_info = DURC_RelationalModelExtractor._process_table(
                            conn, cursor, db_name, schema_name, current_table, all_tables, stdout_writer, style
                        )
                        
                        # Add the table to the relational model
                        relational_model[db_name][current_table] = table_info
                        
                        stdout_writer(f"Processed table: {db_name}.{schema_name + '.' if schema_name else ''}{current_table}")
                    
            except OperationalError as e:
                stdout_writer(style.ERROR(f"Database operation error: {e}"))
            except Exception as e:
                stdout_writer(style.ERROR(f"Error processing database '{db_name}': {e}"))
        
        return relational_model
    
    @staticmethod
    def _process_table(conn, cursor, db_name, schema_name, table, all_tables, stdout_writer, style):
        """
        Process a single table and extract its information.
        
        Args:
            conn: Database connection
            cursor: Database cursor
            db_name (str): Database name
            schema_name (str): Schema name
            table (str): Table name
            all_tables (list): List of all tables in the schema
            stdout_writer: Django stdout writer for output messages
            style: Django style for formatting output messages
            
        Returns:
            dict: Table information including columns and relationships
        """
        # Get table description (columns)
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns c
            WHERE table_name = %s
            {f"AND table_schema = '{schema_name}'" if schema_name else ""}
            ORDER BY ordinal_position
        """, [table])
        
        columns_data = cursor.fetchall()
        
        # Get primary key information
        cursor.execute(f"""
            SELECT ccu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu 
            ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = %s
            {f"AND tc.table_schema = '{schema_name}'" if schema_name else ""}
            AND tc.constraint_type = 'PRIMARY KEY'
        """, [table])
        
        primary_keys = set([row[0] for row in cursor.fetchall()])
        
        # Get foreign key information
        cursor.execute(f"""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = %s
            {f"AND tc.table_schema = '{schema_name}'" if schema_name else ""}
            AND tc.constraint_type = 'FOREIGN KEY'
        """, [table])
        
        foreign_key_columns = set([row[0] for row in cursor.fetchall()])
        
        # Get foreign key relationships
        cursor.execute(f"""
            SELECT kcu.column_name, ccu.table_schema, ccu.table_name, ccu.column_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu 
            ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name = %s
            {f"AND tc.table_schema = '{schema_name}'" if schema_name else ""}
        """, [table])
        
        foreign_keys = {}
        for fk_col, fk_schema, fk_table, fk_target_col in cursor.fetchall():
            foreign_keys[fk_col] = {
                'schema': fk_schema,
                'table': fk_table,
                'column': fk_target_col
            }
        
        # Construct a simplified CREATE TABLE statement
        create_table_sql = DURC_RelationalModelExtractor._generate_create_table_sql(
            schema_name, table, columns_data, primary_keys, foreign_keys
        )
        
        # Process columns
        column_data = DURC_RelationalModelExtractor._process_columns(
            columns_data, primary_keys, foreign_key_columns, foreign_keys, 
            db_name, schema_name, table, all_tables, cursor, stdout_writer, style
        )
        
        # Process relationships
        has_many, belongs_to = DURC_RelationalModelExtractor._process_relationships(
            column_data, foreign_keys, db_name, schema_name, table, cursor, stdout_writer, style
        )
        
        # Create the table info dictionary
        table_info = {
            'table_name': table,
            'db': db_name,
            'column_data': column_data,
            'create_table_sql': create_table_sql
        }
        
        # Add relationships if they exist
        if has_many:
            table_info['has_many'] = has_many
        if belongs_to:
            table_info['belongs_to'] = belongs_to
        
        return table_info
    
    @staticmethod
    def _generate_create_table_sql(schema_name, table, columns_data, primary_keys, foreign_keys):
        """
        Generate a simplified CREATE TABLE SQL statement.
        
        Args:
            schema_name (str): Schema name
            table (str): Table name
            columns_data (list): List of column data tuples
            primary_keys (set): Set of primary key column names
            foreign_keys (dict): Dictionary of foreign key information
            
        Returns:
            str: CREATE TABLE SQL statement
        """
        create_table_parts = [f"CREATE TABLE {schema_name + '.' if schema_name else ''}{table} ("]
        column_parts = []
        
        for col_name, data_type, is_nullable, default_value in columns_data:
            col_def = f"  {col_name} {data_type}"
            
            if not is_nullable == 'YES':
                col_def += " NOT NULL"
            
            if default_value:
                col_def += f" DEFAULT {default_value}"
            
            column_parts.append(col_def)
        
        # Add primary key constraint if any
        if primary_keys:
            column_parts.append(f"  PRIMARY KEY ({', '.join(primary_keys)})")
        
        # Add foreign key constraints
        for fk_col, fk_info in foreign_keys.items():
            # Use the current schema for references if the foreign key is in the same schema
            ref_schema = schema_name if fk_info['schema'] == 'public' else fk_info['schema']
            column_parts.append(
                f"  FOREIGN KEY ({fk_col}) REFERENCES {ref_schema}.{fk_info['table']}({fk_info['column']})"
            )
        
        create_table_parts.append(',\n'.join(column_parts))
        create_table_parts.append(")")
        
        return '\n'.join(create_table_parts)
    
    @staticmethod
    def _process_columns(columns_data, primary_keys, foreign_key_columns, foreign_keys, 
                         db_name, schema_name, table, all_tables, cursor, stdout_writer, style):
        """
        Process column information for a table.
        
        Args:
            columns_data (list): List of column data tuples
            primary_keys (set): Set of primary key column names
            foreign_key_columns (set): Set of foreign key column names
            foreign_keys (dict): Dictionary of foreign key information
            db_name (str): Database name
            schema_name (str): Schema name
            table (str): Table name
            all_tables (list): List of all tables in the schema
            cursor: Database cursor
            stdout_writer: Django stdout writer for output messages
            style: Django style for formatting output messages
            
        Returns:
            list: Processed column data
        """
        processed_columns = []
        
        for col_name, data_type, is_nullable, default_value in columns_data:
            # Determine if this column is a primary key or foreign key
            is_primary = col_name in primary_keys
            is_foreign = col_name in foreign_key_columns
            # Skip columns that start with underscore
            if col_name.startswith('_'):
                continue
            
            # Determine if this is a linked key (ends with _id)
            is_linked_key = col_name.endswith('_id')
            
            # Get foreign key information
            foreign_db = None
            foreign_table = None
            if col_name in foreign_keys:
                foreign_db = db_name  # Assume same database
                foreign_table = foreign_keys[col_name]['table']
            elif is_linked_key and not is_foreign:
                # Try pattern-based relationship detection
                foreign_db, foreign_table = DURC_RelationalModelExtractor._detect_pattern_based_relationship(
                    col_name, db_name, schema_name, table, all_tables, cursor, foreign_keys, stdout_writer, style
                )
                
                if not foreign_table:
                    # Try standard linked key detection
                    foreign_db, foreign_table = DURC_RelationalModelExtractor._detect_linked_key_relationship(
                        col_name, db_name, schema_name, cursor, foreign_keys, stdout_writer, style
                    )
            
            # Determine if auto-increment
            is_auto_increment = False
            if default_value and ('nextval' in str(default_value) or 'auto_increment' in str(default_value).lower()):
                is_auto_increment = True
            
            # Map PostgreSQL data types to simplified types
            simplified_type = DURC_DataTypeMapper.map_data_type(data_type)
            
            processed_columns.append({
                'column_name': col_name,
                'data_type': simplified_type,
                'is_primary_key': is_primary,
                'is_foreign_key': is_foreign,
                'is_linked_key': is_linked_key,
                'foreign_db': foreign_db,
                'foreign_table': foreign_table,
                'is_nullable': is_nullable == 'YES',
                'default_value': default_value,
                'is_auto_increment': is_auto_increment
            })
        
        return processed_columns
    
    @staticmethod
    def _detect_pattern_based_relationship(col_name, db_name, schema_name, table, all_tables, 
                                          cursor, foreign_keys, stdout_writer, style):
        """
        Detect pattern-based relationships for columns following patterns like *_{table_name}_id.
        
        Args:
            col_name (str): Column name
            db_name (str): Database name
            schema_name (str): Schema name
            table (str): Table name
            all_tables (list): List of all tables in the schema
            cursor: Database cursor
            foreign_keys (dict): Dictionary of foreign key information
            stdout_writer: Django stdout writer for output messages
            style: Django style for formatting output messages
            
        Returns:
            tuple: (foreign_db, foreign_table) or (None, None) if not detected
        """
        for potential_table in all_tables:
            # Check if the column follows the pattern *_{table_name}_id
            if col_name.endswith(f"_{potential_table}_id") and col_name != f"{potential_table}_id":
                stdout_writer(style.SUCCESS(
                    f"Detected pattern-based relationship: {schema_name}.{table}.{col_name} -> {schema_name}.{potential_table}"
                ))
                
                # Add to foreign_keys for use in belongs_to relationships
                foreign_keys[col_name] = {
                    'schema': schema_name,
                    'table': potential_table,
                    'column': 'id',  # Assume the primary key is 'id'
                    'is_pattern_based': True
                }
                
                return db_name, potential_table
        
        return None, None
    
    @staticmethod
    def _detect_linked_key_relationship(col_name, db_name, schema_name, cursor, 
                                       foreign_keys, stdout_writer, style):
        """
        Detect linked key relationships for columns ending with _id.
        
        Args:
            col_name (str): Column name
            db_name (str): Database name
            schema_name (str): Schema name
            cursor: Database cursor
            foreign_keys (dict): Dictionary of foreign key information
            stdout_writer: Django stdout writer for output messages
            style: Django style for formatting output messages
            
        Returns:
            tuple: (foreign_db, foreign_table) or (None, None) if not detected
        """
        # Try to infer the foreign table from the column name
        inferred_table = col_name[:-3]  # Remove _id suffix
        
        # First check if this table exists in the current schema
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name = %s
                {f"AND table_schema = '{schema_name}'" if schema_name else ""}
            )
        """, [inferred_table])
        
        if cursor.fetchone()[0]:
            # Table exists in the current schema
            return db_name, inferred_table
        else:
            # If not found in current schema, check all schemas in this database
            cursor.execute("""
                SELECT table_schema 
                FROM information_schema.tables 
                WHERE table_name = %s
                AND table_schema != 'information_schema'
                AND table_schema != 'pg_catalog'
                LIMIT 1
            """, [inferred_table])
            
            result = cursor.fetchone()
            if result:
                # Found in another schema
                foreign_schema = result[0]
                
                # Store the cross-schema information
                # Use the table parameter passed to this method
                stdout_writer(style.SUCCESS(
                    f"Detected cross-schema relationship: {schema_name}.table.{col_name} -> {foreign_schema}.{inferred_table}"
                ))
                
                # Add the schema information to the column data
                foreign_keys[col_name] = {
                    'schema': foreign_schema,
                    'table': inferred_table,
                    'column': 'id',  # Assume the primary key is 'id'
                    'is_cross_schema': True
                }
                
                return db_name, inferred_table
        
        return None, None
    
    @staticmethod
    def _process_relationships(column_data, foreign_keys, db_name, schema_name, table, cursor, stdout_writer, style):
        """
        Process relationships for a table.
        
        Args:
            column_data (list): Processed column data
            foreign_keys (dict): Dictionary of foreign key information
            db_name (str): Database name
            schema_name (str): Schema name
            table (str): Table name
            cursor: Database cursor
            stdout_writer: Django stdout writer for output messages
            style: Django style for formatting output messages
            
        Returns:
            tuple: (has_many, belongs_to) dictionaries
        """
        has_many = {}
        belongs_to = {}
        
        # Find "belongs_to" relationships (foreign keys in this table)
        for col in column_data:
            if col['is_foreign_key'] or col['is_linked_key']:
                if col['foreign_table']:
                    # Determine the prefix (if any)
                    prefix = None
                    if col['column_name'].endswith('_id'):
                        prefix_candidate = col['column_name'][:-3]  # Remove _id
                        if prefix_candidate != col['foreign_table']:
                            prefix = prefix_candidate
                    
                    # Use the current schema for the foreign table if it's in the public schema
                    foreign_db = col['foreign_db']
                    foreign_table = col['foreign_table']
                    
                    # Check if this is a cross-schema relationship
                    relationship = {
                        'prefix': prefix,
                        'type': foreign_table,
                        'to_table': foreign_table,
                        'to_db': foreign_db,
                        'local_key': col['column_name']
                    }
                    
                    # Add schema information if this is a cross-schema relationship
                    if col['column_name'] in foreign_keys and 'is_cross_schema' in foreign_keys[col['column_name']]:
                        relationship['to_schema'] = foreign_keys[col['column_name']]['schema']
                        stdout_writer(style.SUCCESS(
                            f"Adding cross-schema relationship to belongs_to: {schema_name}.{table}.{col['column_name']} -> {relationship['to_schema']}.{foreign_table}"
                        ))
                    
                    belongs_to[col['column_name'][:-3] if col['column_name'].endswith('_id') else col['column_name']] = relationship
        
        # Find "has_many" relationships (foreign keys in other tables pointing to this table)
        # First, check for foreign keys in the same schema
        cursor.execute(f"""
            SELECT tc.table_name, kcu.column_name, tc.table_schema
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu 
            ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND ccu.table_name = %s
            {f"AND ccu.table_schema = '{schema_name}'" if schema_name else ""}
        """, [table])
        
        for ref_table, ref_column, ref_schema in cursor.fetchall():
            # Skip tables that start with underscore
            if ref_table.startswith('_'):
                continue
            
            # Determine the prefix (if any)
            prefix = None
            if ref_column.endswith('_id'):
                prefix_candidate = ref_column[:-3]  # Remove _id
                if prefix_candidate != table:
                    prefix = prefix_candidate
            
            relation_name = ref_table
            if prefix:
                relation_name = f"{prefix}_{ref_table}"
            
            relationship = {
                'prefix': prefix,
                'type': ref_table,
                'from_table': ref_table,
                'from_db': db_name,
                'from_column': ref_column
            }
            
            # Add schema information if this is a cross-schema relationship
            if ref_schema != schema_name:
                relationship['from_schema'] = ref_schema
                stdout_writer(style.SUCCESS(
                    f"Adding cross-schema relationship to has_many: {schema_name}.{table} <- {ref_schema}.{ref_table}.{ref_column}"
                ))
            
            has_many[relation_name] = relationship
        
        # Now check for potential cross-schema relationships based on naming conventions
        # Look for tables in other schemas that might have columns ending with _id that match this table name
        cursor.execute("""
            SELECT c.table_schema, c.table_name, c.column_name
            FROM information_schema.columns c
            JOIN information_schema.tables t ON c.table_schema = t.table_schema AND c.table_name = t.table_name
            WHERE c.column_name = %s
            AND t.table_type = 'BASE TABLE'
            AND c.table_schema != %s
            AND c.table_schema NOT IN ('information_schema', 'pg_catalog')
        """, [f"{table}_id", schema_name])
        
        for ref_schema, ref_table, ref_column in cursor.fetchall():
            # Skip tables that start with underscore
            if ref_table.startswith('_'):
                continue
            
            # This is a potential cross-schema relationship based on naming convention
            relation_name = f"{ref_schema}_{ref_table}"
            
            # Check if this relationship already exists (might have been detected through foreign keys)
            if relation_name not in has_many:
                stdout_writer(style.SUCCESS(
                    f"Detected potential cross-schema has_many relationship through naming convention: {schema_name}.{table} <- {ref_schema}.{ref_table}.{ref_column}"
                ))
                
                has_many[relation_name] = {
                    'prefix': None,
                    'type': ref_table,
                    'from_table': ref_table,
                    'from_db': db_name,
                    'from_schema': ref_schema,
                    'from_column': ref_column,
                    'is_inferred': True
                }
        
        return has_many, belongs_to
