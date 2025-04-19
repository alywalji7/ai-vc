import { NextRequest, NextResponse } from 'next/server';

const SCHEDULER_API_URL = 'http://localhost:8085';

export async function POST(
  req: NextRequest,
  { params }: { params: { taskName: string } }
) {
  try {
    const { taskName } = params;
    
    const response = await fetch(`${SCHEDULER_API_URL}/tasks/${taskName}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error running task: ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error proxying to scheduler service:', error);
    return NextResponse.json(
      { error: 'Failed to run task through scheduler service' },
      { status: 500 }
    );
  }
}