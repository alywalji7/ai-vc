'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

export default function TermsPage() {
  const [termsContent, setTermsContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTerms = async () => {
      try {
        const response = await axios.get('/api/legal/terms');
        setTermsContent(response.data.content);
        setIsLoading(false);
      } catch (err) {
        console.error('Failed to fetch terms of service', err);
        setError('Failed to load terms of service. Please try again later.');
        setIsLoading(false);
      }
    };

    fetchTerms();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="p-4 bg-destructive/10 text-destructive rounded-md">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="prose dark:prose-invert max-w-none">
        <ReactMarkdown>{termsContent}</ReactMarkdown>
      </div>
    </div>
  );
}