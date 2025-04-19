import { NextRequest, NextResponse } from 'next/server';

/**
 * Handle POST requests to launch due diligence
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { company_id, modules = ['financial', 'tech'] } = body;

    if (!company_id) {
      return NextResponse.json(
        { error: 'Company ID is required' },
        { status: 400 }
      );
    }

    // Call the backend service
    const response = await fetch(
      `http://localhost:8000/api/dd/launch?company_id=${company_id}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modules }),
        cache: 'no-store',
      }
    );

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
    console.error('Error launching due diligence:', error);
    return NextResponse.json(
      { error: 'An error occurred while launching due diligence' },
      { status: 500 }
    );
  }
}

/**
 * Handle GET requests to get due diligence results
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const company_id = searchParams.get('company_id');

    if (!company_id) {
      return NextResponse.json(
        { error: 'Company ID is required' },
        { status: 400 }
      );
    }

    // Call the backend service to get results
    const response = await fetch(
      `http://localhost:8000/api/dd/results?company_id=${company_id}`,
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
      { error: 'An error occurred while retrieving due diligence results' },
      { status: 500 }
    );
  }
}