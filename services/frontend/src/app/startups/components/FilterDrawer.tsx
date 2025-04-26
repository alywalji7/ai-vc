import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Slider } from '@/components/ui/slider';
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@/components/ui/drawer';
import { MixerHorizontalIcon } from '@radix-ui/react-icons';
import { debounce } from '@/lib/utils';

export type FilterValues = {
  minScore: number;
  sectors: string[];
  geography?: 'USA' | 'EU' | 'APAC' | 'ROW';
};

type FilterDrawerProps = {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onFilterChange: (filters: FilterValues) => void;
  initialFilters: FilterValues;
  availableSectors: string[];
};

export const FilterDrawer: React.FC<FilterDrawerProps> = ({
  isOpen,
  onOpenChange,
  onFilterChange,
  initialFilters,
  availableSectors,
}) => {
  // Filter state
  const [minScore, setMinScore] = useState(initialFilters.minScore);
  const [selectedSectors, setSelectedSectors] = useState<string[]>(initialFilters.sectors);
  const [geography, setGeography] = useState<'USA' | 'EU' | 'APAC' | 'ROW' | undefined>(
    initialFilters.geography
  );

  // Update filters when external initialFilters change
  useEffect(() => {
    setMinScore(initialFilters.minScore);
    setSelectedSectors(initialFilters.sectors);
    setGeography(initialFilters.geography);
  }, [initialFilters]);

  // Debounced filter change handler
  const handleFilterChange = debounce(() => {
    onFilterChange({
      minScore,
      sectors: selectedSectors,
      geography,
    });
  }, 300);

  // Handle filter changes
  useEffect(() => {
    handleFilterChange();
  }, [minScore, selectedSectors, geography]);

  // Toggle sector selection
  const toggleSector = (sector: string, checked: boolean) => {
    if (checked) {
      setSelectedSectors((prev) => [...prev, sector]);
    } else {
      setSelectedSectors((prev) => prev.filter((s) => s !== sector));
    }
  };

  // Reset filters
  const resetFilters = () => {
    setMinScore(0.5);
    setSelectedSectors([]);
    setGeography(undefined);
  };

  return (
    <Drawer open={isOpen} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Filter Startups</DrawerTitle>
          <DrawerDescription>
            Apply filters to find startups that match your criteria.
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4 py-2 space-y-6">
          {/* Score Filter */}
          <div className="space-y-2">
            <Label htmlFor="score-filter" className="text-sm font-medium">
              Minimum Radar Score: {Math.round(minScore * 100)}%
            </Label>
            <Slider
              id="score-filter"
              min={0}
              max={1}
              step={0.05}
              value={[minScore]}
              onValueChange={(values) => setMinScore(values[0])}
              className="w-full"
            />
          </div>

          {/* Geography Filter */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Geography</Label>
            <RadioGroup
              value={geography || ''}
              onValueChange={(value) => setGeography(value ? value as any : undefined)}
              className="flex flex-col space-y-1 mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="USA" id="usa" />
                <Label htmlFor="usa" className="text-sm">United States</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="EU" id="eu" />
                <Label htmlFor="eu" className="text-sm">Europe</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="APAC" id="apac" />
                <Label htmlFor="apac" className="text-sm">Asia-Pacific</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="ROW" id="row" />
                <Label htmlFor="row" className="text-sm">Rest of World</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="" id="all-regions" />
                <Label htmlFor="all-regions" className="text-sm">All Regions</Label>
              </div>
            </RadioGroup>
          </div>

          {/* Sectors Filter */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Sectors</Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {availableSectors.map((sector) => (
                <div key={sector} className="flex items-start space-x-2">
                  <Checkbox
                    id={sector}
                    checked={selectedSectors.includes(sector)}
                    onCheckedChange={(checked) => toggleSector(sector, !!checked)}
                  />
                  <Label htmlFor={sector} className="text-sm">
                    {sector}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        </div>
        <DrawerFooter>
          <Button variant="outline" onClick={resetFilters}>
            Reset Filters
          </Button>
          <DrawerClose asChild>
            <Button>Apply Filters</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
};

// Separate component for filter trigger button
export const FilterTrigger: React.FC<{
  onClick: () => void;
  activeFilters: number;
}> = ({ onClick, activeFilters }) => {
  return (
    <Button
      onClick={onClick}
      variant="outline"
      size="sm"
      className="flex items-center gap-2"
    >
      <MixerHorizontalIcon className="h-4 w-4" />
      <span>Filter</span>
      {activeFilters > 0 && (
        <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
          {activeFilters}
        </span>
      )}
    </Button>
  );
};

export default FilterDrawer;