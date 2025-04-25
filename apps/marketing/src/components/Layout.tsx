import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { trackEvent } from '../lib/analytics';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
  ogImage?: string;
  noIndex?: boolean;
}

const Layout: React.FC<LayoutProps> = ({
  children,
  title = 'AI.VC - Transform Complex Financial Data Into Actionable Insights',
  description = 'AI.VC is an advanced AI-driven investment intelligence platform that transforms complex financial data into actionable insights through sophisticated data ingestion and graph-based analysis.',
  ogImage = '/images/og-image.jpg',
  noIndex = false,
}) => {
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Handle scroll events to update header styles
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMenuOpen(false);
  }, [router.asPath]);
  
  // Track navigation clicks
  const handleNavClick = (destination: string) => {
    trackEvent('navigation_click', {
      from: router.asPath,
      to: destination,
    });
  };

  // Toggle mobile menu
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:image" content={ogImage} />
        <meta property="og:type" content="website" />
        <meta property="og:url" content={`https://aivc.com${router.asPath}`} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <meta name="twitter:image" content={ogImage} />
        {noIndex && <meta name="robots" content="noindex, nofollow" />}
      </Head>

      <header 
        className={`fixed w-full z-50 transition-all duration-300 ${
          isScrolled ? 'bg-white shadow-sm py-3' : 'bg-transparent py-5'
        }`}
      >
        <div className="container-xl flex items-center justify-between">
          <Link href="/" onClick={() => handleNavClick('/')} className="flex items-center">
            <img 
              src="/logo.svg" 
              alt="AI.VC Logo" 
              className="h-8 md:h-10" 
              width="auto" 
              height="40" 
            />
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8 items-center">
            <Link 
              href="/features" 
              onClick={() => handleNavClick('/features')}
              className="text-gray-700 hover:text-primary-600 font-medium"
            >
              Features
            </Link>
            <Link 
              href="/pricing" 
              onClick={() => handleNavClick('/pricing')}
              className="text-gray-700 hover:text-primary-600 font-medium"
            >
              Pricing
            </Link>
            <Link 
              href="/about" 
              onClick={() => handleNavClick('/about')}
              className="text-gray-700 hover:text-primary-600 font-medium"
            >
              About
            </Link>
            <Link 
              href="/contact" 
              onClick={() => handleNavClick('/contact')}
              className="text-gray-700 hover:text-primary-600 font-medium"
            >
              Contact
            </Link>
            <a 
              href="https://app.aivc.com/login" 
              onClick={() => trackEvent('nav_login_click')}
              className="btn btn-outline btn-md"
              target="_blank"
              rel="noopener noreferrer"
            >
              Sign In
            </a>
            <a 
              href="https://app.aivc.com/signup" 
              onClick={() => trackEvent('nav_signup_click')}
              className="btn btn-primary btn-md"
              target="_blank"
              rel="noopener noreferrer"
            >
              Get Started
            </a>
          </nav>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden text-gray-700"
            onClick={toggleMenu}
            aria-label="Toggle menu"
          >
            {isMenuOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        <div 
          className={`md:hidden fixed inset-0 bg-white z-40 transition-transform duration-300 ease-in-out transform ${
            isMenuOpen ? 'translate-x-0' : 'translate-x-full'
          } pt-20`}
        >
          <nav className="flex flex-col space-y-6 p-8">
            <Link 
              href="/features" 
              onClick={() => handleNavClick('/features')}
              className="text-gray-800 text-lg font-medium"
            >
              Features
            </Link>
            <Link 
              href="/pricing" 
              onClick={() => handleNavClick('/pricing')}
              className="text-gray-800 text-lg font-medium"
            >
              Pricing
            </Link>
            <Link 
              href="/about" 
              onClick={() => handleNavClick('/about')}
              className="text-gray-800 text-lg font-medium"
            >
              About
            </Link>
            <Link 
              href="/contact" 
              onClick={() => handleNavClick('/contact')}
              className="text-gray-800 text-lg font-medium"
            >
              Contact
            </Link>
            <div className="pt-4 flex flex-col space-y-4">
              <a 
                href="https://app.aivc.com/login" 
                onClick={() => trackEvent('nav_login_click')}
                className="btn btn-outline btn-lg w-full text-center"
                target="_blank"
                rel="noopener noreferrer"
              >
                Sign In
              </a>
              <a 
                href="https://app.aivc.com/signup" 
                onClick={() => trackEvent('nav_signup_click')}
                className="btn btn-primary btn-lg w-full text-center"
                target="_blank"
                rel="noopener noreferrer"
              >
                Get Started
              </a>
            </div>
          </nav>
        </div>
      </header>

      <main className="pt-[76px] md:pt-[88px]">
        {children}
      </main>

      <footer className="bg-gray-900 text-white py-12 md:py-20">
        <div className="container-xl">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-12">
            <div>
              <img 
                src="/logo-white.svg" 
                alt="AI.VC Logo" 
                className="h-8 mb-6" 
                width="auto" 
                height="32" 
              />
              <p className="text-gray-400 mb-6">
                Transform complex financial data into actionable insights through AI-driven analysis.
              </p>
              <div className="flex space-x-4">
                <a 
                  href="https://twitter.com/aivc" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  aria-label="Twitter"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
                <a 
                  href="https://linkedin.com/company/aivc" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  aria-label="LinkedIn"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                  </svg>
                </a>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Product</h3>
              <ul className="space-y-3">
                <li>
                  <Link 
                    href="/features" 
                    onClick={() => handleNavClick('/features')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Features
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/pricing" 
                    onClick={() => handleNavClick('/pricing')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/security" 
                    onClick={() => handleNavClick('/security')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Security
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/integrations" 
                    onClick={() => handleNavClick('/integrations')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Integrations
                  </Link>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Company</h3>
              <ul className="space-y-3">
                <li>
                  <Link 
                    href="/about" 
                    onClick={() => handleNavClick('/about')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    About
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/team" 
                    onClick={() => handleNavClick('/team')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Team
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/careers" 
                    onClick={() => handleNavClick('/careers')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Careers
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/contact" 
                    onClick={() => handleNavClick('/contact')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Contact
                  </Link>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-3">
                <li>
                  <Link 
                    href="/blog" 
                    onClick={() => handleNavClick('/blog')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Blog
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/documentation" 
                    onClick={() => handleNavClick('/documentation')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Documentation
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/faq" 
                    onClick={() => handleNavClick('/faq')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    FAQ
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/support" 
                    onClick={() => handleNavClick('/support')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Support
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col md:flex-row md:justify-between items-center">
            <p className="text-gray-500 text-sm mb-4 md:mb-0">
              &copy; {new Date().getFullYear()} AI.VC. All rights reserved.
            </p>
            <div className="flex flex-wrap gap-4 md:gap-6 text-sm">
              <Link 
                href="/terms" 
                onClick={() => handleNavClick('/terms')}
                className="text-gray-500 hover:text-white transition-colors"
              >
                Terms
              </Link>
              <Link 
                href="/privacy" 
                onClick={() => handleNavClick('/privacy')}
                className="text-gray-500 hover:text-white transition-colors"
              >
                Privacy
              </Link>
              <Link 
                href="/cookies" 
                onClick={() => handleNavClick('/cookies')}
                className="text-gray-500 hover:text-white transition-colors"
              >
                Cookies
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
};

export default Layout;