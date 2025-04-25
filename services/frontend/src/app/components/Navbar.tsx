'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ThemeToggle } from '@/lib/theme/ThemeToggle';
import { MobileNav } from '@/components/MobileNav';
import { cn } from '@/lib/utils';

export default function Navbar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === '/') {
      return pathname === path;
    }
    return pathname?.startsWith(path);
  };

  return (
    <nav className="sticky top-0 z-30 w-full border-b border-border bg-background">
      <div className="container mx-auto px-4">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center">
            <div className="flex lg:hidden">
              <MobileNav />
            </div>
            <div className="flex-shrink-0 flex items-center ml-2 lg:ml-0">
              <Link href="/" className="text-xl font-bold text-primary">
                AI.VC
              </Link>
            </div>
            <div className="hidden lg:ml-6 lg:flex lg:space-x-8">
              <Link
                href="/"
                className={cn(
                  "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                  isActive('/') 
                    ? 'border-primary text-foreground' 
                    : 'border-transparent text-muted-foreground hover:border-border hover:text-foreground'
                )}
              >
                Home
              </Link>
              <Link
                href="/dashboard"
                className={cn(
                  "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                  isActive('/dashboard') 
                    ? 'border-primary text-foreground' 
                    : 'border-transparent text-muted-foreground hover:border-border hover:text-foreground'
                )}
              >
                Dashboard
              </Link>
              <Link
                href="/deal-memos"
                className={cn(
                  "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                  isActive('/deal-memos') 
                    ? 'border-primary text-foreground' 
                    : 'border-transparent text-muted-foreground hover:border-border hover:text-foreground'
                )}
              >
                Deal Memos
              </Link>
              <Link
                href="/audit-trail"
                className={cn(
                  "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                  isActive('/audit-trail') 
                    ? 'border-primary text-foreground' 
                    : 'border-transparent text-muted-foreground hover:border-border hover:text-foreground'
                )}
              >
                Audit Trail
              </Link>
              <Link
                href="/portfolio"
                className={cn(
                  "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                  isActive('/portfolio') 
                    ? 'border-primary text-foreground' 
                    : 'border-transparent text-muted-foreground hover:border-border hover:text-foreground'
                )}
              >
                Portfolio
              </Link>
              <Link
                href="/pricing"
                className={cn(
                  "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                  isActive('/pricing') 
                    ? 'border-primary text-foreground' 
                    : 'border-transparent text-muted-foreground hover:border-border hover:text-foreground'
                )}
              >
                Pricing
              </Link>
            </div>
          </div>
          <div className="flex items-center">
            <div className="hidden md:block">
              <ThemeToggle />
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}