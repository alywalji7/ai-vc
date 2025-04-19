import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Navbar from './components/Navbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Polyglot Monorepo',
  description: 'A polyglot monorepo with Python backend services, TypeScript/Next.js frontend, and containerized infrastructure',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navbar />
        <main className="container mx-auto py-6 px-4">
          {children}
        </main>
      </body>
    </html>
  )
}
