import { NextRequest, NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { registerFounder } from '@/lib/feedback';

// This is a simplified example - in production, you would use proper storage
const UPLOAD_DIR = path.join(process.cwd(), 'public', 'uploads');

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    const email = formData.get('email') as string;
    const name = formData.get('name') as string;
    const companyName = formData.get('companyName') as string;
    const deckFile = formData.get('deck') as File;
    
    if (!email || !name || !companyName || !deckFile) {
      return NextResponse.json(
        { message: 'Missing required fields' },
        { status: 400 }
      );
    }
    
    // Generate a unique filename
    const uniqueId = uuidv4();
    const fileName = `${uniqueId}-${deckFile.name.replace(/\s+/g, '-')}`;
    const filePath = path.join(UPLOAD_DIR, fileName);
    
    // In a production environment, you would upload this to S3/MinIO
    // This is a simplified example for development
    try {
      const fileArrayBuffer = await deckFile.arrayBuffer();
      const fileBuffer = Buffer.from(fileArrayBuffer);
      
      // Ensure upload directory exists
      await writeFile(filePath, fileBuffer);
      
      // Store in database via beta_feedback service
      const deckUrl = `/uploads/${fileName}`;
      const result = await registerFounder(email, name, companyName, deckUrl);
      
      if (result.status !== 'success' && result.status !== 'exists') {
        console.error('Error registering founder:', result);
        return NextResponse.json(
          { message: 'Error registering application' },
          { status: 500 }
        );
      }
      
      return NextResponse.json(
        { message: 'Application submitted successfully' },
        { status: 200 }
      );
    } catch (error) {
      console.error('Error saving file:', error);
      return NextResponse.json(
        { message: 'Error saving file' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error processing application:', error);
    return NextResponse.json(
      { message: 'Failed to process application' },
      { status: 500 }
    );
  }
}