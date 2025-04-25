import { promises as fs } from 'fs';
import path from 'path';
import { NextRequest, NextResponse } from 'next/server';

/**
 * API route to fetch documentation content by slug
 * This reads MDX files from the docs/end-user directory
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string } }
) {
  try {
    const { slug } = params;
    const docsDirectory = path.join(process.cwd(), '../../docs/end-user');
    
    // Make sure the slug is valid (only alphanumeric and hyphens)
    if (!/^[a-z0-9-]+$/.test(slug)) {
      return NextResponse.json(
        { error: 'Invalid document slug' },
        { status: 400 }
      );
    }
    
    const filePath = path.join(docsDirectory, `${slug}.mdx`);
    
    try {
      const content = await fs.readFile(filePath, 'utf8');
      return NextResponse.json({ content });
    } catch (error) {
      console.error(`Error reading file ${filePath}:`, error);
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }
  } catch (error) {
    console.error('Error processing documentation request:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}