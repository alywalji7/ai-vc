'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { formatCurrency, formatPercent, formatDate, truncateText } from '@/lib/utils';

export interface StartupInfo {
  id: string;
  name: string;
  logoUrl: string;
  description: string;
  sector: string;
  location: string;
  radarScore: number;
  foundedDate: Date;
  latestFunding?: {
    amount: number;
    round: string;
    date: Date;
  };
}

interface StartupCardProps {
  startup: StartupInfo;
  className?: string;
}

const StartupCard: React.FC<StartupCardProps> = ({ startup, className }) => {
  // Function to determine the color based on radar score
  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card className={`overflow-hidden hover:shadow-md transition-shadow ${className}`}>
      <CardHeader className="p-4 pb-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative h-10 w-10 rounded-md bg-gray-100 overflow-hidden">
              {startup.logoUrl ? (
                <Image
                  src={startup.logoUrl}
                  alt={`${startup.name} logo`}
                  fill
                  className="object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-primary/10 text-primary font-bold">
                  {startup.name.substring(0, 2).toUpperCase()}
                </div>
              )}
            </div>
            <div>
              <h3 className="font-medium">{startup.name}</h3>
              <div className="text-sm text-muted-foreground">{startup.sector}</div>
            </div>
          </div>
          <div className={`text-lg font-bold ${getScoreColor(startup.radarScore)}`}>
            {formatPercent(startup.radarScore)}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-4">
        <p className="text-sm text-muted-foreground mb-3">
          {truncateText(startup.description, 120)}
        </p>
        
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-4 w-4 mr-1 text-muted-foreground" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" 
              />
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" 
              />
            </svg>
            <span>{startup.location}</span>
          </div>
          <div className="flex items-center">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-4 w-4 mr-1 text-muted-foreground" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" 
              />
            </svg>
            <span>Founded {formatDate(startup.foundedDate)}</span>
          </div>
        </div>
      </CardContent>
      
      <CardFooter className="p-4 pt-0 flex justify-between border-t">
        {startup.latestFunding ? (
          <div className="text-sm">
            <span className="text-muted-foreground">Latest Round:</span>{' '}
            <span className="font-medium">{startup.latestFunding.round} · {formatCurrency(startup.latestFunding.amount)}</span>
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">No funding data available</div>
        )}
        
        <Link 
          href={`/startups/${startup.id}`}
          className="text-primary text-sm font-medium hover:underline"
        >
          View Details
        </Link>
      </CardFooter>
    </Card>
  );
};

export default StartupCard;