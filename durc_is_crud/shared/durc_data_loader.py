import json
import os


class DurcDataLoader:
    """
    Shared data loader for DURC JSON files.
    
    This class provides a thin layer on top of JSON file loading that can be used
    by both Django management commands (like durc_compile) and standalone CLI tools
    (like durc-mine-fkeys).
    
    For now, this should simply return a dictionary in the same structure as loading
    the JSON directly would. In the future, it may have extra functionality that is
    useful to both Django and non-Django scripts.
    """
    
    def load_relational_model(self, json_file_path: str) -> dict:
        """
        Load and return the DURC relational model from JSON file.
        
        Args:
            json_file_path (str): Path to the JSON file containing the relational model
            
        Returns:
            dict: The loaded relational model data
            
        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
            Exception: For other file reading errors
        """
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"Input file {json_file_path} does not exist")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                relational_model = json.load(f)
            return relational_model
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to parse {json_file_path} as JSON: {e}", e.doc, e.pos)
        except Exception as e:
            raise Exception(f"Error reading {json_file_path}: {e}")
