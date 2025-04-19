import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
console.log('BACKEND_URL is set to:', BACKEND_URL);

/**
 * GET handler for retrieving a list of all data rooms
 */
export async function GET(request: NextRequest) {
  try {
    // Build the API URL
    const apiUrl = `${BACKEND_URL}/api/dataroom`;
    
    console.log('Frontend API trying to fetch from:', apiUrl);
    
    // Fetch data from the backend with additional options
    const response = await fetch(apiUrl, {
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      },
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Error fetching datarooms: ${response.statusText}` },
        { status: response.status }
      );
    }
    
    // Return the data
    const data = await response.json();
    console.log('Frontend API received from backend:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in dataroom API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}