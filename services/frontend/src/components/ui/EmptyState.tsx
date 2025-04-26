import React from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

type EmptyStateProps = {
  title: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  onAction?: () => void;
  className?: string;
  imageUrl?: string;
};

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  actionHref,
  onAction,
  className,
  imageUrl = '/empty-state-illustration.svg',
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-6 text-center rounded-lg border border-dashed border-gray-300 bg-gray-50 dark:bg-gray-900 dark:border-gray-700',
        className
      )}
    >
      {imageUrl && (
        <div className="mb-4 relative w-48 h-48">
          <Image 
            src={imageUrl} 
            alt="Empty state illustration" 
            fill
            className="object-contain"
          />
        </div>
      )}
      <h3 className="text-lg font-medium mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-muted-foreground mb-4 max-w-md">
          {description}
        </p>
      )}
      {actionLabel && (actionHref || onAction) && (
        <Button
          onClick={onAction}
          {...(actionHref && { as: 'a', href: actionHref })}
        >
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;