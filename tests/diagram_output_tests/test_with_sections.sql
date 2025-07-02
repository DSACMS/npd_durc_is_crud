-- Test SQL file with diagram sections for DURC diagram generator

-- Diagram Section: User Management
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username varchar(50) NOT NULL UNIQUE,
    email varchar(100) NOT NULL UNIQUE,
    password_hash varchar(255) NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Diagram Section: User Management
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

-- Diagram Section: Content Management
CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE,
    description text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Diagram Section: Content Management
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

-- Diagram Section: Content Management
CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    parent_comment_id integer,
    content text NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Diagram Section: Engagement
CREATE TABLE vote (
    id SERIAL PRIMARY KEY,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    vote_type varchar(10) NOT NULL CHECK (vote_type IN ('up', 'down')),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

-- Diagram Section: Engagement
CREATE TABLE bookmark (
    id SERIAL PRIMARY KEY,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);
