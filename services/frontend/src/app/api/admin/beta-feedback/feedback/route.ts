import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${process.env.BETA_FEEDBACK_URL || 'http://localhost:8200'}/feedback`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error fetching feedback data:', errorText);
      return NextResponse.json(
        { message: 'Failed to fetch feedback data' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Error in feedback API:', error);
    return NextResponse.json(
      { message: error.message || 'An error occurred fetching feedback data' },
      { status: 500 }
    );
  }
}