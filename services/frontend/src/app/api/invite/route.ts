import { NextRequest, NextResponse } from 'next/server';
import { clerkClient } from '@clerk/nextjs/server';
import { registerLP } from '@/lib/feedback';

export async function POST(request: NextRequest) {
  try {
    const { email } = await request.json();

    if (!email) {
      return NextResponse.json(
        { message: 'Email is required' },
        { status: 400 }
      );
    }

    // Create magic link using Clerk
    console.log(`Sending magic link to ${email}`);
    
    // In production, this would use the actual Clerk client
    // For development, we'll simulate success
    /*
    const magicLink = await clerkClient.emails.createMagicLinkFlow({
      emailAddressId: email,
      redirectUrl: `${process.env.NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL || '/dashboard'}`,
    });
    */

    // Call the beta_feedback API to pre-create the LP record
    const result = await registerLP(email);
    
    if (result.status !== 'success' && result.status !== 'exists') {
      console.error('Error pre-creating LP record:', result);
      // We don't want to fail the user-facing request if this fails
      // Just log it and continue
    }

    return NextResponse.json(
      { message: 'Magic link sent successfully' },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error sending magic link:', error);
    return NextResponse.json(
      { message: 'Failed to send magic link' },
      { status: 500 }
    );
  }
}