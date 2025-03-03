-- Drop existing backup table if it exists
DROP TABLE IF EXISTS users_backup;

-- Create backup of existing users table
CREATE TABLE users_backup AS SELECT * FROM users;

-- Drop existing constraints and indexes
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_pkey CASCADE;

-- Modify existing columns
ALTER TABLE users ALTER COLUMN email SET DATA TYPE VARCHAR(255);

-- Check if password_hash already exists, if not, create it from password column
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'password'
    ) THEN
        ALTER TABLE users RENAME COLUMN password TO password_hash;
        ALTER TABLE users ALTER COLUMN password_hash SET DATA TYPE VARCHAR(255);
    ELSIF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'password_hash'
    ) THEN
        ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
    END IF;
END $$;

-- Add new columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(50) UNIQUE;
ALTER TABLE users ALTER COLUMN created_at SET DATA TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- Generate usernames for any existing users from their email BEFORE adding constraints
UPDATE users 
SET username = SPLIT_PART(email, '@', 1) 
WHERE username IS NULL;

-- Make sure ID is serial/integer type
ALTER TABLE users ALTER COLUMN id SET DATA TYPE integer;
ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);

-- Now add constraints after data is prepared
ALTER TABLE users ADD PRIMARY KEY (id);
ALTER TABLE users ALTER COLUMN username SET NOT NULL;
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add foreign key constraint to cart table
ALTER TABLE cart
    ADD CONSTRAINT fk_cart_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE;

-- Add Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT
    USING (auth.uid()::text::integer = id);

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE
    USING (auth.uid()::text::integer = id);

-- Create policy for cart access
CREATE POLICY "Users can view their own cart" ON cart
    FOR ALL
    USING (user_id = (SELECT id FROM users WHERE id = auth.uid()::text::integer));

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE ON users TO authenticated;
GRANT SELECT ON users TO anon; 