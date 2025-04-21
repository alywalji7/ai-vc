import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Navbar from './components/Navbar'
import TRPCProvider from '@/lib/trpc/Provider'
import { ThemeProvider } from '@/lib/theme/ThemeProvider'

const inter = Inter({ subsets: ['latin'] })

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
      <body className={`${inter.className} min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <TRPCProvider>
            <Navbar />
            <main className="container mx-auto py-6 px-4">
              {children}
            </main>
          </TRPCProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
