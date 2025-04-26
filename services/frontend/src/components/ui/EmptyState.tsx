'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Button } from './button';

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
  imageUrl?: string;
  className?: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  actionHref,
  imageUrl,
  className,
}) => {
  return (
    <div className={`flex flex-col items-center justify-center text-center p-8 ${className}`}>
      {imageUrl && (
        <div className="relative w-40 h-40 mb-6">
          <Image 
            src={imageUrl} 
            alt="Empty state illustration" 
            fill 
            className="object-contain"
          />
        </div>
      )}
      
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground mb-6 max-w-md mx-auto">{description}</p>
      
      {actionLabel && actionHref && (
        <Button asChild>
          <Link href={actionHref}>
            {actionLabel}
          </Link>
        </Button>
      )}
    </div>
  );
};

export default EmptyState;