'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';
import { formatPercent } from '@/lib/utils';

// Define the type for the filter values
export interface FilterValues {
  minScore: number;
  sectors: string[];
  geography: 'USA' | 'Europe' | 'Asia' | 'LatAm' | 'Global';
  fundingStage: string;
  hasRevenueOnly: boolean;
}

interface FilterDrawerProps {
  filters: FilterValues;
  onFiltersChange: (filters: FilterValues) => void;
}

// Available sectors for filtering
const AVAILABLE_SECTORS = [
  'AI',
  'FinTech',
  'HealthTech',
  'EdTech',
  'CleanTech',
  'Hardware',
  'SaaS',
  'E-commerce',
  'Cybersecurity',
];

// Available funding stages
const FUNDING_STAGES = [
  'All',
  'Pre-seed',
  'Seed',
  'Series A',
  'Series B',
  'Series C+',
];

const FilterDrawer: React.FC<FilterDrawerProps> = ({ filters, onFiltersChange }) => {
  // Local state to track filter values while the drawer is open
  const [localFilters, setLocalFilters] = useState<FilterValues>(filters);
  
  // Handler for when the drawer is opened
  const handleOpenChange = (open: boolean) => {
    if (open) {
      // Reset local filters to match the current applied filters
      setLocalFilters(filters);
    }
  };
  
  // Handler for applying the filters
  const handleApplyFilters = () => {
    onFiltersChange(localFilters);
  };
  
  // Handler for clearing all filters
  const handleClearFilters = () => {
    const defaultFilters: FilterValues = {
      minScore: 0,
      sectors: [],
      geography: 'Global',
      fundingStage: 'All',
      hasRevenueOnly: false,
    };
    
    setLocalFilters(defaultFilters);
    onFiltersChange(defaultFilters);
  };
  
  // Handler for updating sector selection
  const handleSectorChange = (sector: string, checked: boolean) => {
    if (checked) {
      setLocalFilters({
        ...localFilters,
        sectors: [...localFilters.sectors, sector],
      });
    } else {
      setLocalFilters({
        ...localFilters,
        sectors: localFilters.sectors.filter((s) => s !== sector),
      });
    }
  };

  return (
    <Dialog onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-4 w-4" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" 
            />
          </svg>
          Filters
          {(filters.minScore > 0 || 
            filters.sectors.length > 0 || 
            filters.geography !== 'Global' || 
            filters.fundingStage !== 'All' || 
            filters.hasRevenueOnly) && (
            <span className="inline-flex items-center justify-center w-5 h-5 ml-1 text-xs font-semibold text-white bg-primary rounded-full">
              {(filters.minScore > 0 ? 1 : 0) + 
                (filters.sectors.length > 0 ? 1 : 0) + 
                (filters.geography !== 'Global' ? 1 : 0) + 
                (filters.fundingStage !== 'All' ? 1 : 0) + 
                (filters.hasRevenueOnly ? 1 : 0)}
            </span>
          )}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="sm:max-w-[500px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Filter Startups</DialogTitle>
          <DialogDescription>
            Select criteria to filter the startup list. Apply multiple filters to narrow your results.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-6 py-4">
          {/* Radar Score Filter */}
          <div className="space-y-2">
            <Label htmlFor="score-filter" className="block text-sm font-medium">
              Minimum Radar Score: {formatPercent(localFilters.minScore)}
            </Label>
            <Slider
              id="score-filter"
              min={0}
              max={1}
              step={0.01}
              value={[localFilters.minScore]}
              onValueChange={(values) => {
                setLocalFilters({ ...localFilters, minScore: values[0] });
              }}
              className="w-full"
            />
          </div>
          
          {/* Geography Filter */}
          <div className="space-y-2">
            <Label className="block text-sm font-medium">Geography</Label>
            <RadioGroup
              value={localFilters.geography}
              onValueChange={(value) => {
                setLocalFilters({ ...localFilters, geography: value as FilterValues['geography'] });
              }}
              className="grid grid-cols-3 gap-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="Global" id="global" />
                <Label htmlFor="global" className="cursor-pointer">Global</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="USA" id="usa" />
                <Label htmlFor="usa" className="cursor-pointer">USA</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="Europe" id="europe" />
                <Label htmlFor="europe" className="cursor-pointer">Europe</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="Asia" id="asia" />
                <Label htmlFor="asia" className="cursor-pointer">Asia</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="LatAm" id="latam" />
                <Label htmlFor="latam" className="cursor-pointer">LatAm</Label>
              </div>
            </RadioGroup>
          </div>
          
          {/* Funding Stage Filter */}
          <div className="space-y-2">
            <Label className="block text-sm font-medium">Funding Stage</Label>
            <RadioGroup
              value={localFilters.fundingStage}
              onValueChange={(value) => {
                setLocalFilters({ ...localFilters, fundingStage: value });
              }}
              className="grid grid-cols-3 gap-2"
            >
              {FUNDING_STAGES.map((stage) => (
                <div key={stage} className="flex items-center space-x-2">
                  <RadioGroupItem value={stage} id={stage.toLowerCase().replace(/\s+/g, '-')} />
                  <Label htmlFor={stage.toLowerCase().replace(/\s+/g, '-')} className="cursor-pointer">
                    {stage}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
          
          {/* Sectors Filter */}
          <div className="space-y-2">
            <Label className="block text-sm font-medium">Sectors</Label>
            <div className="grid grid-cols-2 gap-2">
              {AVAILABLE_SECTORS.map((sector) => (
                <div key={sector} className="flex items-center space-x-2">
                  <Checkbox
                    id={`sector-${sector.toLowerCase()}`}
                    checked={localFilters.sectors.includes(sector)}
                    onCheckedChange={(checked) => {
                      if (typeof checked === 'boolean') {
                        handleSectorChange(sector, checked);
                      }
                      return false;
                    }}
                  />
                  <Label htmlFor={`sector-${sector.toLowerCase()}`} className="cursor-pointer">
                    {sector}
                  </Label>
                </div>
              ))}
            </div>
          </div>
          
          {/* Revenue Filter */}
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="revenue-filter"
                checked={localFilters.hasRevenueOnly}
                onCheckedChange={(checked) => {
                  if (typeof checked === 'boolean') {
                    setLocalFilters({ ...localFilters, hasRevenueOnly: checked });
                  }
                  return false;
                }}
              />
              <Label htmlFor="revenue-filter" className="cursor-pointer">
                Show only startups with revenue
              </Label>
            </div>
          </div>
        </div>
        
        <DialogFooter className="flex sm:justify-between">
          <Button 
            variant="outline" 
            onClick={handleClearFilters}
            className="mr-auto"
          >
            Clear Filters
          </Button>
          
          <DialogClose asChild>
            <Button onClick={handleApplyFilters}>Apply Filters</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default FilterDrawer;