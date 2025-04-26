'use client'

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import StartupCard, { Startup } from '@/app/startups/components/StartupCard';
import FilterDrawer, { FilterTrigger, FilterValues } from '@/app/startups/components/FilterDrawer';
import { Button } from '@/components/ui/button';
import { PlusIcon } from '@radix-ui/react-icons';
import { api } from '@/lib/trpc/api';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import EmptyState from '@/components/ui/EmptyState';

export default function StartupsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Filter drawer state
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  
  // Get filter values from URL params
  const minScore = searchParams.get('minScore') ? parseFloat(searchParams.get('minScore')!) : 0.5;
  const sectors = searchParams.get('sectors') ? searchParams.get('sectors')!.split(',') : [];
  const geography = searchParams.get('geography') as 'USA' | 'EU' | 'APAC' | 'ROW' | undefined;
  
  // Set up filter state
  const [filters, setFilters] = useState<FilterValues>({
    minScore,
    sectors,
    geography,
  });
  
  // Update URL when filters change
  const updateUrlParams = (filters: FilterValues) => {
    const params = new URLSearchParams();
    
    if (filters.minScore !== 0.5) {
      params.set('minScore', filters.minScore.toString());
    }
    
    if (filters.sectors.length > 0) {
      params.set('sectors', filters.sectors.join(','));
    }
    
    if (filters.geography) {
      params.set('geography', filters.geography);
    }
    
    const newUrl = params.toString() ? `?${params.toString()}` : '';
    router.push(`/startups${newUrl}`);
  };
  
  // Handle filter changes
  const handleFilterChange = (newFilters: FilterValues) => {
    setFilters(newFilters);
    updateUrlParams(newFilters);
  };
  
  // Count active filters
  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.minScore > 0.5) count++;
    if (filters.sectors.length > 0) count++;
    if (filters.geography) count++;
    return count;
  };
  
  // Fetch startups based on filters
  const { data: startups, isLoading, error } = useQuery({
    queryKey: ['startups', filters],
    queryFn: async () => {
      // Call API to fetch startups with filters
      // For now, return mock data
      return await api.startup.getStartups.query(filters);
    },
  });
  
  // Fetch available sectors for filter
  const { data: sectorData } = useQuery({
    queryKey: ['sectors'],
    queryFn: async () => {
      // Call API to fetch available sectors
      return await api.startup.getSectors.query();
    },
  });
  
  const availableSectors = sectorData || [];
  
  // Handle card click
  const handleStartupClick = (id: string) => {
    router.push(`/startups/${id}`);
  };
  
  // Handle upvote
  const handleUpvote = (id: string) => {
    // Call API to upvote a startup
    api.startup.upvote.mutate({ id });
  };
  
  // Handle suggest new startup
  const handleSuggestClick = () => {
    router.push('/startups/suggest');
  };
  
  return (
    <div className="container py-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Startup Radar</h1>
        <div className="flex items-center gap-2">
          <FilterTrigger 
            onClick={() => setIsFilterOpen(true)} 
            activeFilters={getActiveFilterCount()} 
          />
          <Button onClick={handleSuggestClick} size="sm" className="flex items-center gap-1">
            <PlusIcon className="h-4 w-4" />
            <span>Suggest</span>
          </Button>
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center items-center py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="flex justify-center items-center py-20 text-red-500">
          Failed to load startups. Please try again.
        </div>
      ) : startups && startups.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {startups.map((startup) => (
            <StartupCard
              key={startup.id}
              startup={startup}
              onClick={handleStartupClick}
              onUpvote={handleUpvote}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No startups found"
          description="Try adjusting your filters or suggest a new startup to our database."
          action={
            <Button onClick={handleSuggestClick} className="mt-4">
              Suggest a Startup
            </Button>
          }
        />
      )}
      
      <FilterDrawer
        isOpen={isFilterOpen}
        onOpenChange={setIsFilterOpen}
        onFilterChange={handleFilterChange}
        initialFilters={filters}
        availableSectors={availableSectors}
      />
    </div>
  );
}