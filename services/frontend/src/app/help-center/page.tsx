'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { showIntercomChat } from '@/components/IntercomProvider';

// Define the structure of our documentation
const documentationCategories = [
  {
    title: 'Getting Started',
    slug: 'getting-started',
    description: 'Learn the basics of the AI.VC Platform',
  },
  {
    title: 'Portfolio Management',
    slug: 'portfolio-management',
    description: 'How to upload and manage your investment portfolio',
  },
  {
    title: 'FAQ',
    slug: 'faq',
    description: 'Answers to common questions',
  },
];

export default function HelpCenter() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredDocs, setFilteredDocs] = useState(documentationCategories);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [docContent, setDocContent] = useState<string | null>(null);

  // Load the document content if a category is selected in the URL
  useEffect(() => {
    const category = searchParams.get('category');
    if (category) {
      setSelectedCategory(category);
      fetchDocContent(category);
    } else {
      setSelectedCategory(null);
      setDocContent(null);
    }
  }, [searchParams]);

  // Filter docs when search term changes
  useEffect(() => {
    if (searchTerm) {
      const filtered = documentationCategories.filter(
        doc => 
          doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          doc.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredDocs(filtered);
    } else {
      setFilteredDocs(documentationCategories);
    }
  }, [searchTerm]);

  // Fetch document content from our API
  const fetchDocContent = async (slug: string) => {
    try {
      // Show loading state
      setDocContent(`# ${slug.charAt(0).toUpperCase() + slug.slice(1).replace(/-/g, ' ')}\n\nLoading documentation content...`);
      
      // Fetch the content from our API
      const response = await fetch(`/api/documentation/${slug}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to load documentation');
      }
      
      const data = await response.json();
      setDocContent(data.content);
    } catch (error) {
      console.error('Error fetching documentation:', error);
      setDocContent('# Error\n\nFailed to load documentation content. Please try again later.');
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Update the URL with the search term
    const params = new URLSearchParams(searchParams.toString());
    if (searchTerm) {
      params.set('q', searchTerm);
    } else {
      params.delete('q');
    }
    router.push(`/help-center?${params.toString()}`);
  };

  const handleCategoryClick = (slug: string) => {
    setSelectedCategory(slug);
    router.push(`/help-center?category=${slug}`);
  };

  return (
    <div className="flex flex-col space-y-6">
      <h1 className="text-3xl font-bold">Help Center</h1>
      
      <div className="flex items-center space-x-4">
        <form onSubmit={handleSearch} className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Search documentation..."
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary text-white px-3 py-1 rounded-md"
            >
              Search
            </button>
          </div>
        </form>
        
        <button
          onClick={() => showIntercomChat()}
          className="bg-primary text-white px-4 py-2 rounded-md flex items-center space-x-2"
        >
          <span>Chat with Support</span>
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {selectedCategory ? (
          <div className="col-span-1 md:col-span-3">
            <button
              onClick={() => router.push('/help-center')}
              className="text-primary mb-4 inline-flex items-center"
            >
              ← Back to Help Center
            </button>
            
            <div className="bg-card p-6 rounded-lg shadow">
              {docContent ? (
                <div className="prose max-w-none">
                  {/* In a real app, this would use a MDX renderer component */}
                  <div dangerouslySetInnerHTML={{ __html: docContent.replace(/\n/g, '<br/>') }} />
                </div>
              ) : (
                <div className="flex justify-center items-center h-64">
                  <div className="w-16 h-16 border-4 border-t-primary border-opacity-50 rounded-full animate-spin"></div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <>
            {filteredDocs.map((doc) => (
              <div
                key={doc.slug}
                className="bg-card p-6 rounded-lg shadow cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => handleCategoryClick(doc.slug)}
              >
                <h2 className="text-xl font-semibold mb-2">{doc.title}</h2>
                <p className="text-muted-foreground mb-4">{doc.description}</p>
                <Link
                  href={`/help-center?category=${doc.slug}`}
                  className="text-primary hover:underline"
                >
                  Read more →
                </Link>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}