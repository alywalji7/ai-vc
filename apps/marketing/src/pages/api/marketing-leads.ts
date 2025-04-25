import type { NextApiRequest, NextApiResponse } from 'next';
import { Pool } from 'pg';
import { trackEvent } from '../../lib/analytics';

// Database connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Types
type LeadData = {
  email: string;
  name?: string;
  company?: string;
  title?: string;
  phone?: string;
  company_size?: string;
  investment_stage?: string;
  fund_size?: string;
  notes?: string;
  lead_source: string;
  lead_campaign?: string;
  lead_medium?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  referrer_url?: string;
  first_page_visited?: string;
  user_agent?: string;
  ip_address?: string;
  country?: string;
  city?: string;
};

// Response types
type SuccessResponse = {
  success: true;
  id: number;
  message: string;
};

type ErrorResponse = {
  success: false;
  error: string;
};

/**
 * Validates lead data
 * @param data Lead data to validate
 * @returns An array of validation error messages, or an empty array if valid
 */
function validateLeadData(data: any): string[] {
  const errors: string[] = [];
  
  // Check required fields
  if (!data.email) {
    errors.push('Email is required');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push('Email is invalid');
  }
  
  if (!data.lead_source) {
    errors.push('Lead source is required');
  }
  
  // Check field length constraints
  if (data.email && data.email.length > 255) {
    errors.push('Email must be 255 characters or less');
  }
  
  if (data.name && data.name.length > 100) {
    errors.push('Name must be 100 characters or less');
  }
  
  if (data.company && data.company.length > 100) {
    errors.push('Company must be 100 characters or less');
  }
  
  if (data.title && data.title.length > 100) {
    errors.push('Title must be 100 characters or less');
  }
  
  if (data.phone && data.phone.length > 50) {
    errors.push('Phone must be 50 characters or less');
  }
  
  return errors;
}

/**
 * Sanitizes lead data for database insertion
 * @param data Raw lead data
 * @returns Sanitized data ready for db insertion
 */
function sanitizeLeadData(data: any): LeadData {
  // Keep only known fields and use proper types
  return {
    email: String(data.email).trim().toLowerCase(),
    name: data.name ? String(data.name).trim() : undefined,
    company: data.company ? String(data.company).trim() : undefined,
    title: data.title ? String(data.title).trim() : undefined,
    phone: data.phone ? String(data.phone).trim() : undefined,
    company_size: data.company_size ? String(data.company_size).trim() : undefined,
    investment_stage: data.investment_stage ? String(data.investment_stage).trim() : undefined,
    fund_size: data.fund_size ? String(data.fund_size).trim() : undefined,
    notes: data.notes ? String(data.notes).trim() : undefined,
    lead_source: String(data.lead_source).trim(),
    lead_campaign: data.lead_campaign ? String(data.lead_campaign).trim() : undefined,
    lead_medium: data.lead_medium ? String(data.lead_medium).trim() : undefined,
    utm_source: data.utm_source ? String(data.utm_source).trim() : undefined,
    utm_medium: data.utm_medium ? String(data.utm_medium).trim() : undefined,
    utm_campaign: data.utm_campaign ? String(data.utm_campaign).trim() : undefined,
    utm_term: data.utm_term ? String(data.utm_term).trim() : undefined,
    utm_content: data.utm_content ? String(data.utm_content).trim() : undefined,
    referrer_url: data.referrer_url ? String(data.referrer_url).trim() : undefined,
    first_page_visited: data.first_page_visited ? String(data.first_page_visited).trim() : undefined,
    user_agent: data.user_agent,
    ip_address: data.ip_address,
    country: data.country,
    city: data.city
  };
}

/**
 * Inserts a lead into the database
 * @param data Validated and sanitized lead data
 * @returns The ID of the inserted lead
 */
async function insertLead(data: LeadData): Promise<number> {
  // Prepare query fields and values
  const fields = Object.keys(data).filter(key => data[key as keyof LeadData] !== undefined);
  const values = fields.map(field => data[field as keyof LeadData]);
  const placeholders = fields.map((_, index) => `$${index + 1}`);
  
  // Build and execute query
  const query = `
    INSERT INTO marketing_leads (${fields.join(', ')})
    VALUES (${placeholders.join(', ')})
    RETURNING id
  `;
  
  const result = await pool.query(query, values);
  return result.rows[0].id;
}

/**
 * API route handler for marketing leads
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<SuccessResponse | ErrorResponse>
) {
  // Only allow POST method
  if (req.method !== 'POST') {
    return res.status(405).json({
      success: false,
      error: 'Method not allowed',
    });
  }
  
  try {
    // Get client IP
    const forwarded = req.headers['x-forwarded-for'];
    const ip = forwarded
      ? Array.isArray(forwarded)
        ? forwarded[0]
        : forwarded.split(/, /)[0]
      : req.socket.remoteAddress;
    
    // Add IP and user agent to request data
    const data = {
      ...req.body,
      ip_address: ip,
      user_agent: req.headers['user-agent'],
    };
    
    // Validate the data
    const validationErrors = validateLeadData(data);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        success: false,
        error: validationErrors.join(', '),
      });
    }
    
    // Sanitize the data
    const sanitizedData = sanitizeLeadData(data);
    
    // Insert the lead
    const leadId = await insertLead(sanitizedData);
    
    // Track the event for analytics
    trackEvent('marketing_lead_created', {
      lead_id: leadId,
      lead_source: sanitizedData.lead_source,
      lead_campaign: sanitizedData.lead_campaign,
    });
    
    // Return success
    return res.status(201).json({
      success: true,
      id: leadId,
      message: 'Lead created successfully',
    });
  } catch (error) {
    console.error('Error creating marketing lead:', error);
    
    // Check for duplicate key violation
    if (error instanceof Error && error.message.includes('duplicate key')) {
      return res.status(409).json({
        success: false,
        error: 'A lead with this email already exists',
      });
    }
    
    // Return general error
    return res.status(500).json({
      success: false,
      error: 'An error occurred while creating the lead',
    });
  }
}