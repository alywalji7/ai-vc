'use client';

import { useState, useEffect } from 'react';

interface Feedback {
  id: number;
  user_id: string;
  sentiment: string;
  message: string;
  created_at: string;
}

interface LP {
  id: number;
  email: string;
  name: string | null;
  organization: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

interface Founder {
  id: number;
  email: string;
  name: string | null;
  company_name: string | null;
  deck_url: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function BetaFeedbackPage() {
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [lps, setLps] = useState<LP[]>([]);
  const [founders, setFounders] = useState<Founder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('feedback');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError('');
      
      try {
        // Fetch feedback data
        const feedbackResponse = await fetch('/api/admin/beta-feedback/feedback');
        if (!feedbackResponse.ok) {
          throw new Error('Failed to fetch feedback data');
        }
        const feedbackData = await feedbackResponse.json();
        setFeedback(feedbackData);

        // Fetch LP data
        const lpsResponse = await fetch('/api/admin/beta-feedback/lps');
        if (!lpsResponse.ok) {
          throw new Error('Failed to fetch LP data');
        }
        const lpsData = await lpsResponse.json();
        setLps(lpsData);

        // Fetch founder data
        const foundersResponse = await fetch('/api/admin/beta-feedback/founders');
        if (!foundersResponse.ok) {
          throw new Error('Failed to fetch founder data');
        }
        const foundersData = await foundersResponse.json();
        setFounders(foundersData);
      } catch (err: any) {
        console.error('Error fetching data:', err);
        setError(err.message || 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const exportFeedback = async () => {
    try {
      window.open(`${process.env.BETA_FEEDBACK_URL || 'http://localhost:8200'}/feedback/export?format=csv`, '_blank');
    } catch (err: any) {
      console.error('Error exporting feedback:', err);
      setError(err.message || 'Failed to export feedback');
    }
  };

  const sentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'bg-green-100 text-green-800';
      case 'negative':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto mt-10 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Beta Feedback Dashboard</h1>
        {activeTab === 'feedback' && (
          <button
            onClick={exportFeedback}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Export CSV
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100 rounded">
          {error}
        </div>
      )}

      <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
        <ul className="flex flex-wrap -mb-px">
          <li className="mr-2">
            <button
              className={`inline-block p-4 border-b-2 rounded-t-lg ${
                activeTab === 'feedback'
                  ? 'border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-500'
                  : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('feedback')}
            >
              Feedback
            </button>
          </li>
          <li className="mr-2">
            <button
              className={`inline-block p-4 border-b-2 rounded-t-lg ${
                activeTab === 'lps'
                  ? 'border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-500'
                  : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('lps')}
            >
              Limited Partners
            </button>
          </li>
          <li className="mr-2">
            <button
              className={`inline-block p-4 border-b-2 rounded-t-lg ${
                activeTab === 'founders'
                  ? 'border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-500'
                  : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('founders')}
            >
              Founders
            </button>
          </li>
        </ul>
      </div>

      {loading ? (
        <div className="text-center p-10">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4">Loading data...</p>
        </div>
      ) : (
        <>
          {activeTab === 'feedback' && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Sentiment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Message
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                  {feedback.map((item) => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {item.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {item.user_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${sentimentColor(item.sentiment)}`}>
                          {item.sentiment}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-md truncate">
                        {item.message}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {new Date(item.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                  {feedback.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                        No feedback data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'lps' && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Organization
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                  {lps.map((lp) => (
                    <tr key={lp.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {lp.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {lp.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {lp.name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {lp.organization || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          lp.status === 'ACTIVE' 
                            ? 'bg-green-100 text-green-800' 
                            : lp.status === 'INACTIVE' 
                              ? 'bg-red-100 text-red-800' 
                              : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {lp.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {new Date(lp.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                  {lps.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                        No LP data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'founders' && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Deck
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                  {founders.map((founder) => (
                    <tr key={founder.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {founder.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {founder.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {founder.name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {founder.company_name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {founder.deck_url ? (
                          <a 
                            href={founder.deck_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            View Deck
                          </a>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          founder.status === 'ACTIVE' 
                            ? 'bg-green-100 text-green-800' 
                            : founder.status === 'REJECTED' 
                              ? 'bg-red-100 text-red-800' 
                              : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {founder.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {new Date(founder.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                  {founders.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                        No founder data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}