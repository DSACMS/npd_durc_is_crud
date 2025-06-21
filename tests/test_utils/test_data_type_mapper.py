import unittest
from durc_is_crud.management.commands.durc_utils.data_type_mapper import DURC_DataTypeMapper

class TestDataTypeMapper(unittest.TestCase):
    def test_integer_types(self):
        """Test mapping of integer data types"""
        integer_types = ['integer', 'int', 'int4', 'serial', 'bigint', 'int8', 'bigserial', 'smallint', 'int2', 'smallserial']
        for pg_type in integer_types:
            self.assertEqual(DURC_DataTypeMapper.map_data_type(pg_type), 'int')
            # Test with uppercase as well
            self.assertEqual(DURC_DataTypeMapper.map_data_type(pg_type.upper()), 'int')
    
    def test_string_types(self):
        """Test mapping of string data types"""
        # Test varchar types
        self.assertEqual(DURC_DataTypeMapper.map_data_type('varchar'), 'varchar')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('varchar(255)'), 'varchar')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('character varying'), 'varchar')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('character varying(100)'), 'varchar')
        
        # Test text type
        self.assertEqual(DURC_DataTypeMapper.map_data_type('text'), 'text')
        
        # Test char types
        self.assertEqual(DURC_DataTypeMapper.map_data_type('char'), 'char')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('character'), 'char')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('character(10)'), 'char')
    
    def test_numeric_types(self):
        """Test mapping of numeric data types"""
        # Test float types
        self.assertEqual(DURC_DataTypeMapper.map_data_type('real'), 'float')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('float4'), 'float')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('float8'), 'float')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('double precision'), 'float')
        
        # Test decimal types
        self.assertEqual(DURC_DataTypeMapper.map_data_type('numeric'), 'decimal')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('numeric(10,2)'), 'decimal')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('decimal'), 'decimal')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('decimal(10,2)'), 'decimal')
    
    def test_date_time_types(self):
        """Test mapping of date and time data types"""
        self.assertEqual(DURC_DataTypeMapper.map_data_type('date'), 'date')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('timestamp'), 'timestamp')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('timestamp with time zone'), 'timestamp')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('time'), 'time')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('time with time zone'), 'time')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('datetime'), 'datetime')
    
    def test_other_types(self):
        """Test mapping of other data types"""
        self.assertEqual(DURC_DataTypeMapper.map_data_type('bytea'), 'blob')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('boolean'), 'tinyint')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('bool'), 'tinyint')
        
        # Test fallback for unknown types
        self.assertEqual(DURC_DataTypeMapper.map_data_type('json'), 'json')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('jsonb'), 'jsonb')
        self.assertEqual(DURC_DataTypeMapper.map_data_type('uuid'), 'uuid')

if __name__ == '__main__':
    unittest.main()
