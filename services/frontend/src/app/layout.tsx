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
                      <div className="flex flex-col sm:flex-row justify-between items-center gap-2">
                        <p className="text-sm text-muted-foreground">
                          &copy; {new Date().getFullYear()} AI.VC Platform. All rights reserved.
                        </p>
                        <div className="flex gap-4 text-sm">
                          <a 
                            href="/static/legal/adv.pdf" 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-primary hover:text-primary/90 transition-colors"
                          >
                            Download latest ADV
                          </a>
                          <a 
                            href="/legal/terms" 
                            className="text-muted-foreground hover:text-foreground transition-colors"
                          >
                            Terms
                          </a>
                          <a 
                            href="/legal/privacy"
                            className="text-muted-foreground hover:text-foreground transition-colors"
                          >
                            Privacy
                          </a>
                        </div>
                      </div>
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
