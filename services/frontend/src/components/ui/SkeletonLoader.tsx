import React from 'react';
import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "h-5 w-full animate-pulse rounded-md bg-muted/70",
        className
      )}
    />
  );
}

export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="w-full overflow-hidden rounded-lg border border-border">
      <div className="bg-muted/40 px-6 py-3">
        <div className="grid grid-cols-4 gap-4">
          {Array(columns)
            .fill(0)
            .map((_, i) => (
              <Skeleton
                key={i}
                className="h-4 w-24"
              />
            ))}
        </div>
      </div>
      <div className="divide-y divide-border">
        {Array(rows)
          .fill(0)
          .map((_, i) => (
            <div key={i} className="px-6 py-4">
              <div className="grid grid-cols-4 gap-4">
                {Array(columns)
                  .fill(0)
                  .map((_, j) => (
                    <Skeleton
                      key={j}
                      className="h-4 w-full"
                    />
                  ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="space-y-3 rounded-lg border border-border p-4">
      <Skeleton className="h-4 w-1/2" />
      <Skeleton className="h-8 w-1/4" />
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="space-y-4 rounded-lg border border-border p-4">
      <Skeleton className="h-4 w-1/4" />
      <div className="h-64 w-full animate-pulse rounded-md bg-muted/50" />
    </div>
  );
}

export function MetricsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array(4)
        .fill(0)
        .map((_, i) => (
          <CardSkeleton key={i} />
        ))}
    </div>
  );
}