import os
import json
import unittest
from unittest.mock import patch, mock_open
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

class TestDurcCompileCommand(unittest.TestCase):
    def setUp(self):
        # Create test directories
        os.makedirs('durc_config', exist_ok=True)
        os.makedirs('durc_generated', exist_ok=True)
        
        # Create a sample relational model JSON file
        self.input_path = os.path.join('durc_config', 'DURC_relational_model.json')
        self.sample_model = {
            'testdb': {
                'table1': {
                    'table_name': 'table1',
                    'db': 'testdb',
                    'column_data': [
                        {
                            'column_name': 'id',
                            'data_type': 'int',
                            'is_primary_key': True,
                            'is_foreign_key': False,
                            'is_linked_key': False,
                            'is_nullable': False,
                            'is_auto_increment': True
                        },
                        {
                            'column_name': 'name',
                            'data_type': 'varchar',
                            'is_primary_key': False,
                            'is_foreign_key': False,
                            'is_linked_key': False,
                            'is_nullable': False,
                            'is_auto_increment': False
                        }
                    ]
                }
            }
        }
        
        with open(self.input_path, 'w') as f:
            json.dump(self.sample_model, f)
    
    def tearDown(self):
        # Clean up test files and directories
        if os.path.exists(self.input_path):
            os.remove(self.input_path)
        
        placeholder_file = os.path.join('durc_generated', 'durc_compile_placeholder.txt')
        if os.path.exists(placeholder_file):
            os.remove(placeholder_file)
        
        if os.path.exists('durc_config'):
            os.rmdir('durc_config')
        
        if os.path.exists('durc_generated'):
            os.rmdir('durc_generated')
    
    def test_durc_compile_command_default_paths(self):
        # Test the command with default input and output paths
        out = StringIO()
        call_command('durc_compile', stdout=out)
        
        # Check that the placeholder file was created
        placeholder_file = os.path.join('durc_generated', 'durc_compile_placeholder.txt')
        self.assertTrue(os.path.exists(placeholder_file))
        
        # Check the content of the placeholder file
        with open(placeholder_file, 'r') as f:
            content = f.read()
            self.assertIn('DURC compile command was run with input file', content)
    
    def test_durc_compile_command_custom_paths(self):
        # Test the command with custom input and output paths
        custom_input = 'custom_input.json'
        custom_output = 'custom_output_dir'
        
        # Create a custom input file
        with open(custom_input, 'w') as f:
            json.dump(self.sample_model, f)
        
        # Create a custom output directory
        os.makedirs(custom_output, exist_ok=True)
        
        # Call the command with custom paths
        out = StringIO()
        call_command('durc_compile', input_json_file=custom_input, output_dir=custom_output, stdout=out)
        
        # Check that the placeholder file was created in the custom output directory
        placeholder_file = os.path.join(custom_output, 'durc_compile_placeholder.txt')
        self.assertTrue(os.path.exists(placeholder_file))
        
        # Clean up custom files and directories
        os.remove(custom_input)
        os.remove(placeholder_file)
        os.rmdir(custom_output)
    
    def test_durc_compile_command_nonexistent_input(self):
        # Test that the command raises an error when the input file doesn't exist
        nonexistent_input = 'nonexistent.json'
        
        # Call the command with a nonexistent input file
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command('durc_compile', input_json_file=nonexistent_input, stdout=out)

if __name__ == '__main__':
    unittest.main()
