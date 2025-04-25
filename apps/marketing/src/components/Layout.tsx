import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { trackEvent } from '../lib/analytics';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  title = 'AI.VC - AI-Powered Investment Intelligence Platform', 
  description = 'Transform complex financial data into actionable insights through sophisticated data ingestion and graph-based analysis'
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const router = useRouter();

  // Handle scroll events for sticky header
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    const handleRouteChange = () => {
      setIsMobileMenuOpen(false);
    };
    
    router.events.on('routeChangeComplete', handleRouteChange);
    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router.events]);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const trackCtaClick = (ctaName: string) => {
    trackEvent('cta_click', { cta: ctaName });
  };

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:type" content="website" />
        <meta property="og:image" content="/og-image.jpg" />
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:title" content={title} />
        <meta property="twitter:description" content={description} />
      </Head>

      <div className="flex flex-col min-h-screen">
        {/* Header */}
        <header 
          className={`sticky top-0 z-40 w-full transition-all duration-200 bg-white ${
            isScrolled ? 'shadow-md' : ''
          }`}
        >
          <div className="container-lg py-4 mx-auto">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <Link 
                href="/" 
                className="flex items-center text-2xl font-bold text-primary-700"
              >
                <span className="mr-2">
                  <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M16 2L28 9V23L16 30L4 23V9L16 2Z" fill="#0284C7" />
                    <path d="M16 8L22 12V20L16 24L10 20V12L16 8Z" fill="white" />
                  </svg>
                </span>
                AI.VC
              </Link>

              {/* Desktop Navigation */}
              <nav className="hidden md:flex space-x-8">
                <Link 
                  href="/features" 
                  className={`text-base font-medium hover:text-primary-600 transition-colors ${
                    router.pathname === '/features' ? 'text-primary-600' : 'text-gray-700'
                  }`}
                >
                  Features
                </Link>
                <Link 
                  href="/pricing"
                  className={`text-base font-medium hover:text-primary-600 transition-colors ${
                    router.pathname === '/pricing' ? 'text-primary-600' : 'text-gray-700'
                  }`}
                >
                  Pricing
                </Link>
                <Link 
                  href="/about"
                  className={`text-base font-medium hover:text-primary-600 transition-colors ${
                    router.pathname === '/about' ? 'text-primary-600' : 'text-gray-700'
                  }`}
                >
                  About
                </Link>
                <Link 
                  href="/blog"
                  className={`text-base font-medium hover:text-primary-600 transition-colors ${
                    router.pathname === '/blog' || router.pathname.startsWith('/blog/') ? 'text-primary-600' : 'text-gray-700'
                  }`}
                >
                  Blog
                </Link>
                <Link 
                  href="/contact"
                  className={`text-base font-medium hover:text-primary-600 transition-colors ${
                    router.pathname === '/contact' ? 'text-primary-600' : 'text-gray-700'
                  }`}
                >
                  Contact
                </Link>
              </nav>

              {/* CTA Buttons */}
              <div className="hidden md:flex items-center space-x-4">
                <a 
                  href="https://app.aivc.com/login" 
                  className="text-primary-600 hover:text-primary-800 font-medium transition-colors"
                  onClick={() => trackCtaClick('login_header')}
                >
                  Log In
                </a>
                <a 
                  href="https://app.aivc.com/signup" 
                  className="btn btn-primary"
                  onClick={() => trackCtaClick('signup_header')}
                >
                  Get Started
                </a>
              </div>

              {/* Mobile Menu Button */}
              <button 
                className="flex items-center md:hidden"
                onClick={toggleMobileMenu}
                aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className="h-6 w-6 text-gray-700" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  {isMobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          <div 
            className={`md:hidden ${
              isMobileMenuOpen ? 'max-h-screen border-t border-gray-100' : 'max-h-0 overflow-hidden'
            } transition-all duration-300 ease-in-out`}
          >
            <nav className="flex flex-col space-y-4 p-4 bg-white">
              <Link 
                href="/features"
                className={`text-base font-medium hover:text-primary-600 transition-colors ${
                  router.pathname === '/features' ? 'text-primary-600' : 'text-gray-700'
                }`}
              >
                Features
              </Link>
              <Link 
                href="/pricing"
                className={`text-base font-medium hover:text-primary-600 transition-colors ${
                  router.pathname === '/pricing' ? 'text-primary-600' : 'text-gray-700'
                }`}
              >
                Pricing
              </Link>
              <Link 
                href="/about"
                className={`text-base font-medium hover:text-primary-600 transition-colors ${
                  router.pathname === '/about' ? 'text-primary-600' : 'text-gray-700'
                }`}
              >
                About
              </Link>
              <Link 
                href="/blog"
                className={`text-base font-medium hover:text-primary-600 transition-colors ${
                  router.pathname === '/blog' || router.pathname.startsWith('/blog/') ? 'text-primary-600' : 'text-gray-700'
                }`}
              >
                Blog
              </Link>
              <Link 
                href="/contact"
                className={`text-base font-medium hover:text-primary-600 transition-colors ${
                  router.pathname === '/contact' ? 'text-primary-600' : 'text-gray-700'
                }`}
              >
                Contact
              </Link>
              <div className="pt-4 border-t border-gray-100 flex flex-col space-y-4">
                <a 
                  href="https://app.aivc.com/login" 
                  className="text-primary-600 hover:text-primary-800 font-medium transition-colors"
                  onClick={() => trackCtaClick('login_mobile')}
                >
                  Log In
                </a>
                <a 
                  href="https://app.aivc.com/signup" 
                  className="btn btn-primary w-full text-center"
                  onClick={() => trackCtaClick('signup_mobile')}
                >
                  Get Started
                </a>
              </div>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-grow">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12">
          <div className="container-lg mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {/* Brand Column */}
              <div className="col-span-1">
                <Link 
                  href="/"
                  className="flex items-center text-2xl font-bold text-white mb-4"
                >
                  <span className="mr-2">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M16 2L28 9V23L16 30L4 23V9L16 2Z" fill="#38BDF8" />
                      <path d="M16 8L22 12V20L16 24L10 20V12L16 8Z" fill="white" />
                    </svg>
                  </span>
                  AI.VC
                </Link>
                <p className="text-gray-400 mb-4">
                  Transforming complex financial data into actionable insights.
                </p>
                <div className="flex space-x-4">
                  <a href="https://twitter.com/aivc" aria-label="Twitter" className="text-gray-400 hover:text-white transition-colors">
                    <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"></path>
                    </svg>
                  </a>
                  <a href="https://linkedin.com/company/aivc" aria-label="LinkedIn" className="text-gray-400 hover:text-white transition-colors">
                    <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"></path>
                    </svg>
                  </a>
                </div>
              </div>

              {/* Links Column 1 */}
              <div className="col-span-1">
                <h3 className="text-lg font-bold mb-4">Company</h3>
                <ul className="space-y-3">
                  <li><Link href="/about" className="text-gray-400 hover:text-white transition-colors">About Us</Link></li>
                  <li><Link href="/careers" className="text-gray-400 hover:text-white transition-colors">Careers</Link></li>
                  <li><Link href="/contact" className="text-gray-400 hover:text-white transition-colors">Contact</Link></li>
                  <li><Link href="/blog" className="text-gray-400 hover:text-white transition-colors">Blog</Link></li>
                </ul>
              </div>

              {/* Links Column 2 */}
              <div className="col-span-1">
                <h3 className="text-lg font-bold mb-4">Product</h3>
                <ul className="space-y-3">
                  <li><Link href="/features" className="text-gray-400 hover:text-white transition-colors">Features</Link></li>
                  <li><Link href="/pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</Link></li>
                  <li><Link href="/security" className="text-gray-400 hover:text-white transition-colors">Security</Link></li>
                  <li><Link href="/docs" className="text-gray-400 hover:text-white transition-colors">Documentation</Link></li>
                </ul>
              </div>

              {/* Newsletter Column */}
              <div className="col-span-1">
                <h3 className="text-lg font-bold mb-4">Stay Updated</h3>
                <p className="text-gray-400 mb-4">
                  Subscribe to our newsletter for the latest updates and insights.
                </p>
                <form className="flex flex-col space-y-2" onSubmit={(e) => {
                  e.preventDefault();
                  const email = (e.currentTarget.elements.namedItem('email') as HTMLInputElement).value;
                  // Here you would typically submit this to your API
                  trackEvent('newsletter_subscribe', { location: 'footer' });
                  alert('Thank you for subscribing!');
                }}>
                  <input 
                    type="email" 
                    name="email"
                    placeholder="Your email address" 
                    className="form-input bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary-500" 
                    required
                  />
                  <button type="submit" className="btn btn-primary">
                    Subscribe
                  </button>
                </form>
              </div>
            </div>

            {/* Copyright */}
            <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400">
                &copy; {new Date().getFullYear()} AI.VC. All rights reserved.
              </p>
              <div className="flex space-x-6 mt-4 md:mt-0">
                <Link href="/privacy" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</Link>
                <Link href="/terms" className="text-gray-400 hover:text-white transition-colors">Terms of Service</Link>
                <Link href="/cookies" className="text-gray-400 hover:text-white transition-colors">Cookie Policy</Link>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default Layout;