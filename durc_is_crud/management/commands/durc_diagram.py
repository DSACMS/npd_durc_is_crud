import os
from django.core.management.base import BaseCommand, CommandError
from .durc_utils.sql_parser import DURC_SQLParser
from .durc_utils.diagram_section_parser import DURC_DiagramSectionParser
from .durc_utils.mermaid_generator import DURC_MermaidGenerator

class Command(BaseCommand):
    help = 'Generate Mermaid diagrams from CREATE TABLE SQL statements'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sql_files',
            nargs='+',
            type=str,
            required=True,
            help='List of SQL files to parse for CREATE TABLE statements'
        )
        parser.add_argument(
            '--output_md_file',
            type=str,
            required=True,
            help='Output markdown file path for the generated diagram'
        )

    def handle(self, *args, **options):
        sql_files = options.get('sql_files', [])
        output_md_file = options.get('output_md_file')
        
        if not sql_files:
            raise CommandError("You must specify at least one SQL file using --sql_files")
        
        if not output_md_file:
            raise CommandError("You must specify an output markdown file using --output_md_file")
        
        # Validate that all SQL files exist and have .sql extension
        for sql_file in sql_files:
            if not os.path.exists(sql_file):
                raise CommandError(f"SQL file not found: {sql_file}")
            if not sql_file.lower().endswith('.sql'):
                raise CommandError(f"File must have .sql extension: {sql_file}")
        
        self.stdout.write(f"Processing {len(sql_files)} SQL file(s)...")
        
        # Parse SQL files to extract table information
        all_tables = {}
        all_sections = {}
        
        for sql_file in sql_files:
            self.stdout.write(f"Parsing {sql_file}...")
            
            # Parse the SQL file
            tables, sections = DURC_SQLParser.parse_sql_file(
                sql_file, 
                self.stdout.write,
                self.style
            )
            
            # Merge tables and sections
            all_tables.update(tables)
            all_sections.update(sections)
            
            self.stdout.write(f"Found {len(tables)} tables in {sql_file}")
        
        # Process diagram sections
        section_assignments = DURC_DiagramSectionParser.assign_tables_to_sections(
            all_tables, 
            all_sections,
            self.stdout.write,
            self.style
        )
        
        # Generate Mermaid diagram
        mermaid_content = DURC_MermaidGenerator.generate_diagram(
            all_tables,
            section_assignments,
            self.stdout.write,
            self.style
        )
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_md_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write the markdown file
        with open(output_md_file, 'w') as f:
            f.write("# Database Schema Diagram\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_content)
            f.write("\n```\n")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully generated diagram at {output_md_file}")
        )
        self.stdout.write(f"Total tables processed: {len(all_tables)}")
        self.stdout.write(f"Diagram sections found: {len(all_sections)}")
