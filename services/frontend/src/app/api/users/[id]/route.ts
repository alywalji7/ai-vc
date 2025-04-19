import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const userId = params.id;
    
    const response = await fetch(`${backendUrl}/api/users/${userId}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: `Error fetching user: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Error fetching user:`, error);
    return NextResponse.json(
      { error: 'Failed to fetch user from backend' },
      { status: 500 }
    );
  }
}