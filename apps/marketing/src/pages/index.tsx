import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import Layout from '../components/Layout';
import { trackEvent } from '../lib/analytics';

export default function Home() {
  const trackCTAClick = (ctaName: string) => {
    trackEvent('cta_click', { cta: ctaName, location: 'homepage' });
  };

  return (
    <Layout>
      {/* Hero Section */}
      <section className="hero-gradient text-white overflow-hidden relative">
        {/* Animated particles */}
        <div className="absolute inset-0 overflow-hidden opacity-20">
          <div className="absolute top-10 left-10 w-20 h-20 rounded-full bg-white/20 animate-pulse-slow"></div>
          <div className="absolute top-[20%] right-[15%] w-32 h-32 rounded-full bg-white/10 animate-pulse-slow" style={{animationDelay: '1s'}}></div>
          <div className="absolute bottom-[30%] left-[25%] w-16 h-16 rounded-full bg-white/15 animate-pulse-slow" style={{animationDelay: '2s'}}></div>
          <div className="absolute bottom-[10%] right-[10%] w-24 h-24 rounded-full bg-white/10 animate-pulse-slow" style={{animationDelay: '1.5s'}}></div>
        </div>
        
        <div className="container-lg mx-auto py-16 md:py-24 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="space-y-6 md:pr-8">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight fade-in-up">
                AI-Driven Investment Intelligence Platform
              </h1>
              <p className="text-lg md:text-xl text-gray-100 fade-in-up-delay-1">
                Transform complex financial data into actionable insights through sophisticated data ingestion and graph-based analysis.
              </p>
              <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 pt-4 fade-in-up-delay-2">
                <a 
                  href="https://app.aivc.com/signup" 
                  className="btn btn-secondary btn-lg relative overflow-hidden data-flow"
                  onClick={() => trackCTAClick('hero_get_started')}
                >
                  Get Started
                </a>
                <Link 
                  href="/demo"
                  className="btn bg-white text-primary-700 hover:bg-gray-100 btn-lg"
                  onClick={() => trackCTAClick('hero_request_demo')}
                >
                  Request Demo
                </Link>
              </div>
              <div className="text-sm text-gray-200 pt-2 fade-in-up-delay-3">
                No credit card required. 14-day free trial.
              </div>
            </div>
            <div className="relative hidden md:block fade-in-up-delay-1">
              <div className="w-full h-[500px] relative float-animation">
                <div className="absolute inset-0 bg-white/10 backdrop-blur-sm rounded-lg overflow-hidden shadow-2xl">
                  <div className="p-4">
                    <div className="bg-gradient-to-r from-primary-900/80 to-secondary-900/80 p-4 rounded-md text-white mb-4 pulse-animation">
                      <div className="flex items-center mb-2">
                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <span className="font-semibold">AI Investment Radar</span>
                      </div>
                      <p className="text-sm">Identified 3 promising investment opportunities in emerging AI infrastructure.</p>
                    </div>
                    
                    <div className="bg-white/95 rounded-md p-4 shadow-md mb-4 data-flow">
                      <h4 className="font-semibold text-gray-900 mb-2">Portfolio Performance</h4>
                      <div className="h-40 bg-gray-100 rounded mb-2 flex items-center justify-center">
                        <div className="w-full h-full flex items-end justify-between px-4 pt-4">
                          <div className="w-1/6 h-[30%] bg-primary-600 rounded-t" style={{animation: 'fadeInUp 1s ease-out 0.1s forwards', opacity: 0}}></div>
                          <div className="w-1/6 h-[60%] bg-primary-600 rounded-t" style={{animation: 'fadeInUp 1s ease-out 0.2s forwards', opacity: 0}}></div>
                          <div className="w-1/6 h-[45%] bg-primary-600 rounded-t" style={{animation: 'fadeInUp 1s ease-out 0.3s forwards', opacity: 0}}></div>
                          <div className="w-1/6 h-[80%] bg-primary-600 rounded-t" style={{animation: 'fadeInUp 1s ease-out 0.4s forwards', opacity: 0}}></div>
                          <div className="w-1/6 h-[70%] bg-primary-600 rounded-t" style={{animation: 'fadeInUp 1s ease-out 0.5s forwards', opacity: 0}}></div>
                          <div className="w-1/6 h-[90%] bg-primary-600 rounded-t" style={{animation: 'fadeInUp 1s ease-out 0.6s forwards', opacity: 0}}></div>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div className="bg-gray-100 p-2 rounded">
                          <p className="text-gray-600 text-xs">IRR</p>
                          <p className="text-gray-900 font-semibold">24.3%</p>
                        </div>
                        <div className="bg-gray-100 p-2 rounded">
                          <p className="text-gray-600 text-xs">TVPI</p>
                          <p className="text-gray-900 font-semibold">2.1x</p>
                        </div>
                        <div className="bg-gray-100 p-2 rounded">
                          <p className="text-gray-600 text-xs">DPI</p>
                          <p className="text-gray-900 font-semibold">0.4x</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/95 rounded-md p-4 shadow-md">
                      <h4 className="font-semibold text-gray-900 mb-2">Deal Flow Analysis</h4>
                      <div className="space-y-2">
                        <div className="flex items-center">
                          <div className="w-2/3">
                            <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-primary-600 w-0" style={{animation: 'growWidth 1.5s ease-out 0.7s forwards', width: 0}}>
                                <style jsx>{`
                                  @keyframes growWidth {
                                    from { width: 0; }
                                    to { width: 85%; }
                                  }
                                `}</style>
                              </div>
                            </div>
                          </div>
                          <div className="ml-3 text-sm font-medium text-gray-900">Series A</div>
                        </div>
                        <div className="flex items-center">
                          <div className="w-2/3">
                            <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-primary-600 w-0" style={{animation: 'growWidth2 1.5s ease-out 0.9s forwards', width: 0}}>
                                <style jsx>{`
                                  @keyframes growWidth2 {
                                    from { width: 0; }
                                    to { width: 65%; }
                                  }
                                `}</style>
                              </div>
                            </div>
                          </div>
                          <div className="ml-3 text-sm font-medium text-gray-900">Series B</div>
                        </div>
                        <div className="flex items-center">
                          <div className="w-2/3">
                            <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-primary-600 w-0" style={{animation: 'growWidth3 1.5s ease-out 1.1s forwards', width: 0}}>
                                <style jsx>{`
                                  @keyframes growWidth3 {
                                    from { width: 0; }
                                    to { width: 40%; }
                                  }
                                `}</style>
                              </div>
                            </div>
                          </div>
                          <div className="ml-3 text-sm font-medium text-gray-900">Series C</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Partners Section */}
      <section className="bg-gray-50 py-12">
        <div className="container-lg mx-auto">
          <h2 className="text-xl text-center text-gray-600 mb-8">Trusted by leading venture capital firms</h2>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16">
            <div className="w-32 h-12 bg-gray-300 rounded opacity-60 flex items-center justify-center">
              <span className="text-gray-600 font-semibold">ACME VC</span>
            </div>
            <div className="w-32 h-12 bg-gray-300 rounded opacity-60 flex items-center justify-center">
              <span className="text-gray-600 font-semibold">Alpha Partners</span>
            </div>
            <div className="w-32 h-12 bg-gray-300 rounded opacity-60 flex items-center justify-center">
              <span className="text-gray-600 font-semibold">Beta Capital</span>
            </div>
            <div className="w-32 h-12 bg-gray-300 rounded opacity-60 flex items-center justify-center">
              <span className="text-gray-600 font-semibold">Sigma Ventures</span>
            </div>
            <div className="w-32 h-12 bg-gray-300 rounded opacity-60 flex items-center justify-center">
              <span className="text-gray-600 font-semibold">Omega Fund</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 md:py-24">
        <div className="container-lg mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">AI-Powered Investment Intelligence</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our platform combines advanced AI with financial expertise to give you unprecedented insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card p-6 card-hover">
              <div className="feature-icon bg-primary-600">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path>
                  <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">Data-Driven Deal Flow</h3>
              <p className="text-gray-600 mb-4">
                Analyze thousands of potential investments using our AI-powered deal scoring system to identify the most promising opportunities.
              </p>
              <Link 
                href="/features#deal-flow" 
                className="text-primary-600 font-medium hover:text-primary-700 inline-flex items-center"
                onClick={() => trackCTAClick('feature_deal_flow')}
              >
                Learn more
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>

            {/* Feature 2 */}
            <div className="card p-6 card-hover">
              <div className="feature-icon bg-secondary-600">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 0l-2 2a1 1 0 101.414 1.414L8 10.414l1.293 1.293a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">Knowledge Graph Analysis</h3>
              <p className="text-gray-600 mb-4">
                Discover hidden relationships and patterns in your portfolio with our sophisticated knowledge graph technology.
              </p>
              <Link 
                href="/features#knowledge-graph" 
                className="text-primary-600 font-medium hover:text-primary-700 inline-flex items-center"
                onClick={() => trackCTAClick('feature_knowledge_graph')}
              >
                Learn more
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>

            {/* Feature 3 */}
            <div className="card p-6 card-hover">
              <div className="feature-icon bg-accent-600">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"></path>
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">Investment Committee Simulator</h3>
              <p className="text-gray-600 mb-4">
                Test investment theses before your actual IC meeting with our AI-powered simulator that models diverse perspectives.
              </p>
              <Link 
                href="/features#ic-simulator" 
                className="text-primary-600 font-medium hover:text-primary-700 inline-flex items-center"
                onClick={() => trackCTAClick('feature_ic_simulator')}
              >
                Learn more
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link 
              href="/features" 
              className="btn btn-primary"
              onClick={() => trackCTAClick('all_features')}
            >
              View All Features
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="bg-gray-50 py-16 md:py-24">
        <div className="container-lg mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">What Our Clients Say</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Hear from the investment teams that trust our platform.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="testimonial-card">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gray-300 rounded-full mr-4"></div>
                <div>
                  <h4 className="font-bold">Sarah Johnson</h4>
                  <p className="text-gray-600 text-sm">Partner, Acme Ventures</p>
                </div>
              </div>
              <p className="text-gray-700">
                "The knowledge graph analysis has revolutionized how we understand market dynamics. We identified three unexpected investment opportunities that have performed exceedingly well."
              </p>
            </div>

            {/* Testimonial 2 */}
            <div className="testimonial-card">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gray-300 rounded-full mr-4"></div>
                <div>
                  <h4 className="font-bold">Michael Chen</h4>
                  <p className="text-gray-600 text-sm">Managing Director, Beta Capital</p>
                </div>
              </div>
              <p className="text-gray-700">
                "The IC Simulator helped us refine our investment thesis and prepare for every possible question. It's like having a team of experienced investors critique your approach before the actual meeting."
              </p>
            </div>

            {/* Testimonial 3 */}
            <div className="testimonial-card">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gray-300 rounded-full mr-4"></div>
                <div>
                  <h4 className="font-bold">Amanda Rodriguez</h4>
                  <p className="text-gray-600 text-sm">Principal, Sigma Ventures</p>
                </div>
              </div>
              <p className="text-gray-700">
                "We've cut our due diligence time in half while actually increasing the depth of our analysis. The AI-powered deal flow scoring has been surprisingly accurate at identifying winners."
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-900 text-white py-16">
        <div className="container-lg mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to transform your investment process?</h2>
              <p className="text-xl mb-6">
                Join leading VC firms that are using AI to gain a competitive edge in sourcing, analyzing, and managing investments.
              </p>
              <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                <a 
                  href="https://app.aivc.com/signup" 
                  className="btn btn-secondary btn-lg"
                  onClick={() => trackCTAClick('footer_get_started')}
                >
                  Get Started
                </a>
                <Link 
                  href="/demo"
                  className="btn bg-white text-primary-700 hover:bg-gray-100 btn-lg"
                  onClick={() => trackCTAClick('footer_request_demo')}
                >
                  Request Demo
                </Link>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="bg-primary-800/50 p-6 rounded-lg">
                <h3 className="font-bold text-2xl mb-4">Enterprise Plan Includes:</h3>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-secondary-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                    </svg>
                    <span>Unlimited deal flow scoring</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-secondary-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                    </svg>
                    <span>Advanced knowledge graph analysis</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-secondary-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                    </svg>
                    <span>Custom investment committee profiles</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-secondary-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                    </svg>
                    <span>Automatic term sheet generation</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-secondary-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                    </svg>
                    <span>Dedicated account manager</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}