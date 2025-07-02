#!/usr/bin/env python3
"""
DURC Diagram Generator

A standalone Python script that generates Mermaid diagrams from CREATE TABLE SQL statements.
This script is not dependent on Django and can be run independently.
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Tuple, Optional


class SQLParser:
    """Parser for SQL CREATE TABLE statements and diagram section comments."""
    
    @staticmethod
    def parse_sql_files(sql_files: List[str]) -> Tuple[Dict, Dict]:
        """
        Parse multiple SQL files and extract table information and sections.
        
        Args:
            sql_files: List of SQL file paths
            
        Returns:
            Tuple of (tables_dict, sections_dict)
        """
        all_tables = {}
        all_sections = {}
        
        for sql_file in sql_files:
            print(f"Parsing {sql_file}...")
            tables, sections = SQLParser._parse_single_file(sql_file)
            all_tables.update(tables)
            all_sections.update(sections)
            print(f"Found {len(tables)} tables in {sql_file}")
        
        return all_tables, all_sections
    
    @staticmethod
    def _parse_single_file(sql_file_path: str) -> Tuple[Dict, Dict]:
        """Parse a single SQL file."""
        tables = {}
        sections = {}
        
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Look for diagram section comments
                if line.startswith('--') and ':' in line:
                    section_info = SQLParser._parse_diagram_section_comment(line)
                    if section_info:
                        # Look ahead to find the next CREATE TABLE statement
                        table_name = SQLParser._find_next_create_table(lines, i)
                        if table_name:
                            sections[table_name] = section_info
                            print(f"Found diagram section '{section_info}' for table '{table_name}'")
                
                # Look for CREATE TABLE statements
                if line.upper().startswith('CREATE TABLE'):
                    table_info = SQLParser._parse_create_table_statement(lines, i)
                    if table_info:
                        table_name = table_info['table_name']
                        tables[table_name] = table_info
                        print(f"Parsed table: {table_name}")
                
                i += 1
                
        except Exception as e:
            print(f"Error parsing SQL file {sql_file_path}: {e}")
            
        return tables, sections
    
    @staticmethod
    def _parse_diagram_section_comment(comment_line: str) -> Optional[str]:
        """Parse a comment line to extract diagram section information."""
        # Remove leading -- and whitespace
        comment_content = comment_line.lstrip('- ').strip()
        
        if ':' not in comment_content:
            return None
        
        # Split on first colon
        parts = comment_content.split(':', 1)
        if len(parts) != 2:
            return None
        
        label = parts[0].strip()
        section_name = parts[1].strip()
        
        # Check if label matches "diagram section" (case and whitespace insensitive)
        normalized_label = re.sub(r'\s+', '', label.lower())
        if normalized_label == 'diagramsection':
            return section_name
        
        return None
    
    @staticmethod
    def _find_next_create_table(lines: List[str], start_index: int) -> Optional[str]:
        """Find the next CREATE TABLE statement after the given index."""
        for i in range(start_index + 1, len(lines)):
            line = lines[i].strip()
            if line.upper().startswith('CREATE TABLE'):
                # Extract table name - handle quoted names with spaces
                match = re.search(r'CREATE TABLE\s+(?:"([^"]+)"|(\w+))', line, re.IGNORECASE)
                if match:
                    table_name = match.group(1) or match.group(2)
                    # Skip tables that start with underscore or contain "ignore" (case insensitive)
                    if table_name.startswith('_') or 'ignore' in table_name.lower():
                        continue
                    return table_name
        return None
    
    @staticmethod
    def _parse_create_table_statement(lines: List[str], start_index: int) -> Optional[Dict]:
        """Parse a CREATE TABLE statement and extract table information."""
        # Find the table name
        create_line = lines[start_index].strip()
        match = re.search(r'CREATE TABLE\s+(?:"([^"]+)"|(\w+))', create_line, re.IGNORECASE)
        if not match:
            return None
        
        table_name = match.group(1) or match.group(2)
        
        # Skip tables that start with underscore (DURC convention) or contain "ignore"
        if table_name.startswith('_') or 'ignore' in table_name.lower():
            return None
        
        # Find the opening parenthesis
        i = start_index
        while i < len(lines) and '(' not in lines[i]:
            i += 1
        
        if i >= len(lines):
            return None
        
        # Collect all lines until we find the closing parenthesis
        table_lines = []
        paren_count = 0
        found_opening = False
        
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('--'):
                i += 1
                continue
            
            # Count parentheses to find the end of the CREATE TABLE statement
            paren_count += line.count('(')
            paren_count -= line.count(')')
            
            if '(' in line:
                found_opening = True
            
            if found_opening:
                table_lines.append(line)
            
            if found_opening and paren_count == 0:
                break
            
            i += 1
        
        # Parse the columns
        columns = SQLParser._parse_columns(table_lines, table_name)
        
        return {
            'table_name': table_name,
            'columns': columns
        }
    
    @staticmethod
    def _parse_columns(table_lines: List[str], table_name: str) -> List[Dict]:
        """Parse column definitions from CREATE TABLE statement."""
        columns = []
        
        # Join all lines and split by commas, but be careful about commas in constraints
        full_text = ' '.join(table_lines)
        
        # Remove the CREATE TABLE part and outer parentheses
        # Find the content between the first ( and last )
        start_paren = full_text.find('(')
        end_paren = full_text.rfind(')')
        
        if start_paren == -1 or end_paren == -1:
            return columns
        
        content = full_text[start_paren + 1:end_paren].strip()
        
        # Split by commas, but be careful about nested parentheses
        parts = []
        current_part = ""
        paren_depth = 0
        
        for char in content:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                parts.append(current_part.strip())
                current_part = ""
                continue
            
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Parse each part
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Skip constraints like PRIMARY KEY, FOREIGN KEY, UNIQUE, etc.
            if (part.upper().startswith('PRIMARY KEY') or 
                part.upper().startswith('FOREIGN KEY') or
                part.upper().startswith('CONSTRAINT') or
                part.upper().startswith('INDEX') or
                part.upper().startswith('KEY') or
                part.upper().startswith('UNIQUE')):
                continue
            
            # Parse column definition
            column_info = SQLParser._parse_column_definition(part, table_name)
            if column_info:
                columns.append(column_info)
        
        return columns
    
    @staticmethod
    def _parse_column_definition(column_def: str, table_name: str) -> Optional[Dict]:
        """Parse a single column definition."""
        # Basic pattern: column_name data_type [constraints]
        parts = column_def.split()
        if len(parts) < 2:
            return None
        
        column_name = parts[0].strip('"')
        data_type = parts[1]
        
        # Skip columns that start with underscore
        if column_name.startswith('_'):
            return None
        
        # Determine if this is a foreign key based on DURC naming convention
        is_foreign_key = column_name.endswith('_id')
        foreign_table = None
        
        if is_foreign_key:
            # Try to infer the foreign table name
            potential_table = column_name[:-3]  # Remove _id
            
            # Handle pattern-based relationships (prefix_table_id)
            if '_' in potential_table:
                # Take the last part as the table name
                foreign_table = potential_table.split('_')[-1]
            else:
                foreign_table = potential_table
        
        return {
            'column_name': column_name,
            'data_type': data_type,
            'is_foreign_key': is_foreign_key,
            'foreign_table': foreign_table
        }


class MermaidGenerator:
    """Generator for Mermaid flowchart diagrams with styled sections."""
    
    # Light pastel colors for tables
    PASTEL_COLORS = [
        '#FFE5E5',  # Light pink
        '#E5F3FF',  # Light blue
        '#E5FFE5',  # Light green
        '#FFF5E5',  # Light orange
        '#F0E5FF',  # Light purple
        '#FFFFE5',  # Light yellow
        '#E5FFFF',  # Light cyan
        '#FFE5F5',  # Light magenta
    ]
    
    # Darker versions for section backgrounds
    SECTION_COLORS = [
        '#FFB3B3',  # Darker pink
        '#B3D9FF',  # Darker blue
        '#B3FFB3',  # Darker green
        '#FFCCB3',  # Darker orange
        '#D9B3FF',  # Darker purple
        '#FFFFB3',  # Darker yellow
        '#B3FFFF',  # Darker cyan
        '#FFB3E5',  # Darker magenta
    ]
    
    @staticmethod
    def generate_diagram(tables: Dict, sections: Dict) -> str:
        """Generate Mermaid flowchart diagram with styled sections."""
        lines = ['flowchart TD']
        
        # Group tables by section
        section_groups = {}
        unassigned_tables = []
        
        for table_name, table_info in tables.items():
            if table_name in sections:
                section_name = sections[table_name]
                # Normalize section name for grouping
                normalized_section = re.sub(r'\s+', ' ', section_name.strip())
                if normalized_section not in section_groups:
                    section_groups[normalized_section] = []
                section_groups[normalized_section].append((table_name, table_info))
            else:
                unassigned_tables.append((table_name, table_info))
        
        color_index = 0
        all_table_nodes = []
        
        # Generate sections with subgraphs
        for section_name, section_tables in section_groups.items():
            section_color = MermaidGenerator.SECTION_COLORS[color_index % len(MermaidGenerator.SECTION_COLORS)]
            table_color = MermaidGenerator.PASTEL_COLORS[color_index % len(MermaidGenerator.PASTEL_COLORS)]
            
            # Create subgraph for section with larger font size for section name
            section_id = f"section_{color_index}"
            # Section labels should be two sizes larger than table names (which are 16px), so 20px
            section_label = f'<span style="font-size: 20px; font-weight: bold;">{section_name}</span>'
            lines.append(f'    subgraph {section_id}["{section_label}"]')
            
            # Generate tables in this section
            for table_name, table_info in section_tables:
                table_content = MermaidGenerator._generate_table_content(table_info)
                lines.append(f'        {table_name}["{table_content}"]')
                all_table_nodes.append(table_name)
            
            lines.append('    end')
            
            # Add styling for the subgraph
            lines.append(f'    style {section_id} fill:{section_color},stroke:#333,stroke-width:2px,color:#000')
            
            # Add styling for tables in this section
            for table_name, table_info in section_tables:
                lines.append(f'    style {table_name} fill:{table_color},stroke:#333,stroke-width:1px,color:#000')
            
            color_index += 1
        
        # Generate unassigned tables
        if unassigned_tables:
            table_color = MermaidGenerator.PASTEL_COLORS[color_index % len(MermaidGenerator.PASTEL_COLORS)]
            
            for table_name, table_info in unassigned_tables:
                table_content = MermaidGenerator._generate_table_content(table_info)
                lines.append(f'    {table_name}["{table_content}"]')
                lines.append(f'    style {table_name} fill:{table_color},stroke:#333,stroke-width:1px,color:#000')
                all_table_nodes.append(table_name)
        
        # Generate relationships
        for table_name, table_info in tables.items():
            for column in table_info['columns']:
                if column['is_foreign_key'] and column['foreign_table']:
                    # Check if the foreign table exists in our tables
                    if column['foreign_table'] in tables:
                        lines.append(f'    {table_name} --> {column["foreign_table"]}')
        
        return '\n'.join(lines)
    
    @staticmethod
    def _generate_table_content(table_info: Dict) -> str:
        """Generate table content for display in flowchart node with proper formatting."""
        table_name = table_info['table_name']
        columns = table_info['columns']
        
        # Create table header with larger font size (two sizes larger than column text)
        content_lines = [f'<span style="font-size: 16px;"><b>{table_name}</b></span>', "---"]
        
        # Add columns with left-aligned names and right-aligned types
        for column in columns:
            data_type = column['data_type']
            column_name = column['column_name']
            
            # Create a table-like structure with left and right alignment
            if column['is_foreign_key']:
                # Use a span with flex-like behavior for alignment
                column_line = f'<div style="display: flex; justify-content: space-between; font-size: 12px;"><span style="text-align: left;">{column_name}</span><span style="text-align: right;">{data_type} (FK)</span></div>'
            else:
                column_line = f'<div style="display: flex; justify-content: space-between; font-size: 12px;"><span style="text-align: left;">{column_name}</span><span style="text-align: right;">{data_type}</span></div>'
            
            content_lines.append(column_line)
        
        # Join with HTML line breaks for proper display
        return "<br/>".join(content_lines)


def main():
    """Main function to run the DURC diagram generator."""
    parser = argparse.ArgumentParser(
        description='Generate Mermaid diagrams from CREATE TABLE SQL statements'
    )
    parser.add_argument(
        '--sql_files',
        nargs='+',
        required=True,
        help='List of SQL files to parse for CREATE TABLE statements'
    )
    parser.add_argument(
        '--output_md_file',
        required=True,
        help='Output markdown file path for the generated diagram'
    )
    
    args = parser.parse_args()
    
    # Validate SQL files
    for sql_file in args.sql_files:
        if not os.path.exists(sql_file):
            print(f"Error: SQL file not found: {sql_file}")
            sys.exit(1)
        if not sql_file.lower().endswith('.sql'):
            print(f"Error: File must have .sql extension: {sql_file}")
            sys.exit(1)
    
    print(f"Processing {len(args.sql_files)} SQL file(s)...")
    
    # Parse SQL files
    tables, sections = SQLParser.parse_sql_files(args.sql_files)
    
    if not tables:
        print("No tables found in the provided SQL files.")
        sys.exit(1)
    
    # Generate Mermaid diagram
    print("Generating Mermaid diagram...")
    mermaid_content = MermaidGenerator.generate_diagram(tables, sections)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output_md_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Write markdown file
    with open(args.output_md_file, 'w', encoding='utf-8') as f:
        f.write("# Database Schema Diagram\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_content)
        f.write("\n```\n\n")
        
        # Add source files list
        f.write("## Source Files\n\n")
        for i, sql_file in enumerate(args.sql_files, 1):
            f.write(f"{i}. [{os.path.basename(sql_file)}]({sql_file})\n")
    
    print(f"Successfully generated diagram at {args.output_md_file}")
    print(f"Total tables processed: {len(tables)}")
    print(f"Diagram sections found: {len(sections)}")


if __name__ == '__main__':
    main()
