'use client';

import { useState, useEffect } from 'react';
import { getPortfolioFiles, getPortfolioFileDetails } from '@/app/api/portfolio/utils';
import { FileIcon, ExclamationTriangleIcon, UpdateIcon, CheckCircledIcon } from '@radix-ui/react-icons';

interface UploadedFilesProps {
  lpId: string;
  refreshTrigger: number;
}

interface FileRecord {
  id: number;
  filename: string;
  uploadDate: string;
  status: 'completed' | 'processing' | 'failed';
  fileType: string;
  fileSize: number;
}

interface FileDetails {
  id: number;
  filename: string;
  uploadDate: string;
  status: 'completed' | 'processing' | 'failed';
  fileType: string;
  fileSize: number;
  rowsProcessed: number | null;
  holdingsCount: number | null;
  fundsCount: number | null;
  processingTime: number | null;
  errors: string[];
}

export default function UploadedFiles({ lpId, refreshTrigger }: UploadedFilesProps) {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<number | null>(null);
  const [selectedFileDetails, setSelectedFileDetails] = useState<FileDetails | null>(null);
  const [isLoadingFiles, setIsLoadingFiles] = useState<boolean>(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    async function fetchFiles() {
      setIsLoadingFiles(true);
      setError(null);
      
      try {
        const data = await getPortfolioFiles(lpId);
        setFiles(data);
      } catch (error: any) {
        setError(error.message || 'Failed to fetch files');
      } finally {
        setIsLoadingFiles(false);
      }
    }
    
    if (lpId) {
      fetchFiles();
    }
  }, [lpId, refreshTrigger]);
  
  useEffect(() => {
    async function fetchFileDetails() {
      if (!selectedFileId) return;
      
      setIsLoadingDetails(true);
      
      try {
        const details = await getPortfolioFileDetails(selectedFileId);
        setSelectedFileDetails(details);
      } catch (error: any) {
        console.error('Error fetching file details:', error);
      } finally {
        setIsLoadingDetails(false);
      }
    }
    
    fetchFileDetails();
  }, [selectedFileId]);
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };
  
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(1)} MB`;
  };
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircledIcon className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <UpdateIcon className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'failed':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };
  
  const getFileIconColor = (fileType: string) => {
    switch (fileType) {
      case 'csv':
        return 'text-green-500';
      case 'xlsx':
        return 'text-blue-500';
      case 'pdf':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };
  
  if (isLoadingFiles) {
    return (
      <div className="p-6 border border-border rounded-lg bg-card">
        <h2 className="text-xl font-semibold mb-4">Uploaded Files</h2>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex p-3 border border-border rounded-md">
              <div className="w-8 h-8 bg-muted rounded-md mr-3"></div>
              <div className="flex-1">
                <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-muted rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-6 border border-border rounded-lg bg-card">
        <h2 className="text-xl font-semibold mb-4">Uploaded Files</h2>
        <div className="p-4 border border-red-200 rounded-lg bg-red-50 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
          <div className="flex items-center mb-2">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            <p className="font-medium">Error Loading Files</p>
          </div>
          <p>{error}</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="p-6 border border-border rounded-lg bg-card">
      <h2 className="text-xl font-semibold mb-4">Uploaded Files</h2>
      
      {files.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-6 border border-dashed border-border rounded-lg bg-muted/30">
          <FileIcon className="h-10 w-10 text-muted-foreground mb-3" />
          <p className="text-muted-foreground text-center">
            No files uploaded yet. Use the uploader above to add files.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {files.map((file) => (
            <div
              key={file.id}
              className={`flex items-center p-4 border rounded-lg cursor-pointer transition hover:shadow-sm ${
                selectedFileId === file.id 
                  ? 'border-primary bg-primary/5' 
                  : 'border-border hover:border-primary/50'
              }`}
              onClick={() => setSelectedFileId(file.id === selectedFileId ? null : file.id)}
            >
              <div className={`flex items-center justify-center h-10 w-10 rounded-lg mr-4 ${getFileIconColor(file.fileType)} bg-opacity-10`}>
                <FileIcon className="h-5 w-5" />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{file.filename}</p>
                <div className="flex items-center text-sm text-muted-foreground">
                  <span>{formatDate(file.uploadDate)}</span>
                  <span className="mx-1">•</span>
                  <span>{formatFileSize(file.fileSize)}</span>
                </div>
              </div>
              
              <div className="flex items-center ml-4">
                <div className="flex items-center mr-3">
                  {getStatusIcon(file.status)}
                  <span className="ml-1 text-sm capitalize">{file.status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {selectedFileId && selectedFileDetails && (
        <div className="mt-6 border border-border rounded-lg p-4">
          <h3 className="text-lg font-medium mb-3">File Details</h3>
          
          {isLoadingDetails ? (
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-muted rounded w-1/3 mb-3"></div>
              <div className="h-4 bg-muted rounded w-1/2 mb-3"></div>
              <div className="h-4 bg-muted rounded w-2/3 mb-3"></div>
              <div className="h-4 bg-muted rounded w-1/4 mb-3"></div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <div className="flex items-center">
                    {getStatusIcon(selectedFileDetails.status)}
                    <span className="ml-1 capitalize">{selectedFileDetails.status}</span>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-muted-foreground">File Type</p>
                  <p className="capitalize">{selectedFileDetails.fileType}</p>
                </div>
                
                <div>
                  <p className="text-sm text-muted-foreground">Upload Date</p>
                  <p>{formatDate(selectedFileDetails.uploadDate)}</p>
                </div>
                
                <div>
                  <p className="text-sm text-muted-foreground">File Size</p>
                  <p>{formatFileSize(selectedFileDetails.fileSize)}</p>
                </div>
              </div>
              
              {selectedFileDetails.status === 'completed' && (
                <>
                  <div className="border-t border-border pt-4">
                    <h4 className="font-medium mb-3">Processing Results</h4>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Rows Processed</p>
                        <p>{selectedFileDetails.rowsProcessed}</p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-muted-foreground">Processing Time</p>
                        <p>{selectedFileDetails.processingTime} seconds</p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-muted-foreground">Holdings Found</p>
                        <p>{selectedFileDetails.holdingsCount}</p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-muted-foreground">Funds Found</p>
                        <p>{selectedFileDetails.fundsCount}</p>
                      </div>
                    </div>
                  </div>
                </>
              )}
              
              {selectedFileDetails.status === 'failed' && selectedFileDetails.errors.length > 0 && (
                <div className="border-t border-border pt-4">
                  <h4 className="font-medium text-red-500 mb-2">Errors</h4>
                  <ul className="text-sm space-y-1">
                    {selectedFileDetails.errors.map((error, index) => (
                      <li key={index} className="text-red-500">
                        <span className="mr-2">•</span>
                        {error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}