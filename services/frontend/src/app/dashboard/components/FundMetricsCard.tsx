import React from 'react';
import { trpc } from '@/lib/trpc/client';
import { CardSkeleton, MetricsSkeleton } from '@/components/ui/SkeletonLoader';
import ErrorBoundary from '@/components/ui/ErrorBoundary';
import { cn } from '@/lib/utils';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface FundMetricsCardProps {
  fundId?: string;
  className?: string;
}

const FundMetricsCard: React.FC<FundMetricsCardProps> = ({
  fundId,
  className,
}) => {
  const { data, isLoading, error } = trpc.dashboard.getFundMetrics.useQuery({
    fundId,
  });

  if (isLoading) {
    return <div className="space-y-8"><MetricsSkeleton /><CardSkeleton /></div>;
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
        <h3 className="font-medium">Error loading fund metrics</h3>
        <p className="text-sm mt-1">{error.message}</p>
      </div>
    );
  }

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${(value * 100).toFixed(1)}%`;
  };

  // Transform data for bar chart
  const performanceData = [
    {
      name: '1M',
      value: data.performance.oneMonth * 100,
    },
    {
      name: '3M',
      value: data.performance.threeMonth * 100,
    },
    {
      name: 'YTD',
      value: data.performance.ytd * 100,
    },
    {
      name: '1Y',
      value: data.performance.oneYear * 100,
    },
    {
      name: 'Since Inception',
      value: data.performance.sinceInception * 100,
    },
  ];

  const benchmarkData = [
    {
      name: 'VC Benchmark',
      fund: data.performance.oneYear * 100,
      benchmark: data.benchmarks.vc * 100,
    },
    {
      name: 'S&P 500',
      fund: data.performance.oneYear * 100,
      benchmark: data.benchmarks.sp500 * 100,
    },
    {
      name: 'NASDAQ',
      fund: data.performance.oneYear * 100,
      benchmark: data.benchmarks.nasdaq * 100,
    },
  ];

  return (
    <div className={cn("space-y-8", className)}>
      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">1 Month</h3>
          <p className={cn(
            "text-2xl font-bold",
            data.performance.oneMonth > 0 ? "text-green-600 dark:text-green-400" :
            data.performance.oneMonth < 0 ? "text-red-600 dark:text-red-400" : "text-foreground"
          )}>
            {formatPercentage(data.performance.oneMonth)}
          </p>
        </div>
        
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">3 Months</h3>
          <p className={cn(
            "text-2xl font-bold",
            data.performance.threeMonth > 0 ? "text-green-600 dark:text-green-400" :
            data.performance.threeMonth < 0 ? "text-red-600 dark:text-red-400" : "text-foreground"
          )}>
            {formatPercentage(data.performance.threeMonth)}
          </p>
        </div>
        
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">YTD</h3>
          <p className={cn(
            "text-2xl font-bold",
            data.performance.ytd > 0 ? "text-green-600 dark:text-green-400" :
            data.performance.ytd < 0 ? "text-red-600 dark:text-red-400" : "text-foreground"
          )}>
            {formatPercentage(data.performance.ytd)}
          </p>
        </div>
        
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">1 Year</h3>
          <p className={cn(
            "text-2xl font-bold",
            data.performance.oneYear > 0 ? "text-green-600 dark:text-green-400" :
            data.performance.oneYear < 0 ? "text-red-600 dark:text-red-400" : "text-foreground"
          )}>
            {formatPercentage(data.performance.oneYear)}
          </p>
        </div>
        
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">Since Inception</h3>
          <p className={cn(
            "text-2xl font-bold",
            data.performance.sinceInception > 0 ? "text-green-600 dark:text-green-400" :
            data.performance.sinceInception < 0 ? "text-red-600 dark:text-red-400" : "text-foreground"
          )}>
            {formatPercentage(data.performance.sinceInception)}
          </p>
        </div>
      </div>

      {/* Fund vs Benchmarks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Performance by Time Period</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                data={performanceData}
                margin={{ top: 10, right: 10, left: 0, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis 
                  dataKey="name" 
                  stroke="var(--muted-foreground)"
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  tickMargin={10}
                />
                <YAxis 
                  tickFormatter={(value) => `${value}%`}
                  stroke="var(--muted-foreground)"
                  fontSize={12}
                />
                <Tooltip 
                  formatter={(value: number) => [`${value.toFixed(1)}%`, 'Return']}
                  contentStyle={{
                    backgroundColor: 'hsl(var(--background))',
                    borderColor: 'hsl(var(--border))',
                    borderRadius: '0.375rem',
                  }}
                />
                <Bar 
                  dataKey="value" 
                  fill="hsl(var(--brand-primary))"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Fund vs. Benchmarks (1Y)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                data={benchmarkData}
                margin={{ top: 10, right: 10, left: 0, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis 
                  dataKey="name" 
                  stroke="var(--muted-foreground)"
                  fontSize={12}
                />
                <YAxis 
                  tickFormatter={(value) => `${value}%`}
                  stroke="var(--muted-foreground)"
                  fontSize={12}
                />
                <Tooltip 
                  formatter={(value: number) => [`${value.toFixed(1)}%`, '']}
                  contentStyle={{
                    backgroundColor: 'hsl(var(--background))',
                    borderColor: 'hsl(var(--border))',
                    borderRadius: '0.375rem',
                  }}
                />
                <Legend />
                <Bar 
                  name="Fund" 
                  dataKey="fund" 
                  fill="hsl(var(--brand-primary))" 
                  radius={[4, 4, 0, 0]}
                />
                <Bar 
                  name="Benchmark" 
                  dataKey="benchmark" 
                  fill="hsl(var(--brand-accent))" 
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Gainers and Losers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Top Gainers (YTD)</h3>
          <div className="space-y-2">
            {data.topGainers.map((item, index) => (
              <div key={index} className="flex justify-between items-center border-b border-border pb-2 last:border-0">
                <span className="text-sm">{item.name}</span>
                <span className="text-sm font-medium text-green-600 dark:text-green-400">
                  {formatPercentage(item.gain)}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Top Losers (YTD)</h3>
          <div className="space-y-2">
            {data.topLosers.map((item, index) => (
              <div key={index} className="flex justify-between items-center border-b border-border pb-2 last:border-0">
                <span className="text-sm">{item.name}</span>
                <span className="text-sm font-medium text-red-600 dark:text-red-400">
                  {formatPercentage(item.gain)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const FundMetricsCardWithErrorBoundary: React.FC<FundMetricsCardProps> = (props) => (
  <ErrorBoundary>
    <FundMetricsCard {...props} />
  </ErrorBoundary>
);

export default FundMetricsCardWithErrorBoundary;