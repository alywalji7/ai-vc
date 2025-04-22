import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${process.env.BETA_FEEDBACK_URL || 'http://localhost:8200'}/founders`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error fetching founder data:', errorText);
      return NextResponse.json(
        { message: 'Failed to fetch founder data' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Error in founder API:', error);
    return NextResponse.json(
      { message: error.message || 'An error occurred fetching founder data' },
      { status: 500 }
    );
  }
}