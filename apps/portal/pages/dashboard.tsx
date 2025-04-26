import React from 'react';
import { useQuery } from '@tanstack/react-query';
import ErrorBoundary from '../components/ErrorBoundary';
import AreaChart from '../components/dashboard/AreaChart';
import BarChart from '../components/dashboard/BarChart';
import DataTable from '../components/dashboard/DataTable';

// Mock API client for demo purposes, in real app this would be a trpc client
const api = {
  fund: {
    getMetrics: async () => {
      // In a real app, this would be a trpc call
      const response = await fetch('/api/trpc/fund.getMetrics');
      const data = await response.json();
      return data.result.data.json;
    }
  }
};

export default function Dashboard() {
  // Fetch data
  const { data, isLoading, error } = useQuery({
    queryKey: ['fundMetrics'],
    queryFn: () => api.fund.getMetrics(),
  });

  // Error state
  if (error) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-6">Fund Dashboard</h1>
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
          <h3 className="text-lg font-medium mb-2">Error loading dashboard data</h3>
          <p className="text-sm">{error instanceof Error ? error.message : 'An unknown error occurred'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Fund Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* NAV Over Time Chart */}
        <ErrorBoundary>
          <AreaChart 
            data={data?.navOverTime || { dates: [], nav: [] }} 
            isLoading={isLoading} 
          />
        </ErrorBoundary>
        
        {/* Sector Allocation Chart */}
        <ErrorBoundary>
          <BarChart 
            data={data?.sectorAllocation || []} 
            isLoading={isLoading} 
          />
        </ErrorBoundary>
      </div>
      
      {/* Top Holdings Table */}
      <div className="mb-6">
        <ErrorBoundary>
          <DataTable 
            data={data?.topHoldings || []} 
            isLoading={isLoading} 
          />
        </ErrorBoundary>
      </div>
    </div>
  );
}