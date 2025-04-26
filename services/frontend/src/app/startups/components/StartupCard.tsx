import React from 'react';
import Image from 'next/image';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { CaretUpIcon } from '@radix-ui/react-icons';

export type Startup = {
  id: string;
  name: string;
  logoUrl: string | null;
  sector: string;
  radarScore: number;
  geography: 'USA' | 'EU' | 'APAC' | 'ROW';
  upvotes: number;
  description: string;
  founded: number;
  website: string;
};

type StartupCardProps = {
  startup: Startup;
  onClick: (id: string) => void;
  onUpvote: (id: string) => void;
  className?: string;
};

const StartupCard: React.FC<StartupCardProps> = ({ 
  startup, 
  onClick, 
  onUpvote,
  className 
}) => {
  const handleClick = () => {
    onClick(startup.id);
  };
  
  const handleUpvoteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onUpvote(startup.id);
  };
  
  // Format radar score as percentage
  const scorePercentage = Math.round(startup.radarScore * 100);
  
  // Determine score color based on value
  const getScoreColor = () => {
    if (scorePercentage >= 85) return 'text-green-600 bg-green-100';
    if (scorePercentage >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };
  
  return (
    <Card 
      className={cn("cursor-pointer hover:shadow-md transition-shadow", className)}
      onClick={handleClick}
    >
      <CardHeader className="p-4 pb-0 flex flex-row justify-between items-start">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-md bg-slate-100 flex items-center justify-center relative overflow-hidden">
            {startup.logoUrl ? (
              <Image 
                src={startup.logoUrl} 
                alt={startup.name} 
                fill 
                className="object-cover"
              />
            ) : (
              <span className="text-xl font-semibold text-slate-400">
                {startup.name.charAt(0)}
              </span>
            )}
          </div>
          <div>
            <h3 className="font-semibold text-base">{startup.name}</h3>
            <p className="text-sm text-muted-foreground">Est. {startup.founded}</p>
          </div>
        </div>
        <Badge variant="outline" className={cn("ml-auto rounded-full px-2", getScoreColor())}>
          {scorePercentage}%
        </Badge>
      </CardHeader>
      
      <CardContent className="p-4 pt-3">
        <p className="text-sm line-clamp-2 min-h-[40px]">
          {startup.description}
        </p>
        <div className="flex gap-2 mt-3">
          <Badge className="rounded-full text-xs">{startup.sector}</Badge>
          <Badge variant="secondary" className="rounded-full text-xs">
            {startup.geography}
          </Badge>
        </div>
      </CardContent>
      
      <CardFooter className="p-4 pt-0 flex justify-between items-center">
        <a 
          href={startup.website} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-xs text-blue-600 hover:underline"
          onClick={(e) => e.stopPropagation()}
        >
          {startup.website.replace(/^https?:\/\/(www\.)?/, '')}
        </a>
        <Button 
          variant="ghost" 
          size="sm"
          className="flex items-center gap-1 text-xs" 
          onClick={handleUpvoteClick}
        >
          {/* @ts-ignore - We'll fix the icon type issue later */}
          <CaretUpIcon className="h-4 w-4" />
          {startup.upvotes}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default StartupCard;