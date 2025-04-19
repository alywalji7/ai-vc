import { NextRequest, NextResponse } from 'next/server';

const SCHEDULER_API_URL = 'http://localhost:8085';

export async function GET(req: NextRequest) {
  try {
    const response = await fetch(`${SCHEDULER_API_URL}/tasks`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error fetching tasks: ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error proxying to scheduler service:', error);
    return NextResponse.json(
      { error: 'Failed to fetch tasks from scheduler service' },
      { status: 500 }
    );
  }
}