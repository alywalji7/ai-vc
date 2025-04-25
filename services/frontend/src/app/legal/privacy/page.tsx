'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

export default function PrivacyPage() {
  const [privacyContent, setPrivacyContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPrivacy = async () => {
      try {
        const response = await axios.get('/api/legal/privacy');
        setPrivacyContent(response.data.content);
        setIsLoading(false);
      } catch (err) {
        console.error('Failed to fetch privacy policy', err);
        setError('Failed to load privacy policy. Please try again later.');
        setIsLoading(false);
      }
    };

    fetchPrivacy();
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
        <ReactMarkdown>{privacyContent}</ReactMarkdown>
      </div>
    </div>
  );
}