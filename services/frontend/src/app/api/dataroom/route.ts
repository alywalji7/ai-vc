import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * GET handler for listing all datarooms
 */
export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const companyId = url.pathname.split('/api/dataroom/')[1];
    
    let apiUrl: string;
    
    if (companyId) {
      // If we have a company ID, get that specific data room
      apiUrl = `${BACKEND_URL}/api/dataroom/${companyId}`;
    } else {
      // Otherwise, list all data rooms
      apiUrl = `${BACKEND_URL}/api/dataroom`;
    }
    
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Error fetching dataroom: ${response.statusText}` },
        { status: response.status }
      );
    }
    
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