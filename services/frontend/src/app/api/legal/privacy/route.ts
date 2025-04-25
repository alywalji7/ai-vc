import fs from 'fs';
import path from 'path';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const privacyPath = path.join(process.cwd(), 'docs', 'legal', 'privacy.md');
    const privacyContent = fs.readFileSync(privacyPath, 'utf8');
    return NextResponse.json({ content: privacyContent });
  } catch (error) {
    console.error('Error fetching privacy policy:', error);
    return NextResponse.json(
      { error: 'Failed to fetch privacy policy' },
      { status: 500 }
    );
  }
}