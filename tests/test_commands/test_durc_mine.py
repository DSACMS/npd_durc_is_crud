import os
import json
import unittest
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

class TestDurcMineCommand(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test outputs
        os.makedirs('durc_config', exist_ok=True)
        self.output_path = os.path.join('durc_config', 'DURC_relational_model.json')
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        if os.path.exists('durc_config'):
            import shutil
            shutil.rmtree('durc_config')
    
    @patch('durc_is_crud.management.commands.durc_utils.include_pattern_parser.DURC_IncludePatternParser.parse_include_patterns')
    @patch('durc_is_crud.management.commands.durc_utils.relational_model_extractor.DURC_RelationalModelExtractor.extract_relational_model')
    def test_durc_mine_command(self, mock_extract, mock_parse):
        # Mock the return values
        mock_parse.return_value = [{'db': 'testdb', 'schema': 'public', 'table': None}]
        mock_extract.return_value = {'testdb': {'table1': {'table_name': 'table1', 'db': 'testdb'}}}
        
        # Call the command
        out = StringIO()
        call_command('durc_mine', include=['testdb.public'], stdout=out)
        
        # Check that the output file was created
        self.assertTrue(os.path.exists(self.output_path))
        
        # Check the content of the output file
        with open(self.output_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, {'testdb': {'table1': {'table_name': 'table1', 'db': 'testdb'}}})
        
        # Check that the mocks were called with the expected arguments
        mock_parse.assert_called_once_with(['testdb.public'])
        mock_extract.assert_called_once()
    
    def test_durc_mine_command_no_include(self):
        # Test that the command raises an error when no include patterns are provided
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command('durc_mine', stdout=out)
    
    @patch('durc_is_crud.management.commands.durc_utils.include_pattern_parser.DURC_IncludePatternParser.parse_include_patterns')
    @patch('durc_is_crud.management.commands.durc_utils.relational_model_extractor.DURC_RelationalModelExtractor.extract_relational_model')
    def test_durc_mine_command_custom_output(self, mock_extract, mock_parse):
        # Mock the return values
        mock_parse.return_value = [{'db': 'testdb', 'schema': 'public', 'table': None}]
        mock_extract.return_value = {'testdb': {'table1': {'table_name': 'table1', 'db': 'testdb'}}}
        
        # Custom output path
        custom_output = 'custom_output.json'
        
        # Call the command with custom output path
        out = StringIO()
        call_command('durc_mine', include=['testdb.public'], output_json_file=custom_output, stdout=out)
        
        # Check that the output file was created
        self.assertTrue(os.path.exists(custom_output))
        
        # Check the content of the output file
        with open(custom_output, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, {'testdb': {'table1': {'table_name': 'table1', 'db': 'testdb'}}})
        
        # Clean up the custom output file
        os.remove(custom_output)
    
    @patch('durc_is_crud.management.commands.durc_utils.include_pattern_parser.DURC_IncludePatternParser.parse_include_patterns')
    @patch('durc_is_crud.management.commands.durc_utils.relational_model_extractor.DURC_RelationalModelExtractor.extract_relational_model')
    def test_durc_mine_postgresql_schema_structure(self, mock_extract, mock_parse):
        # Mock the return values for PostgreSQL with schema structure
        mock_parse.return_value = [{'db': 'testdb', 'schema': 'public', 'table': None}]
        
        # Mock PostgreSQL output with schema layer: db -> schema -> table
        mock_extract.return_value = {
            'testdb': {
                'public': {
                    'users': {
                        'table_name': 'users',
                        'db': 'testdb',
                        'schema': 'public',
                        'column_data': [
                            {
                                'column_name': 'id',
                                'data_type': 'int',
                                'is_primary_key': True,
                                'is_foreign_key': False,
                                'is_linked_key': False,
                                'foreign_db': None,
                                'foreign_table': None,
                                'is_nullable': False,
                                'default_value': None,
                                'is_auto_increment': True
                            }
                        ],
                        'create_table_sql': 'CREATE TABLE public.users (id SERIAL PRIMARY KEY)'
                    }
                }
            }
        }
        
        # Call the command
        out = StringIO()
        call_command('durc_mine', include=['testdb.public'], stdout=out)
        
        # Check that the output file was created
        self.assertTrue(os.path.exists(self.output_path))
        
        # Check the content of the output file has the correct PostgreSQL schema structure
        with open(self.output_path, 'r') as f:
            data = json.load(f)
            
            # Verify the structure is db -> schema -> table
            self.assertIn('testdb', data)
            self.assertIn('public', data['testdb'])
            self.assertIn('users', data['testdb']['public'])
            
            # Verify table info includes schema field
            table_info = data['testdb']['public']['users']
            self.assertEqual(table_info['table_name'], 'users')
            self.assertEqual(table_info['db'], 'testdb')
            self.assertEqual(table_info['schema'], 'public')
        
        # Check that the mocks were called with the expected arguments
        mock_parse.assert_called_once_with(['testdb.public'])
        mock_extract.assert_called_once()

if __name__ == '__main__':
    unittest.main()
