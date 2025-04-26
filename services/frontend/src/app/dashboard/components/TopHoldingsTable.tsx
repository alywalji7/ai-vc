import React from 'react';
import { trpc } from '@/lib/trpc/client';
import { TableSkeleton } from '@/components/ui/SkeletonLoader';
import ErrorBoundary from '@/components/ui/ErrorBoundary';
import { cn } from '@/lib/utils';

interface TopHoldingsTableProps {
  fundId?: string;
  className?: string;
  limit?: number;
}

const TopHoldingsTable: React.FC<TopHoldingsTableProps> = ({
  fundId,
  className,
  limit = 5,
}) => {
  const { data, isLoading, error } = trpc.dashboard.getTopHoldings.useQuery({
    fundId,
    limit,
  });

  if (isLoading) {
    return <TableSkeleton rows={limit} columns={5} />;
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
        <h3 className="font-medium">Error loading top holdings</h3>
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

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  return (
    <div className={cn("rounded-lg border border-border bg-card overflow-hidden", className)}>
      <div className="p-4 border-b border-border">
        <h3 className="text-lg font-semibold">Top Holdings</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-full divide-y divide-border">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Company
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Sector
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Value
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                MOIC
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                % of NAV
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Change (QTD)
              </th>
            </tr>
          </thead>
          <tbody className="bg-card divide-y divide-border">
            {data?.map((holding) => (
              <tr key={holding.id} className="hover:bg-muted/50 transition-colors">
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium">{holding.name}</div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="text-sm text-muted-foreground">{holding.sector}</div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className="text-sm">{formatCurrency(holding.value)}</div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div 
                    className={cn(
                      "text-sm",
                      holding.moic >= 2 ? "text-green-600 dark:text-green-400" :
                      holding.moic >= 1 ? "text-blue-600 dark:text-blue-400" :
                      "text-red-600 dark:text-red-400"
                    )}
                  >
                    {holding.moic.toFixed(1)}x
                  </div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div className="text-sm">{holding.percentOfNav.toFixed(1)}%</div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-right">
                  <div 
                    className={cn(
                      "text-sm",
                      holding.changeQuarter > 0 ? "text-green-600 dark:text-green-400" :
                      holding.changeQuarter < 0 ? "text-red-600 dark:text-red-400" :
                      "text-muted-foreground"
                    )}
                  >
                    {formatPercentage(holding.changeQuarter)}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const TopHoldingsTableWithErrorBoundary: React.FC<TopHoldingsTableProps> = (props) => (
  <ErrorBoundary>
    <TopHoldingsTable {...props} />
  </ErrorBoundary>
);

export default TopHoldingsTableWithErrorBoundary;