import { useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { trackPageview } from '@/lib/analytics';

export default function Pricing() {
  useEffect(() => {
    // Track page view on component mount
    trackPageview('/pricing');
  }, []);

  return (
    <>
      <Head>
        <title>Pricing | AI.VC</title>
        <meta
          name="description"
          content="Transparent pricing plans for AI.VC's investment intelligence platform. Choose the plan that best fits your firm's needs."
        />
      </Head>

      <main className="flex min-h-screen flex-col">
        {/* Header */}
        <section className="bg-indigo-700 py-16 sm:py-24">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
                Straightforward Pricing
              </h1>
              <p className="mt-6 text-xl leading-8 text-indigo-100">
                Choose the plan that fits your investment firm's needs.
                All plans include our core features with different usage limits and support levels.
              </p>
            </div>
          </div>
        </section>

        {/* Pricing Plans */}
        <section className="py-16 sm:py-24 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
              <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
                {/* Starter Plan */}
                <div className="flex flex-col rounded-2xl border border-gray-200 shadow-sm hover:shadow-lg transition-shadow duration-300">
                  <div className="p-8 sm:p-10">
                    <h3 className="text-lg font-semibold leading-8 tracking-tight text-indigo-600">Starter</h3>
                    <div className="mt-4 flex items-baseline text-5xl font-bold tracking-tight text-gray-900">
                      $500
                      <span className="ml-1 text-lg font-semibold text-gray-500">/month</span>
                    </div>
                    <p className="mt-6 text-base leading-7 text-gray-600">
                      Perfect for smaller firms or individual investors just getting started with AI-powered investment intelligence.
                    </p>
                  </div>
                  <div className="flex flex-1 flex-col justify-between px-8 pb-8 pt-2 sm:px-10">
                    <ul className="space-y-4">
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">1 user seat</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">50 API calls per day</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">Basic deal-flow radar</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">Email support</p>
                      </li>
                    </ul>
                    <div className="mt-8">
                      <Link
                        href="/demo?plan=starter"
                        className="inline-block w-full rounded-md bg-indigo-600 py-3 text-center text-base font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                      >
                        Get started
                      </Link>
                    </div>
                  </div>
                </div>

                {/* Pro Plan */}
                <div className="relative flex flex-col rounded-2xl border border-indigo-200 bg-indigo-50 shadow-sm hover:shadow-lg transition-shadow duration-300">
                  <div className="absolute -top-4 left-0 right-0 mx-auto w-32 rounded-full bg-indigo-600 px-4 py-1 text-center text-xs font-semibold uppercase tracking-wide text-white">
                    Most Popular
                  </div>
                  <div className="p-8 sm:p-10">
                    <h3 className="text-lg font-semibold leading-8 tracking-tight text-indigo-600">Pro</h3>
                    <div className="mt-4 flex items-baseline text-5xl font-bold tracking-tight text-gray-900">
                      $1,000
                      <span className="ml-1 text-lg font-semibold text-gray-500">/month</span>
                    </div>
                    <p className="mt-6 text-base leading-7 text-gray-600">
                      Designed for established firms looking to enhance their investment process with AI-powered insights.
                    </p>
                  </div>
                  <div className="flex flex-1 flex-col justify-between px-8 pb-8 pt-2 sm:px-10">
                    <ul className="space-y-4">
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">3 user seats</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">500 API calls per day</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">Advanced deal-flow radar with custom filters</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">Priority email support</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">Investment Committee Simulator</p>
                      </li>
                    </ul>
                    <div className="mt-8">
                      <Link
                        href="/demo?plan=pro"
                        className="inline-block w-full rounded-md bg-indigo-600 py-3 text-center text-base font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                      >
                        Get started
                      </Link>
                    </div>
                  </div>
                </div>

                {/* Enterprise Plan */}
                <div className="flex flex-col rounded-2xl border border-gray-200 shadow-sm hover:shadow-lg transition-shadow duration-300">
                  <div className="p-8 sm:p-10">
                    <h3 className="text-lg font-semibold leading-8 tracking-tight text-indigo-600">Enterprise</h3>
                    <div className="mt-4 flex items-baseline text-5xl font-bold tracking-tight text-gray-900">
                      $2,000
                      <span className="ml-1 text-lg font-semibold text-gray-500">/month</span>
                    </div>
                    <p className="mt-6 text-base leading-7 text-gray-600">
                      Comprehensive solution for larger firms with custom integration needs and advanced analytics requirements.
                    </p>
                  </div>
                  <div className="flex flex-1 flex-col justify-between px-8 pb-8 pt-2 sm:px-10">
                    <ul className="space-y-4">
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">Unlimited user seats</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">10,000 API calls per day</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">All features including Term Sheet Negotiator</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">24/7 dedicated support</p>
                      </li>
                      <li className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="ml-3 text-base text-gray-700">Custom integration & training</p>
                      </li>
                    </ul>
                    <div className="mt-8">
                      <Link
                        href="/demo?plan=enterprise"
                        className="inline-block w-full rounded-md bg-indigo-600 py-3 text-center text-base font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                      >
                        Contact sales
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="py-16 sm:py-24 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900 text-center">
                Frequently Asked Questions
              </h2>
              <dl className="mt-12 space-y-8">
                <div>
                  <dt className="text-lg font-semibold leading-7 text-gray-900">
                    Can I change plans later?
                  </dt>
                  <dd className="mt-2 text-base text-gray-600">
                    Yes, you can upgrade or downgrade your plan at any time. Changes will be reflected in your next billing cycle.
                  </dd>
                </div>
                <div>
                  <dt className="text-lg font-semibold leading-7 text-gray-900">
                    Is there a free trial?
                  </dt>
                  <dd className="mt-2 text-base text-gray-600">
                    We offer a 14-day free trial with access to all features of the Pro plan for qualified investment firms.
                    Contact our sales team to set up your trial.
                  </dd>
                </div>
                <div>
                  <dt className="text-lg font-semibold leading-7 text-gray-900">
                    How do API calls work?
                  </dt>
                  <dd className="mt-2 text-base text-gray-600">
                    API calls include all requests to our platform's APIs, including deal-flow radar searches, 
                    investment committee simulations, and term sheet generations. Dashboard page loads do not count toward your API limit.
                  </dd>
                </div>
                <div>
                  <dt className="text-lg font-semibold leading-7 text-gray-900">
                    Do you offer custom plans?
                  </dt>
                  <dd className="mt-2 text-base text-gray-600">
                    Yes, for firms with unique requirements, we can create custom plans with specific feature sets and 
                    usage limits. Contact our sales team to discuss your needs.
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 sm:py-24 bg-indigo-700">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Ready to enhance your investment process?
              </h2>
              <p className="mt-4 text-lg leading-6 text-indigo-100">
                Schedule a demo to see AI.VC in action and discuss which plan is right for your firm.
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