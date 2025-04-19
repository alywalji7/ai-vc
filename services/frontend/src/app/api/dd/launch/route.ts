import { NextRequest, NextResponse } from 'next/server';

/**
 * Handle POST requests to launch due diligence
 */
export async function POST(request: NextRequest) {
  try {
    const { company_id, modules } = await request.json();

    // Validate required parameters
    if (!company_id) {
      return NextResponse.json(
        { error: 'Missing required parameter: company_id' },
        { status: 400 }
      );
    }

    // Construct the URL with query parameters
    let url = `http://localhost:8000/api/dd/launch?company_id=${encodeURIComponent(company_id)}`;
    
    // Add modules if provided
    if (modules && Array.isArray(modules) && modules.length > 0) {
      url += `&modules=${modules.map(m => encodeURIComponent(m)).join(',')}`;
    }

    // Call the backend service
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to launch due diligence' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in due diligence launch:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * Handle GET requests to get due diligence results
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const company_id = searchParams.get('company_id');

    // Validate required parameters
    if (!company_id) {
      return NextResponse.json(
        { error: 'Missing required parameter: company_id' },
        { status: 400 }
      );
    }

    // Call the backend service
    const response = await fetch(
      `http://localhost:8000/api/dd/results/${encodeURIComponent(company_id)}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to retrieve due diligence results' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error retrieving due diligence results:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}