DURC Diagram
============

I would like to add a second command to this project that makes diagrams from CREATE TABLE statements.

Read the following to understand how DURC works:

* Look in AI_Instructions/DURC_naming_convention_details.md for the naming conventions that DURC uses
* Look in durc_is_crud/management/commands/durc_mine.py as a gateway to the code that implements the relational extraction method

Then implement a CLI python command that:

* First, inferring the relational model from a series CREATE TABLE sql statements in one or more sql files.
* In addition to the relational model, you should create "sections" of the diagram by parsing Diagram Section: comments ahead of CREATE TABLE statements.
* For any SQL comment immediately before a CREATE TABLE statement:
  * Check for a colon ':' and if it exists split the string into label (the first half) and section_name (the second half)
  * check to make sure that the label is always Diagram Section by removing all spaces, converting to lowercase and seeing if it == 'diagramsection'
* When making the diagram, each table should live in a box and should be linked to each other SQL table when there are foregin keys accoriding to the DURC naming scheme.
* Irrespective of links between tables, each table that has an identical section_name should live inside a "background box". For this purpose be flexible with the section_name in the same whitaspace and case invariant way I described for the label part of the SQL comment.
* This python command should not be dependant on DJANGO
* The tables should list all of the fields in the same order as the create table statement
* For now, do not bother to implement an cardianlity indicators.
* the color pallete for the tables should be light pastels
* The tables in each section box should have the same light pastel color to contrast the black lettering of the text
* The section box 'behing' the table boxes should use the same pastel tone, but a darker version to provide contract with the table boxes
* Each section box should have the Section Name in larger black lettering at the top left of the section box.
* EAch section background box should have a background color
* At the bottom of the markdown file, beneath the diagram should be an ordered list of links back to the create table sql files that were the source of the diagram

The argument to the program should be:
--sql_files = a list of one or many files that end in .sql to parse.
--output_md_file = the markdown file to create or overwrite with the diagram.

Formating Specifics
------------

* the table names should be two font sizes larger than the text for the column definitions. The section labels should be two sizes larger than that.
* The column labels should be left aligned in the table boxes, and the column type should be right aligned.
