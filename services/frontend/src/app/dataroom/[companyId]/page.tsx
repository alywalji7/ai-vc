'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';

interface CompanyData {
  id: string;
  name: string;
  website: string;
  founding_date: string;
  github_stars: number;
  commit_velocity: number;
  investor_count: number;
  founder_exit_count: number;
  social_traction: number;
  funding_amount: number;
  radar_score: number;
  generation_timestamp: string;
}

interface DataRoomDetails {
  company_data: CompanyData;
  summary: string;
  files: string[];
}

export default function DataRoomDetailPage({ params }: { params: { companyId: string } }) {
  const { companyId } = params;
  
  const [dataRoom, setDataRoom] = useState<DataRoomDetails | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'summary' | 'data' | 'files'>('summary');

  useEffect(() => {
    const fetchDataRoom = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/dataroom/${companyId}`);
        
        if (!response.ok) {
          throw new Error(`Error fetching dataroom: ${response.statusText}`);
        }
        
        const data = await response.json();
        setDataRoom(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        console.error('Error fetching dataroom:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDataRoom();
  }, [companyId]);

  const formatScore = (score: number) => {
    return (score * 100).toFixed(0) + '%';
  };

  const formatCurrency = (amount: number) => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(1)}K`;
    } else {
      return `$${amount}`;
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href="/dataroom" className="text-blue-500 hover:underline">
          ← Back to Data Rooms
        </Link>
      </div>
      
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      )}
      
      {dataRoom && (
        <>
          <div className="mb-8">
            <div className="flex justify-between items-center">
              <h1 className="text-3xl font-bold">{dataRoom.company_data.name}</h1>
              <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
                dataRoom.company_data.radar_score >= 0.8 ? 'bg-green-100 text-green-800' :
                dataRoom.company_data.radar_score >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                Radar Score: {formatScore(dataRoom.company_data.radar_score)}
              </div>
            </div>
            
            <div className="mt-2">
              <a href={dataRoom.company_data.website} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                {dataRoom.company_data.website}
              </a>
            </div>
            
            <div className="mt-1 text-sm text-gray-500">
              Founded: {formatDate(dataRoom.company_data.founding_date)}
            </div>
          </div>
          
          <div className="border-b border-gray-200 mb-6">
            <nav className="flex -mb-px">
              <button
                className={`px-4 py-2 border-b-2 font-medium text-sm ${
                  activeTab === 'summary' ?
                  'border-blue-500 text-blue-600' :
                  'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('summary')}
              >
                Summary
              </button>
              <button
                className={`px-4 py-2 border-b-2 font-medium text-sm ${
                  activeTab === 'data' ?
                  'border-blue-500 text-blue-600' :
                  'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('data')}
              >
                Data
              </button>
              <button
                className={`px-4 py-2 border-b-2 font-medium text-sm ${
                  activeTab === 'files' ?
                  'border-blue-500 text-blue-600' :
                  'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('files')}
              >
                Files
              </button>
            </nav>
          </div>
          
          {activeTab === 'summary' && (
            <div className="prose max-w-none">
              <ReactMarkdown>
                {dataRoom.summary}
              </ReactMarkdown>
            </div>
          )}
          
          {activeTab === 'data' && (
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Company Data</h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">Raw metrics and KPIs</p>
              </div>
              <div className="border-t border-gray-200">
                <dl>
                  <div className="bg-gray-50 px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Company ID</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{dataRoom.company_data.id}</dd>
                  </div>
                  <div className="bg-white px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">GitHub Stars</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{dataRoom.company_data.github_stars.toLocaleString()}</dd>
                  </div>
                  <div className="bg-gray-50 px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Commit Velocity</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{dataRoom.company_data.commit_velocity}</dd>
                  </div>
                  <div className="bg-white px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Investor Count</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{dataRoom.company_data.investor_count}</dd>
                  </div>
                  <div className="bg-gray-50 px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Founder Exit Count</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{dataRoom.company_data.founder_exit_count}</dd>
                  </div>
                  <div className="bg-white px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Social Traction</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{dataRoom.company_data.social_traction.toLocaleString()}</dd>
                  </div>
                  <div className="bg-gray-50 px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Funding Amount</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{formatCurrency(dataRoom.company_data.funding_amount)}</dd>
                  </div>
                  <div className="bg-white px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Generation Date</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{formatDate(dataRoom.company_data.generation_timestamp)}</dd>
                  </div>
                </dl>
              </div>
            </div>
          )}
          
          {activeTab === 'files' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Available Files</h3>
              {dataRoom.files.length === 0 ? (
                <p className="text-gray-500">No files available for this company.</p>
              ) : (
                <ul className="divide-y divide-gray-200 border border-gray-200 rounded-md">
                  {dataRoom.files.map((filename) => (
                    <li key={filename} className="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                      <div className="w-0 flex-1 flex items-center">
                        <svg className="flex-shrink-0 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                        </svg>
                        <span className="ml-2 flex-1 truncate">{filename}</span>
                      </div>
                      <div className="ml-4 flex-shrink-0">
                        <a 
                          href={`/api/dataroom/${companyId}/file/${filename}`} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="font-medium text-blue-600 hover:text-blue-500"
                        >
                          Download
                        </a>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}