import { useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { trackPageview } from '@/lib/analytics';

// Sample blog posts data (in a real app, this would come from a CMS or API)
const blogPosts = [
  {
    id: 'ai-vc-landscape-2025',
    title: 'The AI-Powered VC Landscape in 2025',
    excerpt: 'How artificial intelligence is transforming venture capital decision-making and deal flow processes.',
    date: 'April 15, 2025',
    author: 'Jane Smith',
    authorTitle: 'Chief Research Officer',
    category: 'Industry Insights',
    readTime: '8 min read',
    imageSrc: '/blog/ai-vc-landscape.jpg',
  },
  {
    id: 'graph-based-investing',
    title: 'Graph-Based Investing: Finding Hidden Connections',
    excerpt: 'Leveraging knowledge graphs to uncover non-obvious relationships between companies, founders, and market trends.',
    date: 'March 28, 2025',
    author: 'David Chen',
    authorTitle: 'Data Science Lead',
    category: 'Technology',
    readTime: '6 min read',
    imageSrc: '/blog/graph-investing.jpg',
  },
  {
    id: 'due-diligence-automation',
    title: 'Automating Due Diligence: From Weeks to Hours',
    excerpt: 'How AI-driven analysis is compressing the timeline for comprehensive investment due diligence.',
    date: 'February 12, 2025',
    author: 'Michael Johnson',
    authorTitle: 'Investment Operations',
    category: 'Best Practices',
    readTime: '5 min read',
    imageSrc: '/blog/due-diligence.jpg',
  },
  {
    id: 'term-sheet-negotiation',
    title: 'The Future of Term Sheet Negotiation',
    excerpt: 'AI assistants are changing how VCs and founders negotiate deal terms, leading to more efficient and balanced outcomes.',
    date: 'January 20, 2025',
    author: 'Sarah Williams',
    authorTitle: 'Legal Affairs',
    category: 'Legal',
    readTime: '7 min read',
    imageSrc: '/blog/term-sheets.jpg',
  },
];

export default function Blog() {
  useEffect(() => {
    // Track page view on component mount
    trackPageview('/blog');
  }, []);

  return (
    <>
      <Head>
        <title>Blog | AI.VC</title>
        <meta
          name="description"
          content="Latest insights on AI in investment, venture capital trends, and technology innovation from the AI.VC team."
        />
      </Head>

      <main className="flex min-h-screen flex-col">
        {/* Header */}
        <section className="bg-indigo-700 py-16 sm:py-24">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
                Investment Intelligence Insights
              </h1>
              <p className="mt-6 text-xl leading-8 text-indigo-100">
                Expert analysis and thought leadership on AI, venture capital,
                and the future of investment decision-making.
              </p>
            </div>
          </div>
        </section>

        {/* Blog Post Grid */}
        <section className="py-16 sm:py-24 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 gap-x-8 gap-y-16 md:grid-cols-2 lg:grid-cols-2">
              {blogPosts.map((post) => (
                <article key={post.id} className="flex flex-col items-start border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow duration-300">
                  <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                    {/* In production, this would be an actual image */}
                    <svg
                      className="h-12 w-12 text-gray-400"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1}
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>

                  <div className="p-6 flex-1 flex flex-col">
                    <div className="flex items-center gap-x-4 text-xs mb-3">
                      <span className="text-gray-500">{post.date}</span>
                      <span className="relative z-10 rounded-full bg-indigo-100 px-3 py-1.5 font-medium text-indigo-800">
                        {post.category}
                      </span>
                    </div>
                    <div className="group">
                      <h3 className="text-xl font-bold leading-7 text-gray-900 group-hover:text-indigo-600">
                        <Link href={`/blog/${post.id}`}>
                          <span className="absolute inset-0" />
                          {post.title}
                        </Link>
                      </h3>
                      <p className="mt-3 text-sm leading-6 text-gray-600 line-clamp-3">{post.excerpt}</p>
                    </div>
                    <div className="relative mt-6 flex items-center gap-x-4">
                      <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-semibold">
                        {post.author.split(' ').map(name => name[0]).join('')}
                      </div>
                      <div className="text-sm leading-6">
                        <p className="font-semibold text-gray-900">{post.author}</p>
                        <p className="text-gray-600">{post.authorTitle}</p>
                      </div>
                    </div>
                    <div className="mt-4 text-xs text-gray-500">{post.readTime}</div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* Newsletter Section */}
        <section className="py-16 sm:py-24 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                Subscribe to our newsletter
              </h2>
              <p className="mt-4 text-lg leading-6 text-gray-600">
                Get the latest insights on AI in investment delivered to your inbox.
              </p>
              <div className="mt-10">
                <form className="max-w-md mx-auto">
                  <div className="flex gap-x-4">
                    <label htmlFor="email-address" className="sr-only">
                      Email address
                    </label>
                    <input
                      id="email-address"
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                      className="min-w-0 flex-auto rounded-md border-0 px-3.5 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                      placeholder="Enter your email"
                    />
                    <button
                      type="submit"
                      className="flex-none rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    >
                      Subscribe
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}