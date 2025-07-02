#!/usr/bin/env python3
"""
Test script for durc_mine_fkeys command
"""
import sys
import os
import json
from datetime import datetime

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock Django components for testing
class MockStyle:
    def SUCCESS(self, text):
        return f"✓ {text}"
    
    def ERROR(self, text):
        return f"✗ {text}"
    
    def WARNING(self, text):
        return f"⚠ {text}"

class MockStdout:
    def write(self, text):
        print(text)

class MockCommand:
    def __init__(self):
        self.stdout = MockStdout()
        self.style = MockStyle()

# Import our command
from durc_is_crud.management.commands.durc_mine_fkeys import Command

def test_durc_mine_fkeys():
    """Test the durc_mine_fkeys command functionality"""
    print("Testing durc_mine_fkeys command...")
    
    # Create command instance
    command = Command()
    command.stdout = MockStdout()
    command.style = MockStyle()
    
    # Test options
    options = {
        'include': ['blog_db'],
        'input_json_file': 'durc_config/DURC_relational_model.json',
        'output_sql_file': 'durc_config/test_foreign_keys.sql'
    }
    
    try:
        # Test the main functionality
        print("\n1. Testing include pattern parsing...")
        from durc_is_crud.management.commands.durc_utils.include_pattern_parser import DURC_IncludePatternParser
        patterns = DURC_IncludePatternParser.parse_include_patterns(['blog_db'])
        print(f"Parsed patterns: {patterns}")
        
        print("\n2. Testing JSON loading...")
        with open('durc_config/DURC_relational_model.json', 'r') as f:
            relational_model = json.load(f)
        print(f"Loaded model with databases: {list(relational_model.keys())}")
        
        print("\n3. Testing foreign key generation...")
        foreign_key_statements = command._generate_foreign_key_statements(
            relational_model, patterns, ['blog_db']
        )
        print(f"Generated {len(foreign_key_statements)} foreign key statements:")
        for stmt in foreign_key_statements:
            print(f"  {stmt}")
        
        print("\n4. Testing SQL file writing...")
        command._write_sql_file('durc_config/test_foreign_keys.sql', foreign_key_statements, ['blog_db'])
        print("SQL file written successfully!")
        
        print("\n5. Reading generated SQL file...")
        with open('durc_config/test_foreign_keys.sql', 'r') as f:
            sql_content = f.read()
        print("Generated SQL content:")
        print("-" * 50)
        print(sql_content)
        print("-" * 50)
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_durc_mine_fkeys()
    sys.exit(0 if success else 1)
