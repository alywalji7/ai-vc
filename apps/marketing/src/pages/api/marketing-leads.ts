import { NextApiRequest, NextApiResponse } from 'next';
import { Pool } from 'pg';

// Initialize PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

interface LeadData {
  name: string;
  email: string;
  company: string;
  role?: string;
  message?: string;
  source?: string;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { name, email, company, role, message, source } = req.body as LeadData;

    // Basic validation
    if (!name || !email || !company) {
      return res.status(400).json({ error: 'Name, email, and company are required' });
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ error: 'Invalid email format' });
    }

    // Insert lead data into database
    const result = await pool.query(
      `INSERT INTO marketing_leads (name, email, company, role, message, source, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, NOW())
       RETURNING id`,
      [name, email, company, role || null, message || null, source || 'website']
    );

    // Send notification to admin (could be implemented with SendGrid or similar)
    // For now, just log to console
    console.log(`New lead: ${name} (${email}) from ${company}`);

    return res.status(201).json({ 
      success: true, 
      message: 'Lead information received',
      id: result.rows[0].id
    });
  } catch (error) {
    console.error('Error saving lead:', error);
    return res.status(500).json({ error: 'Failed to save lead information' });
  }
}