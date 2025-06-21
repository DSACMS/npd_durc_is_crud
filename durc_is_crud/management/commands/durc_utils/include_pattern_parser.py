from django.core.management.base import CommandError

class DURC_IncludePatternParser:
    """
    Utility class for parsing include patterns for database, schema, and table selection.
    """
    
    @staticmethod
    def parse_include_patterns(patterns):
        """
        Parse the include patterns into a structured format.
        
        Args:
            patterns (list): List of pattern strings in the format db.schema.table, db.schema, or db
            
        Returns:
            list: A list of dictionaries with keys:
                - db: database name
                - schema: schema name (or None for all schemas)
                - table: table name (or None for all tables)
                
        Raises:
            CommandError: If an invalid pattern format is provided
        """
        result = []
        
        for pattern in patterns:
            parts = pattern.split('.')
            
            if len(parts) == 1:
                # Format: db
                result.append({
                    'db': parts[0],
                    'schema': None,
                    'table': None
                })
            elif len(parts) == 2:
                # Format: db.schema
                result.append({
                    'db': parts[0],
                    'schema': parts[1],
                    'table': None
                })
            elif len(parts) == 3:
                # Format: db.schema.table
                result.append({
                    'db': parts[0],
                    'schema': parts[1],
                    'table': parts[2]
                })
            else:
                raise CommandError(f"Invalid include pattern: {pattern}. Use format: db.schema.table, db.schema, or db")
        
        return result
