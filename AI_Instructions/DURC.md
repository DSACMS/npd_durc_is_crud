DURC Specification
==================

DURC ("CRUD" spelled backwards) is a framework and Python script for automatically generating Django-based CRUD user interfaces (forms, views, and REST endpoints) based on an existing database schema. The primary goal is to enable developers to rapidly scaffold a fully functional HTML+REST front-end, where customization can be layered cleanly on top of generated code without being overwritten.

Overview
---------

DURC inspects one or more specified database structures and generates:

1. Mine the underlying data models and relationships and write these to /durc_config/DURC_relational_model.json (see the AI_instructions/DURC_simplified.example.json for an example of how this should be structured)
2. From the DURC_relational_model.json generate the "Generated" Django models (safe to overwrite)
3. From the DURC_relational_model.json generate the "Validated" model subclasses (customizable, never overwritten)
4. From the DURC_relational_model.json generate ModelForm classes with enhanced widgets, that refer to the "Validated" model subclasses
5. From the DURC_relational_model.json generate the DJango Rest Framework REST endpoint integration for Tom Select javascript autosuggest widgets

This produces a complete CRUD-ready experience using Django's ecosystem while keeping customization intact across runs.

Inputs
-------------

DURC is executed as two command-line scripts with arguments:

### DURC Mine Command

```bash
python manage.py durc_mine --include mydb.schema1.table1 mydb.schema2 mydb
```

Input Interpretation:

* mydb.schema1.table1 → include just table1
* mydb.schema2 → include all tables in schema2
* mydb → include all schemas and all tables in the database

Output: The json schema documentation file in /durc_config/

### DURC Compile Command

```bash
python manage.py durc_compile /durc_config/DURC_relational_model.json
```

Input: the relational model json file that is created by the durc_mine command.

Output File Structure:

myapp/
├── models/
│   └── g_book.py               # Overwritten every time
|   |__ v_book.py               # Only created once
├── forms/
│   └── v_book_form.py          # Contains enhanced widgets and autosuggest
└── ...

In addition to the command above, which generates all of the Django components at once, it is possible to generate each type of asset one at a time with: 

* python manage.py durc_compile --compile models /durc_config/DURC_relational_model.json
* python manage.py durc_compile --compile model_forms /durc_config/DURC_relational_model.json
* python manage.py durc_compile --compile REST /durc_config/DURC_relational_model.json

Code Generation Layers
------

1. Relational Model Extractor

    * Compiles the relational model to json for inspection
    * The relational model json is then used as the source for subsequent resource compilation
    * Uses Django's native database introspection capabilities to determine database structures

2. Generated Models

    * Mimics inspectdb behavior but fully rewritten for clarity.
    * Regenerated on each run.
    * Stored in models_generated/*.py
    * Contains field definitions, Django data type mappings, and relational model definitions
    * Complete Django model classes that can be used directly

3. Validated Models

    * Subclasses of generated models.
    * Created only once (unless manually deleted).
    * Includes clean() methods and domain logic.
    * Stored in models_validated/*.py
    * Only Django ORM classes have customization persistence

4. Validated ModelForms

    * Subclasses of forms.ModelForm
    * Generated with enhanced widgets:
    * type="date" for date fields ending in _date
    * inputmode="decimal" for numeric fields
    * autosuggest using Tom Select javascript widgets for foreign keys
    * Stored in forms/*.py

Implementation Details
------

1. Django Management Command
    * DURC is implemented as a Django management command (python manage.py durc)
    * Follows standard Django management command structure and conventions

2. Asset Management
    * DURC scripts include all necessary JavaScript and CSS assets
    * Tom Select and Bootstrap are downloaded and hosted locally (not via CDN)
    * Assets are placed in appropriate static directories

3. Relationship Handling
    * Many-to-many relationships have convenience functions on the model classes
    * UI editing is done through the bridging table with two auto-select widgets
    * This approach simplifies the UX for managing many-to-many relationships

4. File Organization
    * Generated files are placed in standard Django directory locations
    * Follows Django conventions for models, forms, views, and templates

Column Naming and Type Rules
------


⸻
Summary

DURC is a convention-over-configuration code generator for Django that produces a full-stack CRUD interface from your database schema, including:

* Layered code structure
* Modern, accessible, mobile-optimized HTML forms
* REST-powered autosuggestions for related fields
* Safeguards to keep your custom code safe from regeneration
