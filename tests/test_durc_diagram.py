#!/usr/bin/env python3
"""
Test suite for DURC Diagram Generator

This module contains tests for the durc_diagram.py script functionality.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the project root to the path so we can import durc_diagram
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from durc_diagram import SQLParser, MermaidGenerator


class TestSQLParser(unittest.TestCase):
    """Test cases for SQL parsing functionality using actual DURC test files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.test_sql_files = [
            self.project_root / 'AI_Instructions' / 'durc_postgres_test_files' / 'DURC_aaa.postgres.sql',
            self.project_root / 'AI_Instructions' / 'durc_postgres_test_files' / 'DURC_bbb.postgres.sql'
        ]
        
        # Verify test files exist
        for sql_file in self.test_sql_files:
            if not sql_file.exists():
                self.skipTest(f"Test SQL file not found: {sql_file}")
    
    def test_parse_durc_test_files(self):
        """Test parsing the actual DURC test SQL files."""
        existing_files = [str(f) for f in self.test_sql_files if f.exists()]
        
        if not existing_files:
            self.skipTest("No DURC test SQL files found")
        
        tables, sections = SQLParser.parse_sql_files(existing_files)
        
        # Should find multiple tables
        self.assertGreater(len(tables), 0)
        
        # Verify some expected tables from DURC_aaa.postgres.sql
        expected_tables = ['author', 'book', 'post', 'comment', 'vote']
        found_tables = [table for table in expected_tables if table in tables]
        self.assertGreater(len(found_tables), 0, "Should find at least some expected tables")
        
        # Test that "Should be Ignored" table is properly filtered out
        self.assertNotIn('Should be Ignored', tables)
        
        # Test foreign key detection on known relationships
        if 'comment' in tables and 'post' in tables:
            comment_table = tables['comment']
            post_id_columns = [col for col in comment_table['columns'] if col['column_name'] == 'post_id']
            if post_id_columns:
                self.assertTrue(post_id_columns[0]['is_foreign_key'])
                self.assertEqual(post_id_columns[0]['foreign_table'], 'post')
        
        if 'vote' in tables and 'post' in tables:
            vote_table = tables['vote']
            post_id_columns = [col for col in vote_table['columns'] if col['column_name'] == 'post_id']
            if post_id_columns:
                self.assertTrue(post_id_columns[0]['is_foreign_key'])
                self.assertEqual(post_id_columns[0]['foreign_table'], 'post')
    
    def test_table_structure_parsing(self):
        """Test that table structures are parsed correctly."""
        existing_files = [str(f) for f in self.test_sql_files if f.exists()]
        
        if not existing_files:
            self.skipTest("No DURC test SQL files found")
        
        tables, sections = SQLParser.parse_sql_files(existing_files)
        
        # Test a specific table structure if it exists
        if 'author' in tables:
            author_table = tables['author']
            self.assertEqual(author_table['table_name'], 'author')
            self.assertGreater(len(author_table['columns']), 0)
            
            # Should have id column
            id_columns = [col for col in author_table['columns'] if col['column_name'] == 'id']
            self.assertEqual(len(id_columns), 1)
            self.assertFalse(id_columns[0]['is_foreign_key'])
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationship detection using DURC test files."""
        existing_files = [str(f) for f in self.test_sql_files if f.exists()]
        
        if not existing_files:
            self.skipTest("No DURC test SQL files found")
        
        tables, sections = SQLParser.parse_sql_files(existing_files)
        
        # Test author_book table relationships if it exists
        if 'author_book' in tables:
            author_book_table = tables['author_book']
            
            # Should have foreign keys to author and book
            author_id_cols = [col for col in author_book_table['columns'] if col['column_name'] == 'author_id']
            book_id_cols = [col for col in author_book_table['columns'] if col['column_name'] == 'book_id']
            
            if author_id_cols:
                self.assertTrue(author_id_cols[0]['is_foreign_key'])
                self.assertEqual(author_id_cols[0]['foreign_table'], 'author')
            
            if book_id_cols:
                self.assertTrue(book_id_cols[0]['is_foreign_key'])
                self.assertEqual(book_id_cols[0]['foreign_table'], 'book')


class TestMermaidGenerator(unittest.TestCase):
    """Test cases for Mermaid diagram generation."""
    
    def test_generate_simple_diagram(self):
        """Test generating a simple diagram without sections."""
        tables = {
            'user': {
                'table_name': 'user',
                'columns': [
                    {'column_name': 'id', 'data_type': 'SERIAL', 'is_foreign_key': False, 'foreign_table': None},
                    {'column_name': 'username', 'data_type': 'varchar(50)', 'is_foreign_key': False, 'foreign_table': None}
                ]
            }
        }
        sections = {}
        
        diagram = MermaidGenerator.generate_diagram(tables, sections)
        
        self.assertIn('flowchart TD', diagram)
        self.assertIn('user[', diagram)
        self.assertIn('<b>user</b>', diagram)
        self.assertIn('font-size: 16px', diagram)  # Table name formatting
        self.assertIn('font-size: 12px', diagram)  # Column formatting
        self.assertIn('text-align: left;">id', diagram)  # Left-aligned column name
        self.assertIn('text-align: right;">SERIAL', diagram)  # Right-aligned data type
        self.assertIn('text-align: right;">varchar(50)', diagram)
    
    def test_generate_diagram_with_sections(self):
        """Test generating a diagram with sections."""
        tables = {
            'user': {
                'table_name': 'user',
                'columns': [
                    {'column_name': 'id', 'data_type': 'SERIAL', 'is_foreign_key': False, 'foreign_table': None}
                ]
            },
            'post': {
                'table_name': 'post',
                'columns': [
                    {'column_name': 'id', 'data_type': 'SERIAL', 'is_foreign_key': False, 'foreign_table': None},
                    {'column_name': 'user_id', 'data_type': 'integer', 'is_foreign_key': True, 'foreign_table': 'user'}
                ]
            }
        }
        sections = {
            'user': 'User Management',
            'post': 'Content Management'
        }
        
        diagram = MermaidGenerator.generate_diagram(tables, sections)
        
        # Check for formatted section labels with HTML styling
        self.assertIn('font-size: 20px; font-weight: bold;">User Management', diagram)
        self.assertIn('font-size: 20px; font-weight: bold;">Content Management', diagram)
        self.assertIn('post --> user', diagram)
        self.assertIn('text-align: right;">integer (FK)', diagram)  # Formatted FK column


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, 'output')
        os.makedirs(self.output_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_end_to_end_workflow(self):
        """Test the complete workflow from SQL files to markdown output."""
        # Create test SQL files
        sql1_content = """
        -- Diagram Section: User Management
        CREATE TABLE user (
            id SERIAL PRIMARY KEY,
            username varchar(50) NOT NULL,
            email varchar(100) NOT NULL,
            created_at timestamp DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Diagram Section: User Management
        CREATE TABLE user_profile (
            id SERIAL PRIMARY KEY,
            user_id integer NOT NULL,
            first_name varchar(50),
            last_name varchar(50),
            bio text
        );
        """
        
        sql2_content = """
        -- Diagram Section: Content Management
        CREATE TABLE post (
            id SERIAL PRIMARY KEY,
            user_id integer NOT NULL,
            title varchar(200) NOT NULL,
            content text NOT NULL,
            published_at timestamp
        );
        """
        
        sql1_file = os.path.join(self.test_dir, 'schema1.sql')
        sql2_file = os.path.join(self.test_dir, 'schema2.sql')
        
        with open(sql1_file, 'w') as f:
            f.write(sql1_content)
        with open(sql2_file, 'w') as f:
            f.write(sql2_content)
        
        # Parse SQL files
        tables, sections = SQLParser.parse_sql_files([sql1_file, sql2_file])
        
        # Verify parsing results
        self.assertEqual(len(tables), 3)
        self.assertEqual(len(sections), 3)
        
        # Generate diagram
        diagram = MermaidGenerator.generate_diagram(tables, sections)
        
        # Verify diagram content
        self.assertIn('flowchart TD', diagram)
        self.assertIn('User Management', diagram)
        self.assertIn('Content Management', diagram)
        self.assertIn('user_profile --> user', diagram)
        self.assertIn('post --> user', diagram)
        
        # Test markdown file generation
        output_file = os.path.join(self.output_dir, 'test_diagram.md')
        with open(output_file, 'w') as f:
            f.write("# Database Schema Diagram\n\n")
            f.write("```mermaid\n")
            f.write(diagram)
            f.write("\n```\n\n")
            f.write("## Source Files\n\n")
            f.write("1. [schema1.sql](schema1.sql)\n")
            f.write("2. [schema2.sql](schema2.sql)\n")
        
        # Verify file was created and has expected content
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn('# Database Schema Diagram', content)
            self.assertIn('```mermaid', content)
            self.assertIn('## Source Files', content)


def run_diagram_tests():
    """Run all diagram generator tests and generate test outputs."""
    # Create test output directory
    test_output_dir = Path(__file__).parent / 'diagram_output_tests'
    test_output_dir.mkdir(exist_ok=True)
    
    # Run the test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate test diagrams using the actual test SQL files
    project_root = Path(__file__).parent.parent
    durc_diagram_path = project_root / 'durc_diagram.py'
    
    if durc_diagram_path.exists():
        # Test with the provided SQL files
        test_sql_files = [
            project_root / 'AI_Instructions' / 'durc_postgres_test_files' / 'DURC_aaa.postgres.sql',
            project_root / 'AI_Instructions' / 'durc_postgres_test_files' / 'DURC_bbb.postgres.sql'
        ]
        
        existing_files = [f for f in test_sql_files if f.exists()]
        
        if existing_files:
            import subprocess
            
            # Generate test diagram
            output_file = test_output_dir / 'test_durc_database_diagram.md'
            cmd = [
                'python3', str(durc_diagram_path),
                '--sql_files'] + [str(f) for f in existing_files] + [
                '--output_md_file', str(output_file)
            ]
            
            try:
                subprocess.run(cmd, check=True, cwd=str(project_root))
                print(f"\nTest diagram generated: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error generating test diagram: {e}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_diagram_tests()
    sys.exit(0 if success else 1)
