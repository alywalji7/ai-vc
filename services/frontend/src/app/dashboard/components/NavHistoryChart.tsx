import React, { useState } from 'react';
import { trpc } from '@/lib/trpc/client';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { ChartSkeleton } from '@/components/ui/SkeletonLoader';
import ErrorBoundary from '@/components/ui/ErrorBoundary';
import { cn } from '@/lib/utils';

type TimeframeOption = '1m' | '3m' | '6m' | '1y' | '3y' | 'all';

const timeframeOptions: { value: TimeframeOption; label: string }[] = [
  { value: '1m', label: '1M' },
  { value: '3m', label: '3M' },
  { value: '6m', label: '6M' },
  { value: '1y', label: '1Y' },
  { value: '3y', label: '3Y' },
  { value: 'all', label: 'All' },
];

interface NavHistoryChartProps {
  fundId?: string;
  className?: string;
}

const NavHistoryChart: React.FC<NavHistoryChartProps> = ({
  fundId,
  className,
}) => {
  const [timeframe, setTimeframe] = useState<TimeframeOption>('1y');
  
  const { data, isLoading, error } = trpc.dashboard.getNavHistory.useQuery({
    fundId,
    timeframe,
  });

  if (isLoading) {
    return <ChartSkeleton />;
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
        <h3 className="font-medium">Error loading NAV history</h3>
        <p className="text-sm mt-1">{error.message}</p>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
    return `$${value}`;
  };

  return (
    <div className={cn("rounded-lg border border-border p-4 bg-card", className)}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">NAV History</h3>
        <div className="flex space-x-1 bg-muted/50 rounded-md p-1">
          {timeframeOptions.map((option) => (
            <button
              key={option.value}
              className={cn(
                "px-2 py-1 text-xs font-medium rounded-md transition-colors",
                timeframe === option.value
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted text-muted-foreground"
              )}
              onClick={() => setTimeframe(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="navGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--brand-primary))" stopOpacity={0.8} />
                <stop offset="95%" stopColor="hsl(var(--brand-primary))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis
              dataKey="date"
              stroke="var(--muted-foreground)"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              tickFormatter={formatCurrency}
              stroke="var(--muted-foreground)"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              formatter={(value: number) => [formatCurrency(value), 'NAV']}
              contentStyle={{
                backgroundColor: 'hsl(var(--background))',
                borderColor: 'hsl(var(--border))',
                borderRadius: '0.375rem',
              }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="hsl(var(--brand-primary))"
              fillOpacity={1}
              fill="url(#navGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const NavHistoryChartWithErrorBoundary: React.FC<NavHistoryChartProps> = (props) => (
  <ErrorBoundary>
    <NavHistoryChart {...props} />
  </ErrorBoundary>
);

export default NavHistoryChartWithErrorBoundary;