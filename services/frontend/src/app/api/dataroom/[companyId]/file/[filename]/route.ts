import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * GET handler for retrieving a file from a dataroom
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { companyId: string; filename: string } }
) {
  try {
    const { companyId, filename } = params;
    
    // Build the API URL
    const apiUrl = `${BACKEND_URL}/api/dataroom/${companyId}/file/${filename}`;
    
    // Fetch the file from the backend
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Error fetching file: ${response.statusText}` },
        { status: response.status }
      );
    }
    
    // Get the content type
    const contentType = response.headers.get('content-type') || 'application/octet-stream';
    
    // Get the file as binary data
    const buffer = await response.arrayBuffer();
    
    // Return the file with the appropriate content type
    return new NextResponse(buffer, {
      status: 200,
      headers: {
        'Content-Type': contentType
      }
    });
  } catch (error) {
    console.error('Error in dataroom file API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}