'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function InvitePage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      setError('Please enter your email address.');
      return;
    }
    
    setLoading(true);
    setError('');
    setMessage('');
    
    try {
      const response = await fetch('/api/invite', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Something went wrong.');
      }
      
      setMessage('Check your email! We sent you a magic link to sign in.');
    } catch (err: any) {
      setError(err.message || 'Failed to send invite. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-6 text-center">Join the AI.VC Beta</h1>
      
      {message && (
        <div className="mb-4 p-3 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100 rounded">
          {message}
        </div>
      )}
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100 rounded">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="email" className="block mb-2 text-sm font-medium">
            Email Address
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md 
                       bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
            placeholder="you@example.com"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 
                     rounded-md transition duration-200 disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Get Magic Link'}
        </button>
      </form>
      
      <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
        <p>Already a member? <a href="/login" className="text-blue-600 dark:text-blue-400 hover:underline">Sign in</a></p>
      </div>
    </div>
  );
}