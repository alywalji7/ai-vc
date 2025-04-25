import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Navbar from './components/Navbar'
import TRPCProvider from '@/lib/trpc/Provider'
import { ThemeProvider } from '@/lib/theme/ThemeProvider'
import { ToastProvider } from '@/components/ui/toast'
import { cn } from '@/lib/utils'
import IntercomProvider from '@/components/IntercomProvider'

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' })

export const metadata: Metadata = {
  title: 'AI.VC Investment Platform',
  description: 'An AI-driven investment platform with comprehensive portfolio management and LP reporting',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn(
        "min-h-screen bg-background font-sans antialiased",
        inter.variable
      )}>
        <ThemeProvider 
          attribute="class" 
          defaultTheme="system" 
          enableSystem
        >
          <TRPCProvider>
            <ToastProvider>
              <IntercomProvider>
                <div className="flex flex-col min-h-screen">
                  <Navbar />
                  <main className="container mx-auto py-6 px-4 flex-1">
                    {children}
                  </main>
                  <footer className="py-4 bg-card border-t border-border">
                    <div className="container mx-auto px-4">
                      <p className="text-center text-sm text-muted-foreground">
                        &copy; {new Date().getFullYear()} AI.VC Platform. All rights reserved.
                      </p>
                    </div>
                  </footer>
                </div>
              </IntercomProvider>
            </ToastProvider>
          </TRPCProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
