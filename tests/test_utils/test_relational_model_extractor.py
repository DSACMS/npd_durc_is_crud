import unittest
from unittest import mock
from django.test import TestCase
from django.db import connection
from django.core.management.base import CommandError
from durc_is_crud.management.commands.durc_utils.relational_model_extractor import DURC_RelationalModelExtractor

class TestRelationalModelExtractor(TestCase):
    """Test cases for the DURC_RelationalModelExtractor utility."""
    
    @mock.patch('django.db.connections')
    @mock.patch('django.db.connection')
    def test_extract_relational_model_basic(self, mock_connection, mock_connections):
        """Test basic extraction of a relational model."""
        # Set up mock cursor
        mock_cursor = mock.MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock the cursor fetchall results for different queries
        mock_cursor.fetchall.side_effect = [
            # Tables query result
            [('test_table',)],
            # Columns query result
            [('id', 'integer', 'NO', 'nextval(\'test_table_id_seq\'::regclass)'),
             ('name', 'character varying', 'NO', None)],
            # Primary key query result
            [('id',)],
            # Foreign key columns query result
            [],
            # Foreign key relationships query result
            [],
            # Has-many relationships query result
            []
        ]
        
        # Mock the cursor fetchone result for linked key relationship check
        mock_cursor.fetchone.return_value = (False,)
        
        # Set up mock style and stdout_writer
        mock_style = mock.MagicMock()
        mock_stdout_writer = mock.MagicMock()
        
        # Set up the patterns to extract
        patterns = [{'db': 'test_db', 'schema': 'public', 'table': None}]
        
        # Call the extract_relational_model method
        result = DURC_RelationalModelExtractor.extract_relational_model(
            patterns, mock_stdout_writer, mock_style
        )
        
        # Assert that the result has the expected structure
        self.assertIn('test_db', result)
        self.assertIn('test_table', result['test_db'])
        self.assertEqual(result['test_db']['test_table']['table_name'], 'test_table')
        self.assertEqual(result['test_db']['test_table']['db'], 'test_db')
        self.assertIn('column_data', result['test_db']['test_table'])
        self.assertIn('create_table_sql', result['test_db']['test_table'])
        
        # Assert that the column data has the expected structure
        column_data = result['test_db']['test_table']['column_data']
        self.assertEqual(len(column_data), 2)
        
        # Check the id column
        id_column = next(col for col in column_data if col['column_name'] == 'id')
        self.assertEqual(id_column['data_type'], 'int')
        self.assertTrue(id_column['is_primary_key'])
        self.assertFalse(id_column['is_foreign_key'])
        self.assertTrue(id_column['is_auto_increment'])
        
        # Check the name column
        name_column = next(col for col in column_data if col['column_name'] == 'name')
        self.assertEqual(name_column['data_type'], 'varchar')
        self.assertFalse(name_column['is_primary_key'])
        self.assertFalse(name_column['is_foreign_key'])
        self.assertFalse(name_column['is_auto_increment'])
    
    @mock.patch('django.db.connections')
    @mock.patch('django.db.connection')
    def test_extract_relational_model_with_foreign_keys(self, mock_connection, mock_connections):
        """Test extraction of a relational model with foreign keys."""
        # Set up mock cursor
        mock_cursor = mock.MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock the cursor fetchall results for different queries
        mock_cursor.fetchall.side_effect = [
            # Tables query result
            [('user',), ('post',)],
            # User columns query result
            [('id', 'integer', 'NO', 'nextval(\'user_id_seq\'::regclass)'),
             ('name', 'character varying', 'NO', None)],
            # User primary key query result
            [('id',)],
            # User foreign key columns query result
            [],
            # User foreign key relationships query result
            [],
            # User has-many relationships query result
            [('post', 'user_id', 'public')],
            # Post columns query result
            [('id', 'integer', 'NO', 'nextval(\'post_id_seq\'::regclass)'),
             ('title', 'character varying', 'NO', None),
             ('user_id', 'integer', 'NO', None)],
            # Post primary key query result
            [('id',)],
            # Post foreign key columns query result
            [('user_id',)],
            # Post foreign key relationships query result
            [('user_id', 'public', 'user', 'id')],
            # Post has-many relationships query result
            []
        ]
        
        # Mock the cursor fetchone result for linked key relationship check
        mock_cursor.fetchone.return_value = (False,)
        
        # Set up mock style and stdout_writer
        mock_style = mock.MagicMock()
        mock_stdout_writer = mock.MagicMock()
        
        # Set up the patterns to extract
        patterns = [{'db': 'test_db', 'schema': 'public', 'table': None}]
        
        # Call the extract_relational_model method
        result = DURC_RelationalModelExtractor.extract_relational_model(
            patterns, mock_stdout_writer, mock_style
        )
        
        # Assert that the result has the expected structure
        self.assertIn('test_db', result)
        self.assertIn('user', result['test_db'])
        self.assertIn('post', result['test_db'])
        
        # Check the user table
        user_table = result['test_db']['user']
        self.assertEqual(user_table['table_name'], 'user')
        self.assertIn('has_many', user_table)
        self.assertIn('post', user_table['has_many'])
        
        # Check the post table
        post_table = result['test_db']['post']
        self.assertEqual(post_table['table_name'], 'post')
        self.assertIn('belongs_to', post_table)
        self.assertIn('user', post_table['belongs_to'])
        
        # Check the post's user_id column
        user_id_column = next(col for col in post_table['column_data'] if col['column_name'] == 'user_id')
        self.assertEqual(user_id_column['data_type'], 'int')
        self.assertTrue(user_id_column['is_foreign_key'])
        self.assertTrue(user_id_column['is_linked_key'])
        self.assertEqual(user_id_column['foreign_table'], 'user')
