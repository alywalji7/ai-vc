'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';

export default function SuccessPage() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (!sessionId) {
      setLoading(false);
      setError('No session ID found');
      return;
    }

    // Verify the payment was successful (in a real app)
    // Here we'll just simulate this with a timeout
    const timer = setTimeout(() => {
      setLoading(false);
      toast({
        title: 'Subscription activated',
        description: 'Your subscription has been successfully activated.',
        variant: 'success',
      });
    }, 1500);

    return () => clearTimeout(timer);
  }, [sessionId, toast]);

  if (loading) {
    return (
      <div className="container mx-auto max-w-md py-16 px-4 text-center">
        <div className="mb-8">
          <div className="mx-auto h-16 w-16 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
        </div>
        <h1 className="text-2xl font-bold mb-4">Processing your subscription</h1>
        <p className="text-muted-foreground">Please wait while we confirm your payment...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto max-w-md py-16 px-4 text-center">
        <div className="mb-8 text-destructive">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mx-auto h-16 w-16"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold mb-4">Something went wrong</h1>
        <p className="text-muted-foreground mb-8">{error}</p>
        <Link href="/pricing">
          <Button variant="default">Return to pricing</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-md py-16 px-4 text-center">
      <div className="mb-8 text-green-600">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="mx-auto h-16 w-16"
        >
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold mb-4">Thank you for subscribing!</h1>
      <p className="text-muted-foreground mb-8">
        Your subscription has been activated successfully. You now have access to all the features of your plan.
      </p>
      <div className="space-y-4">
        <Link href="/dashboard">
          <Button variant="default" className="w-full">Go to dashboard</Button>
        </Link>
        <Link href="/">
          <Button variant="outline" className="w-full">Return to home</Button>
        </Link>
      </div>
    </div>
  );
}