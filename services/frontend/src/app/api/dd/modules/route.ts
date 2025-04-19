import { NextResponse } from 'next/server';

/**
 * Handle GET requests to get available due diligence modules
 */
export async function GET() {
  try {
    // Call the backend service
    const response = await fetch(
      'http://localhost:8000/api/dd/modules',
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
        { error: errorData.detail || 'Failed to retrieve available modules' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error retrieving available modules:', error);
    
    // Fallback to default modules if backend is not available
    return NextResponse.json({ 
      modules: ['financial', 'tech'] 
    });
  }
}