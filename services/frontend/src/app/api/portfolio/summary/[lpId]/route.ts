import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: { lpId: string } }
) {
  try {
    // Check if the user is authenticated (simplified)
    // In a real app, this would use the auth session
    const isAuthenticated = true;
    
    if (!isAuthenticated) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }
    
    const lpId = params.lpId;
    
    if (!lpId) {
      return NextResponse.json(
        { error: 'LP ID is required' },
        { status: 400 }
      );
    }
    
    // For demo purposes, we'll return mock data
    // In a real app, this would fetch from the backend API
    // Mock data for development until the backend API is ready
    const mockSummary = {
      totalValue: 18750000,
      totalCompanies: 43,
      totalFunds: 12,
      totalDeals: 55,
      assetAllocation: [
        {
          category: 'Direct Investments',
          value: 10500000,
          percentage: 0.56
        },
        {
          category: 'Venture Funds',
          value: 5250000,
          percentage: 0.28
        },
        {
          category: 'Growth Equity',
          value: 2250000,
          percentage: 0.12
        },
        {
          category: 'Private Credit',
          value: 750000,
          percentage: 0.04
        }
      ],
      industryExposure: [
        {
          industry: 'Software & SaaS',
          value: 8625000,
          percentage: 0.46
        },
        {
          industry: 'Fintech',
          value: 3750000,
          percentage: 0.2
        },
        {
          industry: 'Healthcare',
          value: 2625000,
          percentage: 0.14
        },
        {
          industry: 'Consumer',
          value: 1875000,
          percentage: 0.1
        },
        {
          industry: 'Infrastructure',
          value: 1125000,
          percentage: 0.06
        },
        {
          industry: 'Other',
          value: 750000,
          percentage: 0.04
        }
      ],
      performanceMetrics: {
        irr: 0.24,
        moic: 2.8,
        tvpi: 1.9,
        dpi: 0.6
      },
      lastUpdated: new Date().toISOString()
    };
    
    // In a production environment, uncomment and use the code below
    // const response = await fetch(`http://localhost:8500/api/v1/portfolio/summary/${lpId}`);
    // 
    // if (!response.ok) {
    //   return NextResponse.json(
    //     { error: 'Failed to fetch portfolio summary' },
    //     { status: response.status }
    //   );
    // }
    // 
    // const data = await response.json();
    // return NextResponse.json(data);
    
    return NextResponse.json(mockSummary);
  } catch (error: any) {
    console.error('Error fetching portfolio summary:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch portfolio summary' },
      { status: 500 }
    );
  }
}