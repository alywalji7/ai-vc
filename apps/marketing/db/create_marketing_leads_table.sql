-- Table: public.marketing_leads

CREATE TABLE IF NOT EXISTS public.marketing_leads (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    company VARCHAR(100),
    title VARCHAR(100),
    phone VARCHAR(50),
    company_size VARCHAR(50),
    investment_stage VARCHAR(50),
    fund_size VARCHAR(50),
    lead_source VARCHAR(50) NOT NULL,
    lead_campaign VARCHAR(100),
    lead_medium VARCHAR(50),
    is_subscribed BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_contacted_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'new',
    assigned_to VARCHAR(50),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    utm_term VARCHAR(100),
    utm_content VARCHAR(100),
    referrer_url TEXT,
    first_page_visited TEXT,
    user_agent TEXT,
    ip_address VARCHAR(50),
    country VARCHAR(50),
    city VARCHAR(50),
    CONSTRAINT marketing_leads_email_unique UNIQUE (email)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_marketing_leads_email ON public.marketing_leads(email);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_created_at ON public.marketing_leads(created_at);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_status ON public.marketing_leads(status);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_lead_source ON public.marketing_leads(lead_source);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_company ON public.marketing_leads(company);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_investment_stage ON public.marketing_leads(investment_stage);

-- Trigger function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_marketing_leads_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function before each update
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_update_marketing_leads_updated_at'
    ) THEN
        CREATE TRIGGER trigger_update_marketing_leads_updated_at
        BEFORE UPDATE ON public.marketing_leads
        FOR EACH ROW
        EXECUTE FUNCTION update_marketing_leads_updated_at();
    END IF;
END
$$;

-- Add comments
COMMENT ON TABLE public.marketing_leads IS 'Table to store marketing leads and their information';
COMMENT ON COLUMN public.marketing_leads.id IS 'Unique identifier for the lead';
COMMENT ON COLUMN public.marketing_leads.email IS 'Email address of the lead (unique)';
COMMENT ON COLUMN public.marketing_leads.name IS 'Full name of the lead';
COMMENT ON COLUMN public.marketing_leads.company IS 'Company name of the lead';
COMMENT ON COLUMN public.marketing_leads.title IS 'Job title of the lead';
COMMENT ON COLUMN public.marketing_leads.company_size IS 'Size of the company the lead works for';
COMMENT ON COLUMN public.marketing_leads.investment_stage IS 'The investment stage the lead is interested in';
COMMENT ON COLUMN public.marketing_leads.fund_size IS 'Fund size range of the lead';
COMMENT ON COLUMN public.marketing_leads.lead_source IS 'Source of the lead (website, event, referral, etc.)';
COMMENT ON COLUMN public.marketing_leads.lead_campaign IS 'Campaign that generated the lead';
COMMENT ON COLUMN public.marketing_leads.lead_medium IS 'Medium that generated the lead';
COMMENT ON COLUMN public.marketing_leads.is_subscribed IS 'Whether the lead is subscribed to marketing emails';
COMMENT ON COLUMN public.marketing_leads.notes IS 'Additional notes about the lead';
COMMENT ON COLUMN public.marketing_leads.created_at IS 'When the lead was created';
COMMENT ON COLUMN public.marketing_leads.updated_at IS 'When the lead was last updated';
COMMENT ON COLUMN public.marketing_leads.last_contacted_at IS 'When the lead was last contacted';
COMMENT ON COLUMN public.marketing_leads.status IS 'Current status of the lead (new, contacted, qualified, etc.)';
COMMENT ON COLUMN public.marketing_leads.assigned_to IS 'Person assigned to this lead';
COMMENT ON COLUMN public.marketing_leads.utm_source IS 'UTM source parameter from the URL';
COMMENT ON COLUMN public.marketing_leads.utm_medium IS 'UTM medium parameter from the URL';
COMMENT ON COLUMN public.marketing_leads.utm_campaign IS 'UTM campaign parameter from the URL';
COMMENT ON COLUMN public.marketing_leads.utm_term IS 'UTM term parameter from the URL';
COMMENT ON COLUMN public.marketing_leads.utm_content IS 'UTM content parameter from the URL';
COMMENT ON COLUMN public.marketing_leads.referrer_url IS 'Referrer URL if available';
COMMENT ON COLUMN public.marketing_leads.first_page_visited IS 'First page the lead visited';
COMMENT ON COLUMN public.marketing_leads.user_agent IS 'User agent of the lead';
COMMENT ON COLUMN public.marketing_leads.ip_address IS 'IP address of the lead';
COMMENT ON COLUMN public.marketing_leads.country IS 'Country of the lead based on IP';
COMMENT ON COLUMN public.marketing_leads.city IS 'City of the lead based on IP';