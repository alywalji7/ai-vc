'use client';

import { useState } from 'react';
import FileUploader from '@/components/portfolio-upload/file-uploader';
import UploadedFiles from '@/components/portfolio-upload/uploaded-files';
import PortfolioSummary from '@/components/portfolio-upload/portfolio-summary';

export default function PortfolioPage() {
  // In a real implementation, this would come from authentication
  const lpId = 'current-user';
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'summary' | 'files'>('summary');
  const [notification, setNotification] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  const handleUploadComplete = () => {
    // Increment refresh trigger to cause components to refetch data
    setRefreshTrigger(prev => prev + 1);
    
    // Show success notification
    setNotification({
      type: 'success',
      message: 'File uploaded successfully! Processing your portfolio data...'
    });
    
    // Clear notification after 5 seconds
    setTimeout(() => {
      setNotification(null);
    }, 5000);
  };

  const handleUploadError = (error: string) => {
    // Show error notification
    setNotification({
      type: 'error',
      message: `Upload failed: ${error}`
    });
    
    // Clear notification after 5 seconds
    setTimeout(() => {
      setNotification(null);
    }, 5000);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Portfolio Manager</h1>
          <p className="text-muted-foreground">
            Upload and analyze your investment portfolio data
          </p>
        </div>
      </div>
      
      {notification && (
        <div 
          className={`mb-6 p-4 rounded-lg ${
            notification.type === 'success' 
              ? 'bg-green-100 border border-green-400 text-green-700 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800' 
              : 'bg-red-100 border border-red-400 text-red-700 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800'
          }`}
        >
          {notification.message}
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <FileUploader 
            lpId={lpId} 
            onUploadComplete={handleUploadComplete} 
            onUploadError={handleUploadError} 
          />
          
          <div className="mt-6">
            <UploadedFiles 
              lpId={lpId} 
              refreshTrigger={refreshTrigger} 
            />
          </div>
        </div>
        
        <div className="lg:col-span-2">
          <div className="bg-card p-6 rounded-lg border border-border mb-6">
            <div className="flex border-b border-border mb-6">
              <button
                className={`pb-3 px-4 text-sm font-medium ${
                  activeTab === 'summary'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
                onClick={() => setActiveTab('summary')}
              >
                Portfolio Summary
              </button>
              <button
                className={`pb-3 px-4 text-sm font-medium ${
                  activeTab === 'files'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
                onClick={() => setActiveTab('files')}
              >
                File Analysis
              </button>
            </div>
            
            {activeTab === 'summary' && (
              <PortfolioSummary 
                lpId={lpId} 
                refreshTrigger={refreshTrigger} 
              />
            )}
            
            {activeTab === 'files' && (
              <div className="text-center py-10">
                <h3 className="text-lg font-medium mb-2">File Analysis Coming Soon</h3>
                <p className="text-muted-foreground">
                  Detailed file analysis and document extraction features will be available in an upcoming release.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}