class DURC_DataTypeMapper:
    """
    Utility class for mapping database data types to simplified types used in DURC schema.
    """
    
    @staticmethod
    def map_data_type(pg_type):
        """Map PostgreSQL data types to simplified types used in DURC schema"""
        pg_type = pg_type.lower()
        
        # Integer types
        if pg_type in ('integer', 'int', 'int4', 'serial', 'bigint', 'int8', 'bigserial', 'smallint', 'int2', 'smallserial'):
            return 'int'
        
        # String types
        if pg_type.startswith('varchar') or pg_type.startswith('character varying'):
            return 'varchar'
        if pg_type == 'text':
            return 'text'
        if pg_type == 'char' or pg_type.startswith('character'):
            return 'char'
        
        # Text types
        if pg_type == 'mediumtext':
            return 'mediumtext'
        if pg_type == 'longtext':
            return 'longtext'
        
        # Numeric types
        if pg_type == 'real' or pg_type == 'float4' or pg_type == 'float8' or pg_type == 'double precision':
            return 'float'
        if pg_type.startswith('numeric') or pg_type.startswith('decimal'):
            return 'decimal'
        
        # Date/time types
        if pg_type == 'date':
            return 'date'
        if pg_type == 'timestamp' or pg_type.startswith('timestamp'):
            return 'timestamp'
        if pg_type == 'time' or pg_type.startswith('time'):
            return 'time'
        if pg_type == 'datetime':
            return 'datetime'
        
        # Binary types
        if pg_type == 'bytea':
            return 'blob'
        
        # Boolean types
        if pg_type == 'boolean' or pg_type == 'bool':
            return 'tinyint'
        
        # Default fallback
        return pg_type
