import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
 
// Paths that don't require subscription
const PUBLIC_PATHS = [
  '/',
  '/login',
  '/signup',
  '/pricing',
  '/api/webhook',
  '/api/create-checkout-session',
]

// Paths that require authentication but not subscription
const AUTH_PATHS = [
  '/dashboard', // Basic dashboard shown to all authenticated users
  '/profile',
]

/**
 * Check if a path is public
 */
function isPublicPath(path: string): boolean {
  return PUBLIC_PATHS.some(publicPath => 
    path === publicPath || path.startsWith(publicPath + '/')
  )
}

/**
 * Check if a path is auth-only
 */
function isAuthPath(path: string): boolean {
  return AUTH_PATHS.some(authPath => 
    path === authPath || path.startsWith(authPath + '/')
  )
}

/**
 * Check if the user has an active subscription
 */
async function hasActiveSubscription(userId: string): Promise<boolean> {
  try {
    // In a real app, you would check against your database or make an API call
    // to your billing service to verify subscription status
    
    // For development purposes, we'll assume all users have active subscriptions
    // Replace this with actual subscription check in production
    return true
    
    // Example of how you might check in production:
    /*
    const response = await fetch(`http://billing-service:8300/subscription/${userId}/check`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.INTERNAL_API_KEY}`,
      },
    })
    
    if (!response.ok) {
      console.error(`Failed to check subscription: ${response.statusText}`)
      return false
    }
    
    const data = await response.json()
    return data.active
    */
  } catch (error) {
    console.error('Error checking subscription status:', error)
    // In case of error, we'll allow access (fail open) to avoid blocking users unnecessarily
    return true
  }
}

/**
 * Middleware to handle authentication and subscription checks
 */
export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname
  
  // Public paths are always accessible
  if (isPublicPath(path)) {
    return NextResponse.next()
  }
  
  // Check if user is authenticated
  // In a real app, you would check for a session cookie or JWT token
  const isAuthenticated = true // Replace with actual auth check
  
  if (!isAuthenticated) {
    // Redirect unauthenticated users to login
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  // Auth paths don't require subscription check
  if (isAuthPath(path)) {
    return NextResponse.next()
  }
  
  // For subscription-required paths, check subscription status
  const userId = 'user_123' // Replace with actual user ID extraction
  const hasSubscription = await hasActiveSubscription(userId)
  
  if (!hasSubscription) {
    // Redirect users without subscription to pricing page
    return NextResponse.redirect(new URL('/pricing', request.url))
  }
  
  // User is authenticated and has subscription, allow access
  return NextResponse.next()
}

/**
 * Configure which paths the middleware runs on
 */
export const config = {
  // Skip static files and public API endpoints
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.png$).*)'],
}