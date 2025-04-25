import { useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { trackPageview } from '@/lib/analytics';

export default function Home() {
  useEffect(() => {
    // Track page view on component mount
    trackPageview('/');
  }, []);

  return (
    <>
      <Head>
        <title>AI.VC | Next-Gen Investment Intelligence</title>
        <meta
          name="description"
          content="AI.VC uses advanced AI to transform complex investment data into actionable insights for venture capital and private equity firms."
        />
      </Head>

      <main className="flex min-h-screen flex-col">
        {/* Hero Section */}
        <section className="bg-gradient-to-b from-gray-50 to-white py-20 sm:py-32">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                <span className="block text-indigo-600">AI-Powered</span>
                <span className="block">Investment Intelligence</span>
              </h1>
              <p className="mt-6 text-xl leading-8 text-gray-600">
                Transform complex financial data into actionable insights with advanced AI analysis, 
                graph-based company relationships, and predictive deal-flow radar.
              </p>
              <div className="mt-10 flex justify-center gap-x-6">
                <Link 
                  href="/features" 
                  className="rounded-md bg-indigo-600 px-8 py-3 text-lg font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  Key Features
                </Link>
                <Link
                  href="/demo"
                  className="rounded-md bg-white px-8 py-3 text-lg font-semibold text-indigo-600 shadow-sm ring-1 ring-inset ring-indigo-200 hover:bg-gray-50 hover:ring-indigo-300"
                >
                  Request Demo
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Value Proposition Section */}
        <section className="py-12 sm:py-24 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              <div className="text-center">
                <div className="flex justify-center items-center mb-4 w-12 h-12 mx-auto bg-indigo-100 rounded-xl">
                  <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Deal-Flow Radar</h2>
                <p className="text-gray-600">
                  Identify high-potential investments before they appear on competitor radars with 
                  our proprietary scoring algorithm.
                </p>
              </div>

              <div className="text-center">
                <div className="flex justify-center items-center mb-4 w-12 h-12 mx-auto bg-indigo-100 rounded-xl">
                  <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">AI Due Diligence</h2>
                <p className="text-gray-600">
                  Accelerate due diligence with AI-powered analysis of company data, market trends, 
                  and competitive landscape.
                </p>
              </div>

              <div className="text-center">
                <div className="flex justify-center items-center mb-4 w-12 h-12 mx-auto bg-indigo-100 rounded-xl">
                  <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Term Sheet Negotiator</h2>
                <p className="text-gray-600">
                  Generate and negotiate term sheets with our intelligent assistant, saving time and 
                  reducing legal costs.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Social Proof Section */}
        <section className="py-12 sm:py-24 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-16">
              Trusted by Leading Investment Firms
            </h2>
            <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
              <div className="col-span-1 flex justify-center items-center">
                <div className="h-12 text-gray-400 font-semibold">ACME Ventures</div>
              </div>
              <div className="col-span-1 flex justify-center items-center">
                <div className="h-12 text-gray-400 font-semibold">Sequoia Capital</div>
              </div>
              <div className="col-span-1 flex justify-center items-center">
                <div className="h-12 text-gray-400 font-semibold">Andressen Horowitz</div>
              </div>
              <div className="col-span-1 flex justify-center items-center">
                <div className="h-12 text-gray-400 font-semibold">Kleiner Perkins</div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-12 sm:py-24 bg-indigo-700">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Ready to transform your investment process?
              </h2>
              <p className="mt-4 text-lg leading-6 text-indigo-100">
                Join leading investment firms already using AI.VC to identify opportunities, 
                streamline due diligence, and make better investment decisions.
              </p>
              <div className="mt-10">
                <Link 
                  href="/demo" 
                  className="inline-block rounded-md bg-white px-8 py-3 text-lg font-semibold text-indigo-700 shadow-sm hover:bg-indigo-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
                >
                  Schedule a Demo
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}