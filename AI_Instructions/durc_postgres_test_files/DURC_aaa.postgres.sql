-- PostgreSQL dump converted from MySQL
--
-- Host: localhost    Database: DURC_aaa
-- ------------------------------------------------------


SET search_path TO DURC_aaa;

--
-- Table structure for table "Should be Ignored"
--

DROP TABLE IF EXISTS "Should be Ignored";
CREATE TABLE "Should be Ignored" (
  "firstname" varchar(11) DEFAULT NULL,
  "lastname" varchar(12) DEFAULT NULL,
  "NULL" varchar(13) DEFAULT NULL
);

--
-- Table structure for table "author"
--

DROP TABLE IF EXISTS "author";
CREATE TABLE "author" (
  id SERIAL PRIMARY KEY,
  lastname varchar(255) NOT NULL,
  firstname varchar(255) NOT NULL,
  created_date timestamp DEFAULT NULL,
  updated_date timestamp DEFAULT NULL
);

--
-- Table structure for table "author_book"
--

DROP TABLE IF EXISTS "author_book";
CREATE TABLE "author_book" (
  id SERIAL PRIMARY KEY,
  author_id integer NOT NULL,
  book_id integer NOT NULL,
  authortype_id integer NOT NULL
);

--
-- Table structure for table "authortype"
--

