#!/usr/bin/env python3
"""
Tests for the DURC Diagram Generator - Graphviz Implementation
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from durc_diagram_graphviz import SQLGlotParser, GraphvizDiagramGenerator


class TestSQLGlotParser(unittest.TestCase):
    """Test cases for SQLGlotParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_sql = """
-- Diagram Section: User Management
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Diagram Section: Content Management  
CREATE TABLE "post" (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "comment" (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- This table should be ignored
CREATE TABLE "_internal_table" (
    id SERIAL PRIMARY KEY,
    data TEXT
);

-- This table should also be ignored
CREATE TABLE "Should be Ignored" (
    id SERIAL PRIMARY KEY,
    data TEXT
);
"""
    
    def test_parse_diagram_section_comment(self):
        """Test parsing of diagram section comments."""
        # Valid diagram section comment
        comment = "-- Diagram Section: User Management"
        result = SQLGlotParser._parse_diagram_section_comment(comment)
        self.assertEqual(result, "User Management")
        
        # Case insensitive
        comment = "-- diagram section: Content Management"
        result = SQLGlotParser._parse_diagram_section_comment(comment)
        self.assertEqual(result, "Content Management")
        
        # With extra spaces
        comment = "--   Diagram   Section  :   Admin Panel   "
        result = SQLGlotParser._parse_diagram_section_comment(comment)
        self.assertEqual(result, "Admin Panel")
        
        # Invalid comment (wrong label)
        comment = "-- Other Section: Something"
        result = SQLGlotParser._parse_diagram_section_comment(comment)
        self.assertIsNone(result)
        
        # No colon
        comment = "-- Diagram Section Something"
        result = SQLGlotParser._parse_diagram_section_comment(comment)
        self.assertIsNone(result)
    
    def test_find_next_create_table(self):
        """Test finding the next CREATE TABLE statement."""
        lines = [
            "-- Some comment",
            "-- Diagram Section: Test",
            "DROP TABLE IF EXISTS test;",
            'CREATE TABLE "test" (',
            "    id SERIAL PRIMARY KEY",
            ");"
        ]
        
        result = SQLGlotParser._find_next_create_table(lines, 1)
        self.assertEqual(result, "test")
        
        # Should skip ignored tables
        lines_with_ignored = [
            "-- Diagram Section: Test",
            'CREATE TABLE "_ignored" (',
            "    id SERIAL PRIMARY KEY",
            ");",
            'CREATE TABLE "valid" (',
            "    id SERIAL PRIMARY KEY",
            ");"
        ]
        
        result = SQLGlotParser._find_next_create_table(lines_with_ignored, 0)
        self.assertEqual(result, "valid")
    
    def test_parse_single_file(self):
        """Test parsing a complete SQL file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(self.sample_sql)
            f.flush()
            
            try:
                tables, sections = SQLGlotParser._parse_single_file(f.name)
                
                # Check that we got the expected tables
                expected_tables = {'user', 'post', 'comment'}
                self.assertEqual(set(tables.keys()), expected_tables)
                
                # Check that ignored tables are not included
                self.assertNotIn('_internal_table', tables)
                self.assertNotIn('Should be Ignored', tables)
                
                # Check sections
                self.assertEqual(sections.get('user'), 'User Management')
                self.assertEqual(sections.get('post'), 'Content Management')
                self.assertNotIn('comment', sections)  # No section comment for comment table
                
                # Check table structure
                user_table = tables['user']
                self.assertEqual(user_table['table_name'], 'user')
                self.assertTrue(len(user_table['columns']) > 0)
                
                # Check foreign key detection
                post_table = tables['post']
                user_id_column = next((col for col in post_table['columns'] if col['column_name'] == 'user_id'), None)
                self.assertIsNotNone(user_id_column)
                if user_id_column:  # Type guard for Pylance
                    self.assertTrue(user_id_column['is_foreign_key'])
                    self.assertEqual(user_id_column['foreign_table'], 'user')
                
            finally:
                os.unlink(f.name)


class TestGraphvizDiagramGenerator(unittest.TestCase):
    """Test cases for GraphvizDiagramGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_tables = {
            'user': {
                'table_name': 'user',
                'columns': [
                    {'column_name': 'id', 'data_type': 'SERIAL', 'is_foreign_key': False, 'foreign_table': None},
                    {'column_name': 'username', 'data_type': 'VARCHAR(50)', 'is_foreign_key': False, 'foreign_table': None},
                    {'column_name': 'email', 'data_type': 'VARCHAR(100)', 'is_foreign_key': False, 'foreign_table': None}
                ]
            },
            'post': {
                'table_name': 'post',
                'columns': [
                    {'column_name': 'id', 'data_type': 'SERIAL', 'is_foreign_key': False, 'foreign_table': None},
                    {'column_name': 'title', 'data_type': 'VARCHAR(200)', 'is_foreign_key': False, 'foreign_table': None},
                    {'column_name': 'user_id', 'data_type': 'INTEGER', 'is_foreign_key': True, 'foreign_table': 'user'}
                ]
            }
        }
        
        self.sample_sections = {
            'user': 'User Management',
            'post': 'Content Management'
        }
    
    def test_generate_table_html(self):
        """Test HTML table generation."""
        table_info = self.sample_tables['user']
        table_color = '#FFE5E5'
        
        html = GraphvizDiagramGenerator._generate_table_html(table_info, table_color)
        
        # Check that HTML contains expected elements
        self.assertIn('<TABLE', html)
        self.assertIn('user', html)  # Table name
        self.assertIn('username', html)  # Column name
        self.assertIn('VARCHAR(50)', html)  # Data type
        self.assertIn(table_color, html)  # Background color
        self.assertIn('POINT-SIZE="16"', html)  # Table name font size
        self.assertIn('POINT-SIZE="12"', html)  # Column font size
    
    def test_generate_table_html_with_foreign_key(self):
        """Test HTML table generation with foreign keys."""
        table_info = self.sample_tables['post']
        table_color = '#E5F3FF'
        
        html = GraphvizDiagramGenerator._generate_table_html(table_info, table_color)
        
        # Check that foreign key is marked
        self.assertIn('(FK)', html)
        self.assertIn('user_id', html)
    
    @patch('graphviz.Digraph')
    def test_generate_diagram(self, mock_digraph):
        """Test diagram generation."""
        mock_dot = MagicMock()
        mock_digraph.return_value = mock_dot
        
        result = GraphvizDiagramGenerator.generate_diagram(
            self.sample_tables, 
            self.sample_sections
        )
        
        # Check that Digraph was created
        mock_digraph.assert_called_once()
        
        # Check that attributes were set
        self.assertTrue(mock_dot.attr.called)
        
        # Check that nodes were added
        self.assertTrue(mock_dot.node.called)
        
        # Check that edges were added (for foreign key relationships)
        self.assertTrue(mock_dot.edge.called)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_end_to_end_parsing_and_generation(self):
        """Test the complete workflow from SQL to diagram."""
        sample_sql = """
-- Diagram Section: Test Section
CREATE TABLE "test_table" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    other_table_id INTEGER
);

CREATE TABLE "other_table" (
    id SERIAL PRIMARY KEY,
    description TEXT
);
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(sample_sql)
            f.flush()
            
            try:
                # Parse the SQL
                tables, sections = SQLGlotParser.parse_sql_files([f.name])
                
                # Generate diagram
                dot = GraphvizDiagramGenerator.generate_diagram(tables, sections)
                
                # Basic checks
                self.assertIsNotNone(dot)
                self.assertEqual(len(tables), 2)
                self.assertEqual(len(sections), 1)
                self.assertEqual(sections['test_table'], 'Test Section')
                
            finally:
                os.unlink(f.name)


if __name__ == '__main__':
    unittest.main()
