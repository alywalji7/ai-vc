import { useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { trackPageview } from '@/lib/analytics';

export default function Features() {
  useEffect(() => {
    // Track page view on component mount
    trackPageview('/features');
  }, []);

  return (
    <>
      <Head>
        <title>Features | AI.VC</title>
        <meta
          name="description"
          content="Explore AI.VC's powerful features for investment intelligence, due diligence, and deal management."
        />
      </Head>

      <main className="flex min-h-screen flex-col">
        {/* Header */}
        <section className="bg-indigo-700 py-16 sm:py-24">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
                Comprehensive Investment Intelligence
              </h1>
              <p className="mt-6 text-xl leading-8 text-indigo-100">
                AI.VC offers a suite of AI-powered tools designed to enhance every step of your investment process,
                from deal sourcing to portfolio management.
              </p>
            </div>
          </div>
        </section>

        {/* Feature List */}
        <section className="py-16 sm:py-24 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
              <div className="space-y-16">
                {/* Feature 1 */}
                <div className="flex flex-col-reverse lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
                      Knowledge Graph & Data Ingestion
                    </h2>
                    <p className="mt-4 text-lg text-gray-600">
                      Our knowledge graph connects billions of data points from SEC filings, news sources,
                      social media, and proprietary databases to provide a comprehensive view of the investment landscape.
                    </p>
                    <ul className="mt-8 space-y-4">
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Real-time data ingestion from multiple sources
                        </p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Graph-based relationship mapping between companies, people, and investors
                        </p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Advanced entity extraction and sentiment analysis from unstructured text
                        </p>
                      </li>
                    </ul>
                  </div>
                  <div className="mb-10 lg:mb-0">
                    <div className="bg-gray-100 rounded-xl p-12 flex items-center justify-center">
                      <svg className="w-24 h-24 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Feature 2 */}
                <div className="flex flex-col lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
                  <div className="mb-10 lg:mb-0">
                    <div className="bg-gray-100 rounded-xl p-12 flex items-center justify-center">
                      <svg className="w-24 h-24 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
                      Deal-Flow Radar
                    </h2>
                    <p className="mt-4 text-lg text-gray-600">
                      Our AI-powered deal-flow radar identifies high-potential companies before they appear on
                      competitors' radars, giving you the advantage to act early on promising opportunities.
                    </p>
                    <ul className="mt-8 space-y-4">
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Proprietary scoring algorithm based on growth metrics, market trends, and founder backgrounds
                        </p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Customizable filters for sector, stage, and investment criteria
                        </p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Early-warning system for companies showing signs of exponential growth
                        </p>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Feature 3 */}
                <div className="flex flex-col-reverse lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
                      Investment Committee Simulator
                    </h2>
                    <p className="mt-4 text-lg text-gray-600">
                      Test investment hypotheses and get AI-powered insights on potential deals before bringing them
                      to your investment committee, saving time and improving decision quality.
                    </p>
                    <ul className="mt-8 space-y-4">
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Two-stage filtering process with rule-based checks and deep LLM analysis
                        </p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Tree-of-Thought reasoning that considers multiple investment scenarios
                        </p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-600">
                          Historical pattern matching with your firm's past successful investments
                        </p>
                      </li>
                    </ul>
                  </div>
                  <div className="mb-10 lg:mb-0">
                    <div className="bg-gray-100 rounded-xl p-12 flex items-center justify-center">
                      <svg className="w-24 h-24 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Additional features can be added here following the same pattern */}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 sm:py-24 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                Experience the full power of AI.VC
              </h2>
              <p className="mt-4 text-lg leading-6 text-gray-600">
                See how our platform can transform your investment process with a personalized demo.
              </p>
              <div className="mt-10 flex justify-center gap-x-6">
                <Link 
                  href="/pricing" 
                  className="rounded-md bg-white px-8 py-3 text-lg font-semibold text-indigo-600 shadow-sm ring-1 ring-inset ring-indigo-200 hover:bg-gray-50 hover:ring-indigo-300"
                >
                  View Pricing
                </Link>
                <Link 
                  href="/demo" 
                  className="rounded-md bg-indigo-600 px-8 py-3 text-lg font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  Request Demo
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}