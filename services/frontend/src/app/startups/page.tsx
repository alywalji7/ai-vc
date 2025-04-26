'use client';

import React, { useState, useEffect } from 'react';
import { useDebounce } from '@/lib/hooks';
import { api } from '@/lib/trpc/api';
import StartupCard, { StartupInfo } from './components/StartupCard';
import FilterDrawer from './components/FilterDrawer';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import EmptyState from '@/components/ui/EmptyState';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

type StartupFilters = {
  minScore: number;
  sectors: string[];
  geography: 'USA' | 'Europe' | 'Asia' | 'LatAm' | 'Global';
  fundingStage: string;
  hasRevenueOnly: boolean;
};

export default function StartupsPage() {
  const [filters, setFilters] = useState<StartupFilters>({
    minScore: 0,
    sectors: [],
    geography: 'Global',
    fundingStage: 'All',
    hasRevenueOnly: false,
  });
  
  const debouncedFilters = useDebounce(filters, 300);
  
  // Fetch startups using tRPC
  const { data: startups, isLoading, error } = api.startup.getStartups.useQuery({
    minScore: debouncedFilters.minScore,
    sectors: debouncedFilters.sectors.length > 0 ? debouncedFilters.sectors : undefined,
    geography: debouncedFilters.geography !== 'Global' ? debouncedFilters.geography : undefined,
    hasRevenue: debouncedFilters.hasRevenueOnly ? true : undefined,
  }, {
    // Keep previous data while loading new data
    keepPreviousData: true,
  });
  
  // Handle filter changes
  const handleFiltersChange = (newFilters: StartupFilters) => {
    setFilters(newFilters);
  };
  
  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Startup Radar</h1>
        <div className="flex gap-4">
          <FilterDrawer 
            filters={filters}
            onFiltersChange={handleFiltersChange}
          />
          <Button asChild>
            <Link href="/startups/suggest">Suggest a Startup</Link>
          </Button>
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="text-center text-red-500 py-8">
          Error loading startups: {error.message}
        </div>
      ) : startups && startups.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {startups.map((startup) => (
            <StartupCard 
              key={startup.id} 
              startup={startup} 
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No startups found"
          description="Try adjusting your filters or suggesting a new startup to add to our radar."
          actionLabel="Suggest a Startup"
          actionHref="/startups/suggest"
          imageUrl="/empty-state-startups.svg"
        />
      )}
    </div>
  );
}