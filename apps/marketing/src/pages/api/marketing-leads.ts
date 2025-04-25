import { NextApiRequest, NextApiResponse } from 'next';
import { Pool } from 'pg';
import { trackEvent } from '../../lib/analytics';

// Initialize PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Email validation regex
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Define types for our lead form data
interface LeadData {
  firstName: string;
  lastName: string;
  email: string;
  company?: string;
  jobTitle?: string;
  phone?: string;
  message?: string;
  leadSource: string;
  campaign?: string;
  referrer?: string;
  utmSource?: string;
  utmMedium?: string;
  utmCampaign?: string;
  utmTerm?: string;
  utmContent?: string;
  interestedIn?: string;
  subscribedToNewsletter: boolean;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, message: 'Method not allowed' });
  }

  try {
    const data = req.body as LeadData;

    // Validate required fields
    if (!data.firstName || !data.lastName || !data.email) {
      return res.status(400).json({ success: false, message: 'First name, last name, and email are required' });
    }

    // Validate email format
    if (!EMAIL_REGEX.test(data.email)) {
      return res.status(400).json({ success: false, message: 'Invalid email format' });
    }

    // Prepare database query
    const query = `
      INSERT INTO marketing_leads (
        first_name,
        last_name,
        email,
        company,
        job_title,
        phone,
        message,
        lead_source,
        campaign,
        referrer,
        utm_source,
        utm_medium,
        utm_campaign,
        utm_term,
        utm_content,
        interested_in,
        subscribed_to_newsletter
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
      RETURNING id`;

    const values = [
      data.firstName,
      data.lastName,
      data.email,
      data.company || null,
      data.jobTitle || null,
      data.phone || null,
      data.message || null,
      data.leadSource || 'website',
      data.campaign || null,
      data.referrer || null,
      data.utmSource || null,
      data.utmMedium || null,
      data.utmCampaign || null,
      data.utmTerm || null,
      data.utmContent || null,
      data.interestedIn || null,
      data.subscribedToNewsletter || false
    ];

    // Execute the query
    const result = await pool.query(query, values);
    const leadId = result.rows[0].id;

    // Track the lead submission event
    trackEvent('lead_submitted', {
      leadId,
      source: data.leadSource,
      campaign: data.campaign,
      utmSource: data.utmSource,
      subscribedToNewsletter: data.subscribedToNewsletter
    });

    // Return success response with lead ID
    return res.status(201).json({ 
      success: true, 
      message: 'Lead submitted successfully', 
      data: { leadId } 
    });

  } catch (error) {
    console.error('Error submitting lead:', error);

    // Handle duplicate email error from PostgreSQL
    if (error instanceof Error && error.message.includes('duplicate key value violates unique constraint')) {
      return res.status(409).json({ 
        success: false, 
        message: 'This email address is already registered in our system' 
      });
    }

    // Return generic error response
    return res.status(500).json({ 
      success: false, 
      message: 'An error occurred while submitting your information' 
    });
  }
}