import { NextRequest, NextResponse } from 'next/server';

/**
 * Proxy for the similarity API
 */
export async function POST(request: NextRequest) {
  try {
    const reqBody = await request.json();
    
    // Forward the request to the similarity API
    const response = await fetch(`${process.env.SIMILARITY_API_URL || 'http://localhost:8090'}/api/v1/similarity`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reqBody),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error from similarity API: ${errorText}`);
      return NextResponse.json(
        { error: 'Error calling similarity API', details: errorText },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in similarity API proxy:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: String(error) },
      { status: 500 }
    );
  }
}