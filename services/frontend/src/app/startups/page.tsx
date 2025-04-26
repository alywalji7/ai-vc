'use client';

import React, { useState } from 'react';
import { api } from '@/lib/trpc/api';
import StartupCard from './components/StartupCard';
import FilterDrawer from './components/FilterDrawer';
import EmptyState from '@/components/ui/EmptyState';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function StartupsPage() {
  // Define default filter values
  const defaultFilters = {
    minScore: 0,
    sectors: [],
    geography: 'Global' as const,
    fundingStage: 'All',
    hasRevenueOnly: false,
  };

  // State for filter values
  const [filters, setFilters] = useState(defaultFilters);

  // Fetch startups data with the current filters
  const { data: startups, isLoading, error } = api.startup.getStartups.useQuery({
    minScore: filters.minScore,
    sectors: filters.sectors,
    geography: filters.geography !== 'Global' ? filters.geography : undefined,
    hasRevenue: filters.hasRevenueOnly,
  });

  // Handle filter changes
  const handleFiltersChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Startup Radar</h1>
          <p className="text-muted-foreground">
            Discover and track promising startups in our ecosystem
          </p>
        </div>
        <div className="flex items-center space-x-4 mt-4 md:mt-0">
          {/* Filter Drawer Component */}
          <FilterDrawer filters={filters} onFiltersChange={handleFiltersChange} />
          
          {/* Suggest New Startup Button */}
          <Button asChild>
            <Link href="/startups/suggest">
              <span className="flex items-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 mr-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Suggest Startup
              </span>
            </Link>
          </Button>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="text-center py-10">
          <h3 className="text-xl text-red-600 mb-2">Error loading startups</h3>
          <p className="text-muted-foreground">
            {error.message || 'Something went wrong. Please try again later.'}
          </p>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !error && startups && startups.length === 0 && (
        <EmptyState
          title="No startups found"
          description="No startups match your current filters. Try adjusting your filters to see more results."
          imageUrl="/illustrations/empty-search.svg"
          actionLabel="Clear Filters"
          actionHref="#"
          className="py-16"
        />
      )}

      {/* Grid of StartupCards */}
      {!isLoading && !error && startups && startups.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {startups.map((startup) => (
            <StartupCard key={startup.id} startup={startup} />
          ))}
        </div>
      )}
    </div>
  );
}