'use client';

import { TooltipProps } from 'recharts';
import { NameType, ValueType } from 'recharts/types/component/DefaultTooltipContent';
import { cn } from '@/lib/utils';

interface CustomTooltipProps extends TooltipProps<ValueType, NameType> {
  className?: string;
  showLabel?: boolean;
  valueFormatter?: (value: number) => string;
  labelFormatter?: (label: string) => string;
}

export const CustomTooltip = ({
  active,
  payload,
  label,
  className,
  showLabel = true,
  valueFormatter = (value: number) => `${value}`,
  labelFormatter = (label: string) => label,
}: CustomTooltipProps) => {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className={cn(
      "p-3 rounded-lg shadow-md border text-sm bg-background", 
      className
    )}>
      {showLabel && (
        <p className="font-medium text-foreground mb-1">
          {labelFormatter(String(label))}
        </p>
      )}
      <div className="space-y-1">
        {payload.map((item, index) => (
          <div key={`item-${index}`} className="flex items-center">
            <div 
              className="w-3 h-3 rounded-full mr-2"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-muted-foreground mr-2">
              {item.name}:
            </span>
            <span className="font-medium text-foreground">
              {valueFormatter(item.value as number)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};