DROP TABLE IF EXISTS "authortype";
CREATE TABLE "authortype" (
  id SERIAL PRIMARY KEY,
  authortypedesc varchar(255) NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

--
-- Table structure for table "book"
--

DROP TABLE IF EXISTS "book";
CREATE TABLE "book" (
  id SERIAL PRIMARY KEY,
  title varchar(255) NOT NULL,
  release_date timestamp NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

--
-- Table structure for table "characterTest"
--

DROP TABLE IF EXISTS "characterTest";
CREATE TABLE "characterTest" (
  id SERIAL PRIMARY KEY,
  funny_character_field varchar(1000) NOT NULL
);

--
-- Table structure for table "comment"
--

DROP TABLE IF EXISTS "comment";
CREATE TABLE "comment" (
  id SERIAL PRIMARY KEY,
  comment_text varchar(1000) NOT NULL,
  post_id integer NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);



--
-- Table structure for table "filterTest"
--

DROP TABLE IF EXISTS "filterTest";
CREATE TABLE "filterTest" (
  id SERIAL PRIMARY KEY,
  test_url varchar(1000) NOT NULL,
  test_json text NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--
-- Table structure for table "foreignkeytestgizmo"
--

DROP TABLE IF EXISTS "foreignkeytestgizmo";
CREATE TABLE "foreignkeytestgizmo" (
  id SERIAL PRIMARY KEY,
  gizmoname varchar(100) NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL,
  deleted_at timestamp NOT NULL
);

--
-- Table structure for table "foreignkeytestthingy"
--

DROP TABLE IF EXISTS "foreignkeytestthingy";
CREATE TABLE "foreignkeytestthingy" (
  id SERIAL PRIMARY KEY,
  thingyname varchar(100) NOT NULL,
  gizmopickupaskey integer NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL,
  deleted_at timestamp NOT NULL
);

CREATE INDEX gizmopickupaskey_idx ON "foreignkeytestthingy" (gizmopickupaskey);
ALTER TABLE "foreignkeytestthingy" ADD CONSTRAINT "forgizmo" 
  FOREIGN KEY (gizmopickupaskey) REFERENCES "foreignkeytestgizmo" (id);

--
-- Table structure for table "funnything"
--

DROP TABLE IF EXISTS "funnything";
CREATE TABLE "funnything" (
  id SERIAL PRIMARY KEY,
  thisint integer DEFAULT NULL,
  thisfloat float DEFAULT NULL,
  thisdecimal decimal(5,5) DEFAULT NULL,
  thisvarchar varchar(100) DEFAULT NULL,
  thisdate date DEFAULT NULL,
  thisdatetime timestamp DEFAULT NULL,
  thistimestamp timestamp NULL DEFAULT NULL,
  thischar char(1) NOT NULL,
  thistext text NOT NULL,
  thisblob bytea DEFAULT NULL,
  thistinyint smallint NOT NULL,
  thistinytext text NOT NULL
);

--
-- Table structure for table "graphdata_nodetypetests"
--

DROP TABLE IF EXISTS "graphdata_nodetypetests";
CREATE TABLE "graphdata_nodetypetests" (
  source_id varchar(50) NOT NULL,
  source_name varchar(190) NOT NULL,
  source_size integer NOT NULL DEFAULT 0,
  source_type varchar(190) NOT NULL,
  source_group varchar(190) NOT NULL,
  source_longitude decimal(17,7) NOT NULL DEFAULT 0.0000000,
  source_latitude decimal(17,7) NOT NULL DEFAULT 0.0000000,
  source_img varchar(190) DEFAULT NULL,
  target_id varchar(50) NOT NULL,
  target_name varchar(190) NOT NULL,
  target_size integer NOT NULL DEFAULT 0,
  target_type varchar(190) NOT NULL,
  target_group varchar(190) NOT NULL,
  target_longitude decimal(17,7) NOT NULL DEFAULT 0.0000000,
  target_latitude decimal(17,7) NOT NULL DEFAULT 0.0000000,
  target_img varchar(190) DEFAULT NULL,
  weight integer NOT NULL DEFAULT 50,
  link_type varchar(190) NOT NULL,
  query_num integer NOT NULL,
  PRIMARY KEY (source_id, source_type, target_id, target_type)
);

--
-- Table structure for table "magicField"
--

DROP TABLE IF EXISTS "magicField";
CREATE TABLE "magicField" (
  id SERIAL PRIMARY KEY,
  editsome_markdown varchar(2000) NOT NULL,
  typesome_sql_code varchar(2000) NOT NULL,
  typesome_php_code text NOT NULL,
  typesome_python_code text NOT NULL,
  typesome_javascript_code varchar(3000) NOT NULL,
  this_datetime timestamp NOT NULL,
  this_date date NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at timestamp DEFAULT NULL
);

--
-- Table structure for table "post"
--

DROP TABLE IF EXISTS "post";
CREATE TABLE "post" (
  id SERIAL PRIMARY KEY,
  title varchar(100) NOT NULL,
  content varchar(1000) NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

--
-- Table structure for table "sibling"
--

DROP TABLE IF EXISTS "sibling";
CREATE TABLE "sibling" (
  id SERIAL PRIMARY KEY,
  siblingname varchar(255) NOT NULL,
  step_sibling_id integer DEFAULT NULL,
  sibling_id integer DEFAULT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

--
-- Table structure for table "tags_report"
--

DROP TABLE IF EXISTS "tags_report";
CREATE TABLE "tags_report" (
  id BIGSERIAL PRIMARY KEY,
  field_to_bold_in_report_display varchar(255) NOT NULL,
  field_to_hide_by_default varchar(255) NOT NULL,
  field_to_italic_in_report_display varchar(255) NOT NULL,
  field_to_right_align_in_report varchar(255) NOT NULL,
  field_to_bolditalic_in_report_display varchar(255) NOT NULL,
  numeric_field integer NOT NULL,
  decimal_field decimal(10,4) NOT NULL,
  currency_field varchar(255) NOT NULL,
  percent_field integer NOT NULL,
  url_field varchar(255) NOT NULL,
  time_field time NOT NULL,
  date_field date NOT NULL,
  datetime_field timestamp NOT NULL
);

--
-- Table structure for table "test_boolean"
--

DROP TABLE IF EXISTS "test_boolean";
CREATE TABLE "test_boolean" (
  id SERIAL PRIMARY KEY,
  label varchar(255) NOT NULL,
  is_something varchar(255) NOT NULL,
  has_something varchar(255) NOT NULL,
  is_something2 smallint DEFAULT NULL,
  has_something2 smallint DEFAULT NULL,
  has_something3 boolean DEFAULT NULL
);

--
-- Table structure for table "test_created_only"
--

DROP TABLE IF EXISTS "test_created_only";
CREATE TABLE "test_created_only" (
  id SERIAL PRIMARY KEY,
  name varchar(255) DEFAULT NULL,
  created_at timestamp NOT NULL
);

--
-- Table structure for table "test_default_date"
--

DROP TABLE IF EXISTS "test_default_date";
CREATE TABLE "test_default_date" (
  id integer NOT NULL PRIMARY KEY,
  datetime_none timestamp NOT NULL,
  date_none date NOT NULL,
  datetime_current timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  date_current varchar(255) DEFAULT 'Current timestamp not supported for date',
  datetime_null timestamp DEFAULT NULL,
  date_null date DEFAULT NULL,
  datetime_defined timestamp NOT NULL DEFAULT '2000-01-01 01:23:45',
  date_defined date NOT NULL DEFAULT '2000-01-01'
);

--
-- Table structure for table "test_null_default"
--

DROP TABLE IF EXISTS "test_null_default";
CREATE TABLE "test_null_default" (
  id SERIAL PRIMARY KEY,
  null_var varchar(255) DEFAULT NULL,
  non_null_var_def varchar(255) NOT NULL,
  non_null_var_no_def varchar(255) DEFAULT NULL,
  nullable_w_default varchar(255) DEFAULT 'THIS IS THE DEFAULT',
  non_null_default varchar(255) NOT NULL DEFAULT 'I CANNOT BE NULL'
);


