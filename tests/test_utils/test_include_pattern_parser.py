import unittest
from django.core.management.base import CommandError
from durc_is_crud.management.commands.durc_utils.include_pattern_parser import DURC_IncludePatternParser

class TestIncludePatternParser(unittest.TestCase):
    def test_db_only_pattern(self):
        """Test parsing of database-only patterns"""
        patterns = ['db1', 'db2']
        result = DURC_IncludePatternParser.parse_include_patterns(patterns)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {'db': 'db1', 'schema': None, 'table': None})
        self.assertEqual(result[1], {'db': 'db2', 'schema': None, 'table': None})
    
    def test_db_schema_pattern(self):
        """Test parsing of database.schema patterns"""
        patterns = ['db1.schema1', 'db2.schema2']
        result = DURC_IncludePatternParser.parse_include_patterns(patterns)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {'db': 'db1', 'schema': 'schema1', 'table': None})
        self.assertEqual(result[1], {'db': 'db2', 'schema': 'schema2', 'table': None})
    
    def test_db_schema_table_pattern(self):
        """Test parsing of database.schema.table patterns"""
        patterns = ['db1.schema1.table1', 'db2.schema2.table2']
        result = DURC_IncludePatternParser.parse_include_patterns(patterns)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {'db': 'db1', 'schema': 'schema1', 'table': 'table1'})
        self.assertEqual(result[1], {'db': 'db2', 'schema': 'schema2', 'table': 'table2'})
    
    def test_mixed_patterns(self):
        """Test parsing of mixed pattern types"""
        patterns = ['db1', 'db2.schema2', 'db3.schema3.table3']
        result = DURC_IncludePatternParser.parse_include_patterns(patterns)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], {'db': 'db1', 'schema': None, 'table': None})
        self.assertEqual(result[1], {'db': 'db2', 'schema': 'schema2', 'table': None})
        self.assertEqual(result[2], {'db': 'db3', 'schema': 'schema3', 'table': 'table3'})
    
    def test_invalid_pattern(self):
        """Test that invalid patterns raise CommandError"""
        patterns = ['db1.schema1.table1.invalid']
        
        with self.assertRaises(CommandError):
            DURC_IncludePatternParser.parse_include_patterns(patterns)

if __name__ == '__main__':
    unittest.main()
