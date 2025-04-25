import { NextResponse } from 'next/server';

export const config = {
  api: {
    bodyParser: false,
  },
};

export async function POST(req: Request) {
  try {
    // Check if the user is authenticated (simplified)
    // In a real app, this would use the auth session
    const isAuthenticated = true;
    
    if (!isAuthenticated) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }
    
    const formData = await req.formData();
    const file = formData.get('file') as File;
    const lpId = formData.get('lpId') as string;
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }
    
    if (!lpId) {
      return NextResponse.json(
        { error: 'No LP ID provided' },
        { status: 400 }
      );
    }
    
    // Validate file type
    const allowedTypes = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'Invalid file type. Only CSV, XLSX, and PDF files are supported.' },
        { status: 400 }
      );
    }
    
    // Validate file size (limit to 10MB)
    const maxSize = 10 * 1024 * 1024; // 10 MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: 'File size exceeds the 10MB limit' },
        { status: 400 }
      );
    }
    
    // Upload to backend service
    const uploadResponse = await uploadFileToBackend(file, lpId);
    
    if (!uploadResponse.ok) {
      const errorData = await uploadResponse.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to upload file' },
        { status: uploadResponse.status }
      );
    }
    
    const responseData = await uploadResponse.json();
    
    return NextResponse.json({
      fileId: responseData.file_id,
      message: 'File uploaded successfully'
    });
  } catch (error: any) {
    console.error('Error uploading file:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}

async function uploadFileToBackend(file: File, lpId: string) {
  // Convert File to a format that can be sent to the backend
  const arrayBuffer = await file.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  
  // Create a FormData object for the backend request
  const formData = new FormData();
  
  // Create a new file object with the buffer
  const backendFile = new File([buffer], file.name, { type: file.type });
  
  formData.append('file', backendFile);
  formData.append('lp_id', lpId);
  
  // Send to the upload service
  return fetch('http://localhost:8500/api/v1/files/upload', {
    method: 'POST',
    body: formData,
  });
}