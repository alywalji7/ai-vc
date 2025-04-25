import { useEffect, useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { trackPageview, trackLeadSubmission } from '@/lib/analytics';

export default function RequestDemo() {
  const router = useRouter();
  const { plan } = router.query;
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    message: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    // Track page view on component mount
    trackPageview('/demo');
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await trackLeadSubmission(formData);
      setSubmitSuccess(true);
      setFormData({
        name: '',
        email: '',
        company: '',
        message: '',
      });
    } catch (error) {
      console.error('Error submitting form:', error);
      setSubmitError('There was an error submitting your request. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Head>
        <title>Request a Demo | AI.VC</title>
        <meta
          name="description"
          content="Schedule a personalized demo to see how AI.VC can transform your investment process."
        />
      </Head>

      <main className="flex min-h-screen flex-col">
        {/* Header */}
        <section className="bg-indigo-700 py-16 sm:py-24">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
                Request a Personalized Demo
              </h1>
              <p className="mt-6 text-xl leading-8 text-indigo-100">
                See how AI.VC can transform your investment process with our 
                AI-powered platform. Fill out the form below and our team will 
                get back to you within 24 hours.
              </p>
            </div>
          </div>
        </section>

        {/* Form Section */}
        <section className="py-16 sm:py-24 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-xl mx-auto">
              {submitSuccess ? (
                <div className="bg-green-50 p-8 rounded-xl text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-green-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <h2 className="mt-4 text-2xl font-bold text-gray-900">
                    Thank you for your interest!
                  </h2>
                  <p className="mt-2 text-gray-600">
                    We've received your demo request and will contact you within 24 hours
                    to schedule a personalized demonstration of the AI.VC platform.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-8">
                  {plan && (
                    <div className="bg-indigo-50 rounded-lg p-4 mb-6">
                      <p className="text-indigo-700">
                        You've selected the <span className="font-semibold">{plan.toString().charAt(0).toUpperCase() + plan.toString().slice(1)}</span> plan. 
                        We'll customize your demo accordingly.
                      </p>
                    </div>
                  )}
                  
                  {submitError && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                      {submitError}
                    </div>
                  )}
                  
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                      Full Name *
                    </label>
                    <div className="mt-1">
                      <input
                        id="name"
                        name="name"
                        type="text"
                        required
                        value={formData.name}
                        onChange={handleInputChange}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                      Work Email *
                    </label>
                    <div className="mt-1">
                      <input
                        id="email"
                        name="email"
                        type="email"
                        required
                        value={formData.email}
                        onChange={handleInputChange}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="company" className="block text-sm font-medium text-gray-700">
                      Company Name *
                    </label>
                    <div className="mt-1">
                      <input
                        id="company"
                        name="company"
                        type="text"
                        required
                        value={formData.company}
                        onChange={handleInputChange}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700">
                      What are you most interested in learning about?
                    </label>
                    <div className="mt-1">
                      <textarea
                        id="message"
                        name="message"
                        rows={4}
                        value={formData.message}
                        onChange={handleInputChange}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                  </div>

                  <div>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className={`w-full rounded-md bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-sm ${
                        isSubmitting ? 'opacity-75 cursor-not-allowed' : 'hover:bg-indigo-500'
                      } focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600`}
                    >
                      {isSubmitting ? 'Submitting...' : 'Request Your Demo'}
                    </button>
                  </div>

                  <p className="text-xs text-gray-500 mt-4">
                    By submitting this form, you agree to our{' '}
                    <a href="/privacy" className="text-indigo-600 hover:text-indigo-500">
                      Privacy Policy
                    </a>{' '}
                    and{' '}
                    <a href="/terms" className="text-indigo-600 hover:text-indigo-500">
                      Terms of Service
                    </a>
                    .
                  </p>
                </form>
              )}
            </div>
          </div>
        </section>

        {/* Features Overview */}
        <section className="py-16 sm:py-24 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900 text-center">
                What to Expect in Your Demo
              </h2>
              <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2">
                <div className="flex flex-col">
                  <div className="flex h-12 w-12 items-center justify-center rounded-md bg-indigo-100 text-indigo-600">
                    <svg
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                  </div>
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-gray-900">Customized Walkthrough</h3>
                    <p className="mt-2 text-gray-600">
                      Get a personalized tour of the AI.VC platform tailored to your firm's investment
                      strategy and needs.
                    </p>
                  </div>
                </div>

                <div className="flex flex-col">
                  <div className="flex h-12 w-12 items-center justify-center rounded-md bg-indigo-100 text-indigo-600">
                    <svg
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-gray-900">Live Feature Demonstrations</h3>
                    <p className="mt-2 text-gray-600">
                      See our AI-powered deal-flow radar, investment committee simulator, and term sheet
                      negotiator in action.
                    </p>
                  </div>
                </div>

                <div className="flex flex-col">
                  <div className="flex h-12 w-12 items-center justify-center rounded-md bg-indigo-100 text-indigo-600">
                    <svg
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                      />
                    </svg>
                  </div>
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-gray-900">Pricing and ROI Discussion</h3>
                    <p className="mt-2 text-gray-600">
                      Understand our transparent pricing model and how AI.VC can deliver measurable ROI
                      for your investment firm.
                    </p>
                  </div>
                </div>

                <div className="flex flex-col">
                  <div className="flex h-12 w-12 items-center justify-center rounded-md bg-indigo-100 text-indigo-600">
                    <svg
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-gray-900">Implementation Timeline</h3>
                    <p className="mt-2 text-gray-600">
                      Learn about our streamlined onboarding process and how quickly you can start
                      using AI.VC to enhance your investment decisions.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}