import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * GET handler for retrieving dataroom by company ID
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { companyId: string } }
) {
  try {
    const companyId = params.companyId;
    const url = new URL(request.url);
    const segments = url.pathname.split('/');
    
    let apiPath: string;
    
    // Check if this is a request for a file or data
    if (segments.includes('file')) {
      // Extract filename from the URL path
      const fileIndex = segments.indexOf('file');
      if (fileIndex !== -1 && fileIndex < segments.length - 1) {
        const filename = segments[fileIndex + 1];
        apiPath = `/api/dataroom/${companyId}/file/${filename}`;
      } else {
        return NextResponse.json(
          { error: 'Invalid file request' },
          { status: 400 }
        );
      }
    } else if (segments.includes('data')) {
      apiPath = `/api/dataroom/${companyId}/data`;
    } else {
      apiPath = `/api/dataroom/${companyId}`;
    }
    
    const response = await fetch(`${BACKEND_URL}${apiPath}`);
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Error fetching dataroom: ${response.statusText}` },
        { status: response.status }
      );
    }
    
    // For file content, pass through the raw response
    if (segments.includes('file')) {
      const contentType = response.headers.get('content-type') || 'application/octet-stream';
      const buffer = await response.arrayBuffer();
      
      return new NextResponse(buffer, {
        status: 200,
        headers: {
          'Content-Type': contentType
        }
      });
    }
    
    // For JSON data, return as JSON
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in dataroom API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}