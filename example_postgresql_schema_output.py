#!/usr/bin/env python3
"""
Example script demonstrating the PostgreSQL schema layer support in durc_mine.

This script shows how the durc_mine command now properly creates a schema layer
for PostgreSQL databases, resulting in the structure:
  database -> schema -> table

Instead of the previous MySQL-style structure:
  database -> table
"""

import json

# Example of MySQL output structure (2 layers: db -> table)
mysql_output = {
    "blog_db": {
        "users": {
            "table_name": "users",
            "db": "blog_db",
            "column_data": [
                {
                    "column_name": "id",
                    "data_type": "int",
                    "is_primary_key": True,
                    "is_foreign_key": False,
                    "is_linked_key": False,
                    "foreign_db": None,
                    "foreign_table": None,
                    "is_nullable": False,
                    "default_value": None,
                    "is_auto_increment": True
                }
            ],
            "create_table_sql": "CREATE TABLE blog_db.users (id INT AUTO_INCREMENT PRIMARY KEY)"
        }
    }
}

# Example of PostgreSQL output structure (3 layers: db -> schema -> table)
postgresql_output = {
    "blog_db": {
        "public": {
            "users": {
                "table_name": "users",
                "db": "blog_db",
                "schema": "public",  # Schema information is now included
                "column_data": [
                    {
                        "column_name": "id",
                        "data_type": "int",
                        "is_primary_key": True,
                        "is_foreign_key": False,
                        "is_linked_key": False,
                        "foreign_db": None,
                        "foreign_table": None,
                        "is_nullable": False,
                        "default_value": None,
                        "is_auto_increment": True
                    }
                ],
                "create_table_sql": "CREATE TABLE public.users (id SERIAL PRIMARY KEY)"
            }
        },
        "auth": {
            "permissions": {
                "table_name": "permissions",
                "db": "blog_db",
                "schema": "auth",  # Different schema
                "column_data": [
                    {
                        "column_name": "id",
                        "data_type": "int",
                        "is_primary_key": True,
                        "is_foreign_key": False,
                        "is_linked_key": False,
                        "foreign_db": None,
                        "foreign_table": None,
                        "is_nullable": False,
                        "default_value": None,
                        "is_auto_increment": True
                    }
                ],
                "create_table_sql": "CREATE TABLE auth.permissions (id SERIAL PRIMARY KEY)"
            }
        }
    }
}

def main():
    print("=== MySQL Output Structure (2 layers: db -> table) ===")
    print(json.dumps(mysql_output, indent=2))
    
    print("\n" + "="*60)
    print("=== PostgreSQL Output Structure (3 layers: db -> schema -> table) ===")
    print(json.dumps(postgresql_output, indent=2))
    
    print("\n" + "="*60)
    print("Key differences:")
    print("1. PostgreSQL output includes a schema layer between database and table")
    print("2. Each table info includes a 'schema' field for PostgreSQL")
    print("3. Multiple schemas can exist within the same database")
    print("4. Cross-schema relationships are properly handled")
    
    print("\nUsage examples:")
    print("# Mine all tables from a specific PostgreSQL schema:")
    print("python manage.py durc_mine --include mydb.public")
    print()
    print("# Mine a specific table from a PostgreSQL schema:")
    print("python manage.py durc_mine --include mydb.public.users")
    print()
    print("# Mine multiple schemas:")
    print("python manage.py durc_mine --include mydb.public mydb.auth")

if __name__ == "__main__":
    main()
