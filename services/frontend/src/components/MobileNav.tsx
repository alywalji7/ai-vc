'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu } from 'lucide-react';
import { useState } from 'react';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { ThemeToggle } from '@/lib/theme/ThemeToggle';

export function MobileNav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === '/') {
      return pathname === path;
    }
    return pathname?.startsWith(path);
  };

  const routes = [
    { href: '/', label: 'Home' },
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/deal-memos', label: 'Deal Memos' },
    { href: '/audit-trail', label: 'Audit Trail' },
    { href: '/pricing', label: 'Pricing' },
  ];

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <button
          className="md:hidden rounded-full w-9 h-9 flex items-center justify-center text-primary hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring"
          aria-label="Open menu"
        >
          <Menu className="h-5 w-5" />
        </button>
      </SheetTrigger>
      <SheetContent side="left" className="w-[240px] md:hidden">
        <div className="flex flex-col h-full py-4">
          <div className="px-4 py-2 mb-6">
            <h2 className="text-lg font-bold text-primary">AI.VC</h2>
          </div>
          <nav className="flex-1">
            <ul className="space-y-1">
              {routes.map((route) => (
                <li key={route.href}>
                  <Link
                    href={route.href}
                    onClick={() => setOpen(false)}
                    className={`flex items-center px-4 py-3 text-sm transition-colors hover:text-foreground ${
                      isActive(route.href)
                        ? 'bg-primary/10 text-primary font-medium'
                        : 'text-muted-foreground'
                    }`}
                  >
                    {route.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          <div className="px-4 py-2 mt-auto border-t border-border">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Theme</span>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}