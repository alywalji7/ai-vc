'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function FounderSignupPage() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);
  
  // Form data
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [deckFile, setDeckFile] = useState<File | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  
  const handleNextStep = () => {
    if (step === 1) {
      if (!email || !name || !companyName) {
        setError('Please fill out all fields.');
        return;
      }
      setError('');
      setStep(2);
    }
  };
  
  const handlePrevStep = () => {
    setStep(1);
    setError('');
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      // Check if file is a PDF
      if (file.type !== 'application/pdf') {
        setError('Please upload a PDF file.');
        return;
      }
      
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10MB limit.');
        return;
      }
      
      setDeckFile(file);
      setError('');
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!deckFile) {
      setError('Please upload your pitch deck.');
      return;
    }
    
    setLoading(true);
    setError('');
    setMessage('');
    
    try {
      // Create form data for file upload
      const formData = new FormData();
      formData.append('email', email);
      formData.append('name', name);
      formData.append('companyName', companyName);
      formData.append('deck', deckFile);
      
      const response = await fetch('/api/founder-signup', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Something went wrong.');
      }
      
      setMessage('Your application has been submitted successfully! We will review it and get back to you soon.');
      
      // Reset form
      setEmail('');
      setName('');
      setCompanyName('');
      setDeckFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      // After 3 seconds, redirect to homepage
      setTimeout(() => {
        router.push('/');
      }, 3000);
      
    } catch (err: any) {
      setError(err.message || 'Failed to submit application. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-2xl mx-auto mt-10 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-6 text-center">Founder Application</h1>
      
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
      
      <div className="mb-8">
        <div className="flex items-center">
          <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
            step >= 1 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300 text-gray-500'
          }`}>
            1
          </div>
          <div className={`flex-1 h-1 mx-2 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
          <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
            step >= 2 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300 text-gray-500'
          }`}>
            2
          </div>
        </div>
        <div className="flex justify-between mt-2">
          <span className="text-sm">Basic Information</span>
          <span className="text-sm">Pitch Deck</span>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        {step === 1 && (
          <div>
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
            
            <div className="mb-4">
              <label htmlFor="name" className="block mb-2 text-sm font-medium">
                Your Name
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                placeholder="John Doe"
                required
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="companyName" className="block mb-2 text-sm font-medium">
                Company Name
              </label>
              <input
                type="text"
                id="companyName"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                placeholder="Startup Inc."
                required
              />
            </div>
            
            <button
              type="button"
              onClick={handleNextStep}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 
                         rounded-md transition duration-200"
            >
              Continue
            </button>
          </div>
        )}
        
        {step === 2 && (
          <div>
            <div className="mb-4">
              <label htmlFor="deck" className="block mb-2 text-sm font-medium">
                Upload Pitch Deck (PDF, max 10MB)
              </label>
              
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-6 text-center">
                <input
                  type="file"
                  id="deck"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".pdf"
                />
                
                {deckFile ? (
                  <div>
                    <p className="mb-2 text-sm text-gray-900 dark:text-gray-300">
                      <span className="font-semibold">Selected file:</span> {deckFile.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {(deckFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        setDeckFile(null);
                        if (fileInputRef.current) {
                          fileInputRef.current.value = '';
                        }
                      }}
                      className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
                    >
                      Remove
                    </button>
                  </div>
                ) : (
                  <div 
                    onClick={() => fileInputRef.current?.click()}
                    className="cursor-pointer"
                  >
                    <svg 
                      className="mx-auto h-12 w-12 text-gray-400" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path 
                        strokeLinecap="round" 
                        strokeLinejoin="round" 
                        strokeWidth="2" 
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      PDF up to 10MB
                    </p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={handlePrevStep}
                className="w-1/2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 
                           text-gray-800 dark:text-gray-200 font-medium py-2 px-4 rounded-md transition duration-200"
              >
                Back
              </button>
              
              <button
                type="submit"
                disabled={loading || !deckFile}
                className="w-1/2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 
                           rounded-md transition duration-200 disabled:opacity-50"
              >
                {loading ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}