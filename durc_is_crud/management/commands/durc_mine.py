import os
import json
from django.core.management.base import BaseCommand, CommandError
from .durc_utils.include_pattern_parser import DURC_IncludePatternParser
from .durc_utils.relational_model_extractor import DURC_RelationalModelExtractor

class Command(BaseCommand):
    help = 'Mine database schema and generate DURC relational model JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--include',
            nargs='+',
            type=str,
            help='Specify databases, schemas, or tables to include in the format: db.schema.table, db.schema, or db'
        )
        parser.add_argument(
            '--output_json_file',
            type=str,
            help='Specify a custom output path for the JSON file (default: durc_config/DURC_relational_model.json)'
        )

    def handle(self, *args, **options):
        include_patterns = options.get('include', [])
        
        if not include_patterns:
            raise CommandError("You must specify at least one database, schema, or table to include using --include")
        
        # Parse the include patterns
        db_schema_table_patterns = DURC_IncludePatternParser.parse_include_patterns(include_patterns)
        
        # Extract the relational model
        relational_model = DURC_RelationalModelExtractor.extract_relational_model(
            db_schema_table_patterns, 
            self.stdout.write,
            self.style
        )
        
        # Determine the output path
        output_path = options.get('output_json_file')
        if not output_path:
            # Use the default path
            os.makedirs('durc_config', exist_ok=True)
            output_path = os.path.join('durc_config', 'DURC_relational_model.json')
        else:
            # Ensure the directory for the custom output path exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
        
        # Write the relational model to JSON file
        with open(output_path, 'w') as f:
            json.dump(relational_model, f, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully generated DURC relational model at {output_path}"))
