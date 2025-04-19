'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Navbar() {
  const pathname = usePathname()

  const isActiveLink = (path: string) => {
    return pathname === path ? 'bg-gray-700' : ''
  }

  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="font-bold text-xl">Polyglot Monorepo</div>
        <ul className="flex space-x-4">
          <li>
            <Link 
              href="/" 
              className={`px-3 py-2 rounded-md ${isActiveLink('/')}`}
            >
              Home
            </Link>
          </li>
          <li>
            <Link 
              href="/scheduler" 
              className={`px-3 py-2 rounded-md ${isActiveLink('/scheduler')}`}
            >
              Scheduler
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}