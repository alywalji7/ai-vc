'use client';

import { useState, useRef } from 'react';
import { uploadPortfolioFile } from '@/app/api/portfolio/utils';
import { UploadIcon, CrossCircledIcon, FilePlusIcon } from '@radix-ui/react-icons';

interface FileUploaderProps {
  lpId: string;
  onUploadComplete: () => void;
  onUploadError: (error: string) => void;
}

export default function FileUploader({ 
  lpId, 
  onUploadComplete, 
  onUploadError 
}: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFile(files[0]);
    }
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };
  
  const processFile = (file: File) => {
    // Check file type
    const allowedTypes = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      onUploadError('Invalid file type. Only CSV, XLSX, and PDF files are supported.');
      return;
    }
    
    // Check file size (limit to 10MB)
    const maxSize = 10 * 1024 * 1024; // 10 MB
    if (file.size > maxSize) {
      onUploadError('File size exceeds the 10MB limit');
      return;
    }
    
    setSelectedFile(file);
  };
  
  const handleUpload = async () => {
    if (!selectedFile) {
      onUploadError('No file selected');
      return;
    }
    
    setIsUploading(true);
    
    try {
      await uploadPortfolioFile(selectedFile, lpId);
      setSelectedFile(null);
      onUploadComplete();
    } catch (error: any) {
      onUploadError(error.message || 'Failed to upload file');
    } finally {
      setIsUploading(false);
    }
  };
  
  const handleCancel = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(1)} MB`;
  };
  
  return (
    <div className="w-full p-6 border border-border rounded-lg bg-card">
      <h2 className="text-xl font-semibold mb-4">Upload Portfolio File</h2>
      
      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragging 
              ? 'border-primary bg-primary/5' 
              : 'border-border hover:border-primary/50 hover:bg-muted/50'
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            className="hidden"
            accept=".csv,.xlsx,.pdf"
            ref={fileInputRef}
            onChange={handleFileChange}
          />
          
          <div className="flex flex-col items-center justify-center">
            <UploadIcon className="h-10 w-10 mb-4 text-muted-foreground" />
            <p className="font-medium mb-1">Drag and drop your file here</p>
            <p className="text-sm text-muted-foreground mb-4">or click to browse files</p>
            <p className="text-xs text-muted-foreground">
              Accepted formats: CSV, XLSX, PDF (Max size: 10MB)
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center p-4 bg-muted/50 rounded-lg border border-border">
            <div className="mr-4">
              <FilePlusIcon className="h-10 w-10 text-primary" />
            </div>
            
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">
                {formatSize(selectedFile.size)} • {selectedFile.type.split('/')[1].toUpperCase()}
              </p>
            </div>
            
            <button
              type="button"
              className="ml-4 text-red-500 hover:text-red-700 focus:outline-none"
              onClick={handleCancel}
              disabled={isUploading}
            >
              <CrossCircledIcon className="h-5 w-5" />
              <span className="sr-only">Remove</span>
            </button>
          </div>
          
          <div className="flex space-x-3">
            <button
              type="button"
              className={`flex-1 py-2 px-4 rounded-md font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ${
                isUploading 
                  ? 'bg-primary/60 cursor-not-allowed' 
                  : 'bg-primary hover:bg-primary/90 text-primary-foreground'
              }`}
              onClick={handleUpload}
              disabled={isUploading}
            >
              {isUploading ? 'Uploading...' : 'Upload File'}
            </button>
            
            <button
              type="button"
              className="py-2 px-4 bg-muted hover:bg-muted/80 text-muted-foreground rounded-md font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-muted"
              onClick={handleCancel}
              disabled={isUploading}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
      
      <div className="mt-4 flex flex-col space-y-1 text-xs text-muted-foreground">
        <p>• Accepted file formats: CSV, XLSX, PDF</p>
        <p>• Maximum file size: 10MB</p>
        <p>• For CSV/XLSX: Ensure columns are properly labeled</p>
        <p>• For PDF: Tables will be automatically extracted</p>
      </div>
    </div>
  );
}