import fs from 'fs';
import path from 'path';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const termsPath = path.join(process.cwd(), 'docs', 'legal', 'terms.md');
    const termsContent = fs.readFileSync(termsPath, 'utf8');
    return NextResponse.json({ content: termsContent });
  } catch (error) {
    console.error('Error fetching terms of service:', error);
    return NextResponse.json(
      { error: 'Failed to fetch terms of service' },
      { status: 500 }
    );
  }
}