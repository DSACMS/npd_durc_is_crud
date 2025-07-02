#!/usr/bin/env python3
"""
DURC Diagram Generator - Graphviz Implementation

A standalone Python script that generates Graphviz diagrams from CREATE TABLE SQL statements.
This implementation uses sqlglot for SQL parsing and Python's graphviz library for diagram generation.
This script is not dependent on Django and can be run independently.
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Tuple, Optional, Set
import sqlglot
from sqlglot import expressions as exp
import graphviz


class SQLGlotParser:
    """Parser for SQL CREATE TABLE statements using sqlglot library."""
    
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
            tables, sections = SQLGlotParser._parse_single_file(sql_file)
            all_tables.update(tables)
            all_sections.update(sections)
            print(f"Found {len(tables)} tables in {sql_file}")
        
        return all_tables, all_sections
    
    @staticmethod
    def _parse_single_file(sql_file_path: str) -> Tuple[Dict, Dict]:
        """Parse a single SQL file using sqlglot."""
        tables = {}
        sections = {}
        
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split content into lines for comment processing
            lines = content.split('\n')
            
            # First pass: find diagram section comments and associate with tables
            section_comments = SQLGlotParser._extract_section_comments(lines)
            
            # Parse SQL statements using sqlglot
            try:
                statements = sqlglot.parse(content, dialect='postgres')
            except Exception as e:
                print(f"Warning: sqlglot parsing failed for {sql_file_path}, trying line-by-line: {e}")
                statements = SQLGlotParser._parse_statements_individually(content)
            
            print(f"Found {len(statements)} statements to process")
            for i, statement in enumerate(statements):
                print(f"Statement {i}: {type(statement)} - {getattr(statement, 'kind', 'no kind')}")
                if isinstance(statement, exp.Create) and statement.kind == "TABLE":
                    table_info = SQLGlotParser._extract_table_info(statement)
                    if table_info:
                        table_name = table_info['table_name']
                        tables[table_name] = table_info
                        
                        # Check if this table has a section comment
                        if table_name in section_comments:
                            sections[table_name] = section_comments[table_name]
                            print(f"Found diagram section '{section_comments[table_name]}' for table '{table_name}'")
                        
                        print(f"Parsed table: {table_name}")
                    else:
                        print(f"Skipped table (filtered out or parsing failed)")
                        
        except Exception as e:
            print(f"Error parsing SQL file {sql_file_path}: {e}")
            
        return tables, sections
    
    @staticmethod
    def _parse_statements_individually(content: str) -> List:
        """Parse SQL statements one by one when bulk parsing fails."""
        statements = []
        
        # Split by semicolons and try to parse each statement
        raw_statements = content.split(';')
        
        for raw_stmt in raw_statements:
            raw_stmt = raw_stmt.strip()
            if not raw_stmt:
                continue
                
            # Only try to parse CREATE TABLE statements
            if raw_stmt.upper().startswith('CREATE TABLE'):
                try:
                    parsed = sqlglot.parse_one(raw_stmt + ';', dialect='postgres')
                    if parsed:
                        statements.append(parsed)
                except Exception as e:
                    print(f"Warning: Could not parse statement: {raw_stmt[:50]}... Error: {e}")
                    continue
        
        return statements
    
    @staticmethod
    def _extract_section_comments(lines: List[str]) -> Dict[str, str]:
        """Extract diagram section comments and associate them with table names."""
        section_comments = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for diagram section comments
            if line.startswith('--') and ':' in line:
                section_info = SQLGlotParser._parse_diagram_section_comment(line)
                if section_info:
                    # Look ahead to find the next CREATE TABLE statement
                    table_name = SQLGlotParser._find_next_create_table(lines, i)
                    if table_name:
                        section_comments[table_name] = section_info
        
        return section_comments
    
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
    def _extract_table_info(create_statement: exp.Create) -> Optional[Dict]:
        """Extract table information from a sqlglot CREATE TABLE statement."""
        if not create_statement.this:
            print("No 'this' attribute in CREATE statement")
            return None
        
        # Get table name - handle different ways sqlglot might store the name
        if hasattr(create_statement.this, 'name'):
            table_name = create_statement.this.name
        elif hasattr(create_statement.this, 'this') and hasattr(create_statement.this.this, 'name'):
            table_name = create_statement.this.this.name
        else:
            table_name = str(create_statement.this)
        
        # Clean up the table name (remove quotes if present)
        if table_name.startswith('"') and table_name.endswith('"'):
            table_name = table_name[1:-1]
        
        print(f"Extracting info for table: '{table_name}'")
        
        # Skip tables that start with underscore (DURC convention) or contain "ignore"
        if table_name.startswith('_') or 'ignore' in table_name.lower():
            print(f"Skipping table '{table_name}' (underscore or ignore)")
            return None
        
        # Extract columns
        columns = []
        if hasattr(create_statement, 'expressions') and create_statement.expressions:
            print(f"Found {len(create_statement.expressions)} expressions for table '{table_name}'")
            for expr in create_statement.expressions:
                print(f"Expression type: {type(expr)}")
                if isinstance(expr, exp.ColumnDef):
                    column_info = SQLGlotParser._extract_column_info(expr, table_name)
                    if column_info:
                        columns.append(column_info)
                        print(f"Added column: {column_info['column_name']}")
        else:
            print(f"No expressions found for table '{table_name}'")
        
        print(f"Table '{table_name}' has {len(columns)} columns")
        return {
            'table_name': table_name,
            'columns': columns
        }
    
    @staticmethod
    def _extract_column_info(column_def: exp.ColumnDef, table_name: str) -> Optional[Dict]:
        """Extract column information from a sqlglot ColumnDef expression."""
        column_name = column_def.this.name
        
        # Skip columns that start with underscore
        if column_name.startswith('_'):
            return None
        
        # Get data type
        data_type = str(column_def.kind) if column_def.kind else 'UNKNOWN'
        
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


class GraphvizDiagramGenerator:
    """Generator for Graphviz diagrams with HTML table styling."""
    
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
    def generate_diagram(tables: Dict, sections: Dict, output_format: str = 'svg') -> graphviz.Digraph:
        """Generate Graphviz diagram with HTML table styling and sections."""
        
        # Create the main graph
        dot = graphviz.Digraph(comment='DURC Database Schema')
        dot.attr(rankdir='TB', bgcolor='white', pad='0.5')
        dot.attr('node', shape='plaintext', fontname='Arial')
        dot.attr('edge', fontname='Arial', fontsize='10')
        
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
        
        # Generate sections with subgraphs
        for section_name, section_tables in section_groups.items():
            section_color = GraphvizDiagramGenerator.SECTION_COLORS[color_index % len(GraphvizDiagramGenerator.SECTION_COLORS)]
            table_color = GraphvizDiagramGenerator.PASTEL_COLORS[color_index % len(GraphvizDiagramGenerator.PASTEL_COLORS)]
            
            # Create subgraph for section
            cluster_name = f'cluster_{color_index}'
            dot.attr('graph', label=section_name, style='filled', color='black', 
                    fillcolor=section_color, fontsize='20', fontname='Arial Bold',
                    labeljust='l', labelloc='t')
            
            # Add subgraph start
            dot.body.append(f'subgraph {cluster_name} {{')
            dot.body.append(f'label="{section_name}";')
            dot.body.append(f'style=filled;')
            dot.body.append(f'fillcolor="{section_color}";')
            dot.body.append(f'fontsize=20;')
            dot.body.append(f'fontname="Arial Bold";')
            dot.body.append(f'labeljust=l;')
            dot.body.append(f'labelloc=t;')
            
            # Generate tables in this section
            for table_name, table_info in section_tables:
                table_html = GraphvizDiagramGenerator._generate_table_html(table_info, table_color)
                dot.node(table_name, label=table_html)
            
            # Close subgraph
            dot.body.append('}')
            
            color_index += 1
        
        # Generate unassigned tables
        if unassigned_tables:
            table_color = GraphvizDiagramGenerator.PASTEL_COLORS[color_index % len(GraphvizDiagramGenerator.PASTEL_COLORS)]
            
            for table_name, table_info in unassigned_tables:
                table_html = GraphvizDiagramGenerator._generate_table_html(table_info, table_color)
                dot.node(table_name, label=table_html)
        
        # Generate relationships
        for table_name, table_info in tables.items():
            for column in table_info['columns']:
                if column['is_foreign_key'] and column['foreign_table']:
                    # Check if the foreign table exists in our tables
                    if column['foreign_table'] in tables:
                        dot.edge(table_name, column['foreign_table'], 
                               arrowhead='crow', arrowsize='0.8', color='#666666')
        
        return dot
    
    @staticmethod
    def _generate_table_html(table_info: Dict, table_color: str) -> str:
        """Generate HTML table content for Graphviz node."""
        table_name = table_info['table_name']
        columns = table_info['columns']
        
        # Ensure we have a valid table name
        if not table_name:
            table_name = "UNKNOWN"
        
        # Start HTML table with styling
        html_parts = [
            f'<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="{table_color}">',
            # Table header with larger font size
            f'<TR><TD COLSPAN="2" BGCOLOR="{table_color}"><FONT POINT-SIZE="16"><B>{table_name}</B></FONT></TD></TR>'
        ]
        
        # Add separator row
        html_parts.append(f'<TR><TD COLSPAN="2" HEIGHT="1" BGCOLOR="black"></TD></TR>')
        
        # Add columns - ensure we have at least one column
        if not columns:
            html_parts.append(
                f'<TR>'
                f'<TD ALIGN="LEFT"><FONT POINT-SIZE="12">No columns found</FONT></TD>'
                f'<TD ALIGN="RIGHT"><FONT POINT-SIZE="12">-</FONT></TD>'
                f'</TR>'
            )
        else:
            for column in columns:
                column_name = column.get('column_name', 'UNKNOWN')
                data_type = column.get('data_type', 'UNKNOWN')
                
                if column.get('is_foreign_key', False):
                    type_text = f"{data_type} (FK)"
                else:
                    type_text = data_type
                
                # Escape any problematic characters
                column_name = str(column_name).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                type_text = str(type_text).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                
                # Create row with left-aligned column name and right-aligned type
                html_parts.append(
                    f'<TR>'
                    f'<TD ALIGN="LEFT"><FONT POINT-SIZE="12">{column_name}</FONT></TD>'
                    f'<TD ALIGN="RIGHT"><FONT POINT-SIZE="12">{type_text}</FONT></TD>'
                    f'</TR>'
                )
        
        html_parts.append('</TABLE>')
        
        return '<' + ''.join(html_parts) + '>'


def main():
    """Main function to run the DURC diagram generator with Graphviz."""
    parser = argparse.ArgumentParser(
        description='Generate Graphviz diagrams from CREATE TABLE SQL statements using sqlglot'
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
    parser.add_argument(
        '--format',
        choices=['svg', 'png', 'pdf'],
        default='svg',
        help='Output format for the diagram (default: svg)'
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
    
    print(f"Processing {len(args.sql_files)} SQL file(s) with sqlglot...")
    
    # Parse SQL files
    tables, sections = SQLGlotParser.parse_sql_files(args.sql_files)
    
    if not tables:
        print("No tables found in the provided SQL files.")
        sys.exit(1)
    
    # Generate Graphviz diagram
    print("Generating Graphviz diagram...")
    dot = GraphvizDiagramGenerator.generate_diagram(tables, sections, args.format)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output_md_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Generate the diagram file
    base_name = os.path.splitext(args.output_md_file)[0]
    diagram_file = f"{base_name}_diagram.{args.format}"
    
    try:
        dot.render(base_name + '_diagram', format=args.format, cleanup=True)
        print(f"Diagram saved as: {diagram_file}")
    except Exception as e:
        print(f"Error generating diagram: {e}")
        print("Make sure Graphviz is installed on your system")
        sys.exit(1)
    
    # Write markdown file
    with open(args.output_md_file, 'w', encoding='utf-8') as f:
        f.write("# Database Schema Diagram (Graphviz Implementation)\n\n")
        
        # Embed the diagram based on format
        if args.format == 'svg':
            # For SVG, we can embed directly or link to it
            f.write(f"![Database Schema Diagram]({os.path.basename(diagram_file)})\n\n")
        else:
            f.write(f"![Database Schema Diagram]({os.path.basename(diagram_file)})\n\n")
        
        # Add source files list
        f.write("## Source Files\n\n")
        for i, sql_file in enumerate(args.sql_files, 1):
            f.write(f"{i}. [{os.path.basename(sql_file)}]({sql_file})\n")
        
        # Add implementation details
        f.write("\n## Implementation Details\n\n")
        f.write("This diagram was generated using:\n")
        f.write("- **SQL Parser**: sqlglot library for robust SQL parsing\n")
        f.write("- **Diagram Engine**: Python graphviz library with HTML table styling\n")
        f.write("- **Table Styling**: HTML tables with two columns (field name, field type)\n")
        f.write("- **Sections**: Grouped tables with colored backgrounds based on diagram section comments\n")
        f.write("- **Relationships**: Foreign key relationships shown as directed edges\n")
    
    print(f"Successfully generated markdown file at {args.output_md_file}")
    print(f"Total tables processed: {len(tables)}")
    print(f"Diagram sections found: {len(sections)}")


if __name__ == '__main__':
    main()
