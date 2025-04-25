-- Create marketing_leads table if it doesn't exist
CREATE TABLE IF NOT EXISTS marketing_leads (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  company VARCHAR(255) NOT NULL,
  role VARCHAR(255),
  message TEXT,
  source VARCHAR(100) DEFAULT 'website',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on email to avoid duplicate leads
CREATE UNIQUE INDEX IF NOT EXISTS idx_marketing_leads_email ON marketing_leads(email);

-- Create index on created_at for better performance on date-based queries
CREATE INDEX IF NOT EXISTS idx_marketing_leads_created_at ON marketing_leads(created_at);

-- Create trigger to automatically update updated_at column
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_marketing_leads_updated_at ON marketing_leads;
CREATE TRIGGER set_marketing_leads_updated_at
BEFORE UPDATE ON marketing_leads
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();