import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const limit = searchParams.get('limit') || '10';

  try {
    // Forward the request to the radar service
    const response = await fetch(`http://localhost:8095/radar/daily_shortlist?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Radar service responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching radar data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch radar data', details: (error as Error).message },
      { status: 500 }
    );
  }
}