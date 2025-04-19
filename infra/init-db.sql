-- Initialize the PostgreSQL database with some schema and initial data

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS app;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table if not exists (already handled by SQLAlchemy, but as a backup)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create items table if not exists (already handled by SQLAlchemy, but as a backup)
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);
CREATE INDEX IF NOT EXISTS idx_items_owner ON items(owner_id);

-- Insert some initial data if the tables are empty
INSERT INTO users (username, email, hashed_password)
SELECT 'admin', 'admin@example.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'  -- SHA-256 hash of 'admin'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

INSERT INTO users (username, email, hashed_password)
SELECT 'user', 'user@example.com', '04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb'  -- SHA-256 hash of 'user'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'user');

-- Insert sample items
DO $$
DECLARE
    admin_id INTEGER;
    user_id INTEGER;
BEGIN
    SELECT id INTO admin_id FROM users WHERE username = 'admin';
    SELECT id INTO user_id FROM users WHERE username = 'user';
    
    IF NOT EXISTS (SELECT 1 FROM items WHERE title = 'First Item') THEN
        INSERT INTO items (title, description, owner_id)
        VALUES ('First Item', 'This is the first item', admin_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM items WHERE title = 'Second Item') THEN
        INSERT INTO items (title, description, owner_id)
        VALUES ('Second Item', 'This is the second item', user_id);
    END IF;
END $$;
