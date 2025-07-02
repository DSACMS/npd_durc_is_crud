-- Merged CREATE TABLE statements
-- Generated on: 2025-07-01 23:46:04
-- Total CREATE TABLE statements: 28
--
-- Source files:
--   ./AI_Instructions/durc_postgres_test_files/DURC_aaa.postgres.sql
--   ./AI_Instructions/durc_postgres_test_files/DURC_bbb.postgres.sql
--   ./tests/diagram_output_tests/test_with_sections.sql


CREATE TABLE "Should be Ignored" (
  "firstname" varchar(11) DEFAULT NULL,
  "lastname" varchar(12) DEFAULT NULL,
  "NULL" varchar(13) DEFAULT NULL
);

CREATE TABLE "author" (
  id SERIAL PRIMARY KEY,
  lastname varchar(255) NOT NULL,
  firstname varchar(255) NOT NULL,
  created_date timestamp DEFAULT NULL,
  updated_date timestamp DEFAULT NULL
);

CREATE TABLE "author_book" (
  id SERIAL PRIMARY KEY,
  author_id integer NOT NULL,
  book_id integer NOT NULL,
  authortype_id integer NOT NULL
);

CREATE TABLE "authortype" (
  id SERIAL PRIMARY KEY,
  authortypedesc varchar(255) NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

CREATE TABLE "book" (
  id SERIAL PRIMARY KEY,
  title varchar(255) NOT NULL,
  release_date timestamp NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

CREATE TABLE "characterTest" (
  id SERIAL PRIMARY KEY,
  funny_character_field varchar(1000) NOT NULL
);

CREATE TABLE "comment" (
  id SERIAL PRIMARY KEY,
  comment_text varchar(1000) NOT NULL,
  post_id integer NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

CREATE TABLE "filterTest" (
  id SERIAL PRIMARY KEY,
  test_url varchar(1000) NOT NULL,
  test_json text NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "foreignkeytestgizmo" (
  id SERIAL PRIMARY KEY,
  gizmoname varchar(100) NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL,
  deleted_at timestamp NOT NULL
);

CREATE TABLE "foreignkeytestthingy" (
  id SERIAL PRIMARY KEY,
  thingyname varchar(100) NOT NULL,
  gizmopickupaskey integer NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL,
  deleted_at timestamp NOT NULL
);

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

CREATE TABLE "post" (
  id SERIAL PRIMARY KEY,
  title varchar(100) NOT NULL,
  content varchar(1000) NOT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

CREATE TABLE "sibling" (
  id SERIAL PRIMARY KEY,
  siblingname varchar(255) NOT NULL,
  step_sibling_id integer DEFAULT NULL,
  sibling_id integer DEFAULT NULL,
  created_at timestamp NOT NULL,
  updated_at timestamp NOT NULL
);

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

CREATE TABLE "test_boolean" (
  id SERIAL PRIMARY KEY,
  label varchar(255) NOT NULL,
  is_something varchar(255) NOT NULL,
  has_something varchar(255) NOT NULL,
  is_something2 smallint DEFAULT NULL,
  has_something2 smallint DEFAULT NULL,
  has_something3 boolean DEFAULT NULL
);

CREATE TABLE "test_created_only" (
  id SERIAL PRIMARY KEY,
  name varchar(255) DEFAULT NULL,
  created_at timestamp NOT NULL
);

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

CREATE TABLE "test_null_default" (
  id SERIAL PRIMARY KEY,
  null_var varchar(255) DEFAULT NULL,
  non_null_var_def varchar(255) NOT NULL,
  non_null_var_no_def varchar(255) DEFAULT NULL,
  nullable_w_default varchar(255) DEFAULT 'THIS IS THE DEFAULT',
  non_null_default varchar(255) NOT NULL DEFAULT 'I CANNOT BE NULL'
);

CREATE TABLE "vote" (
  id SERIAL PRIMARY KEY,
  post_id integer NOT NULL,
  votenum varchar(11) NOT NULL,
  updated_at timestamp NOT NULL,
  created_at timestamp NOT NULL
);

CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username varchar(50) NOT NULL UNIQUE,
    email varchar(100) NOT NULL UNIQUE,
    password_hash varchar(255) NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profile (
    id SERIAL PRIMARY KEY,
    user_id integer NOT NULL,
    first_name varchar(50),
    last_name varchar(50),
    bio text,
    avatar_url varchar(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE,
    description text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post (
    id SERIAL PRIMARY KEY,
    user_id integer NOT NULL,
    category_id integer NOT NULL,
    title varchar(200) NOT NULL,
    content text NOT NULL,
    status varchar(20) DEFAULT 'draft',
    published_at timestamp,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    parent_comment_id integer,
    content text NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vote (
    id SERIAL PRIMARY KEY,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    vote_type varchar(10) NOT NULL CHECK (vote_type IN ('up', 'down')),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

CREATE TABLE bookmark (
    id SERIAL PRIMARY KEY,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);
