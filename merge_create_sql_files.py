#!/usr/bin/env python3
"""
Merge CREATE TABLE SQL statements from multiple SQL files into a single file.

This script recursively searches for .sql files in the specified directory and subdirectories,
extracts CREATE TABLE statements, and merges them into a single _merged_.sql file.
It ignores any existing _merged_.sql files to avoid including previous runs.
"""

import os
import re
import glob
import argparse
from datetime import datetime
from pathlib import Path


class SQLMerger:
    OUTPUT_FILENAME = "_merged_.sql"
    
    @staticmethod
    def find_sql_files(directory="."):
        """
        Recursively find all .sql files, excluding any existing _merged_.sql files.
        """
        sql_files = []
        
        # Use glob to find all .sql files recursively
        pattern = os.path.join(directory, "**", "*.sql")
        all_sql_files = glob.glob(pattern, recursive=True)
        
        # Filter out _merged_.sql files
        for file_path in all_sql_files:
            if not os.path.basename(file_path) == SQLMerger.OUTPUT_FILENAME:
                sql_files.append(file_path)
        
        return sorted(sql_files)
    
    @staticmethod
    def extract_create_table_statements(file_path):
        """
        Extract CREATE TABLE statements from a SQL file.
        Handles multi-line statements and various SQL formats.
        """
        statements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
            except Exception as e:
                print(f"Warning: Could not read file {file_path}: {e}")
                return statements
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {e}")
            return statements
        
        # Split content into lines for processing
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for CREATE TABLE statements (case insensitive)
            if re.match(r'^\s*CREATE\s+TABLE\s+', line, re.IGNORECASE):
                # Found start of CREATE TABLE statement
                statement_lines = [lines[i]]
                i += 1
                
                # Count parentheses to find the end of the statement
                paren_count = line.count('(') - line.count(')')
                
                # Continue reading lines until we have balanced parentheses
                while i < len(lines) and paren_count > 0:
                    current_line = lines[i]
                    statement_lines.append(current_line)
                    paren_count += current_line.count('(') - current_line.count(')')
                    i += 1
                
                # Join the statement lines
                full_statement = '\n'.join(statement_lines)
                
                # Clean up the statement (remove extra whitespace, ensure it ends with semicolon)
                full_statement = full_statement.strip()
                if not full_statement.endswith(';'):
                    full_statement += ';'
                
                statements.append(full_statement)
            else:
                i += 1
        
        return statements
    
    @staticmethod
    def process_files(directory="."):
        """
        Process all SQL files and extract CREATE TABLE statements.
        Returns tuple of (processed_files, create_table_statements)
        """
        sql_files = SQLMerger.find_sql_files(directory)
        processed_files = []
        create_table_statements = []
        
        if not sql_files:
            print("No SQL files found.")
            return processed_files, create_table_statements
        
        print(f"Found {len(sql_files)} SQL files to process:")
        
        for file_path in sql_files:
            print(f"  Processing: {file_path}")
            statements = SQLMerger.extract_create_table_statements(file_path)
            
            if statements:
                processed_files.append(file_path)
                for statement in statements:
                    create_table_statements.append({
                        'file': file_path,
                        'statement': statement
                    })
                print(f"    Found {len(statements)} CREATE TABLE statement(s)")
            else:
                print(f"    No CREATE TABLE statements found")
        
        return processed_files, create_table_statements
    
    @staticmethod
    def generate_merged_file(processed_files, create_table_statements, directory="."):
        """
        Generate the merged SQL file with all CREATE TABLE statements.
        """
        if not create_table_statements:
            print("No CREATE TABLE statements found to merge.")
            return
        
        # Generate header with list of source files
        header = [
            "-- Merged CREATE TABLE statements",
            f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- Total CREATE TABLE statements: {len(create_table_statements)}",
            "--",
            "-- Source files:",
        ]
        
        # Add each source file as a separate comment line
        for file_path in processed_files:
            header.append(f"--   {file_path}")
        
        header.extend(["", ""])  # Add blank lines after header
        
        # Build the content
        content_lines = header.copy()
        
        # Add all CREATE TABLE statements without file separators
        for item in create_table_statements:
            statement = item['statement']
            content_lines.append(statement)
            content_lines.append("")  # Add blank line after each statement
        
        # Create output file path in the specified directory
        output_path = os.path.join(directory, SQLMerger.OUTPUT_FILENAME)
        
        # Write to output file
        try:
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write('\n'.join(content_lines))
            
            print(f"\nSuccessfully created {output_path}")
            print(f"Merged {len(create_table_statements)} CREATE TABLE statements from {len(processed_files)} files")
            
        except Exception as e:
            print(f"Error writing output file: {e}")
    
    @staticmethod
    def run(directory="."):
        """
        Main execution method.
        """
        print("SQL CREATE TABLE Merger")
        print("=" * 50)
        print(f"Working directory: {os.path.abspath(directory)}")
        
        # Check if output file already exists and warn user
        output_path = os.path.join(directory, SQLMerger.OUTPUT_FILENAME)
        if os.path.exists(output_path):
            print(f"Warning: {output_path} already exists and will be overwritten.")
        
        processed_files, create_table_statements = SQLMerger.process_files(directory)
        SQLMerger.generate_merged_file(processed_files, create_table_statements, directory)


def main():
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(
        description="Merge CREATE TABLE SQL statements from multiple SQL files into a single file."
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Directory to search for SQL files and where to output the merged file"
    )
    
    args = parser.parse_args()
    
    # Validate directory exists
    if not os.path.isdir(args.dir):
        print(f"Error: Directory '{args.dir}' does not exist.")
        return 1
    
    SQLMerger.run(args.dir)
    return 0


if __name__ == "__main__":
    exit(main())
