-- Create marketing leads table for storing leads from various sources

CREATE TABLE IF NOT EXISTS marketing_leads (
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  company VARCHAR(255),
  job_title VARCHAR(255),
  phone VARCHAR(50),
  message TEXT,
  lead_source VARCHAR(100) NOT NULL DEFAULT 'website',
  campaign VARCHAR(100),
  referrer TEXT,
  utm_source VARCHAR(100),
  utm_medium VARCHAR(100),
  utm_campaign VARCHAR(100),
  utm_term VARCHAR(100),
  utm_content VARCHAR(100),
  interested_in VARCHAR(255),
  subscribed_to_newsletter BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Add an index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_marketing_leads_email ON marketing_leads (email);

-- Add an index on lead_source for reporting
CREATE INDEX IF NOT EXISTS idx_marketing_leads_source ON marketing_leads (lead_source);

-- Add an index on created_at for date-based queries
CREATE INDEX IF NOT EXISTS idx_marketing_leads_created_at ON marketing_leads (created_at);

-- Add a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Create a trigger to automatically update the updated_at column
DROP TRIGGER IF EXISTS set_marketing_leads_updated_at ON marketing_leads;
CREATE TRIGGER set_marketing_leads_updated_at
BEFORE UPDATE ON marketing_leads
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- If this script is used for migrations, add a comment about the version
COMMENT ON TABLE marketing_leads IS 'Table to store marketing leads. Version 1.0 - Initial creation';

-- Sample query to insert a lead (commented out - for reference)
/*
INSERT INTO marketing_leads (
  first_name, 
  last_name, 
  email, 
  company, 
  job_title, 
  lead_source, 
  utm_source, 
  utm_medium, 
  utm_campaign,
  subscribed_to_newsletter
) VALUES (
  'John', 
  'Doe', 
  'john.doe@example.com', 
  'Example Corp', 
  'CTO', 
  'website', 
  'google', 
  'cpc', 
  'spring_campaign',
  TRUE
);
*/