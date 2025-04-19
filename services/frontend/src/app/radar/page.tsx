'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface CompanyScore {
  company_id: string;
  name: string;
  clos: number;
}

export default function RadarPage() {
  const [companies, setCompanies] = useState<CompanyScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(10);

  useEffect(() => {
    const fetchCompanies = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/radar?limit=${limit}`);
        if (!response.ok) {
          throw new Error(`Error fetching data: ${response.statusText}`);
        }
        const data = await response.json();
        setCompanies(data);
      } catch (err) {
        console.error('Error fetching radar data:', err);
        setError('Failed to fetch investment opportunities. The radar service might not be running.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompanies();
  }, [limit]);

  const handleLimitChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLimit(Number(e.target.value));
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-green-300';
    if (score >= 0.4) return 'bg-yellow-300';
    if (score >= 0.2) return 'bg-orange-300';
    return 'bg-red-300';
  };

  return (
    <div className="container mx-auto py-10 px-4">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Deal-Flow Radar</h1>
          <p className="text-gray-600 mt-2">
            Investment opportunities scored by our ML model based on company metrics
          </p>
        </div>
        <div>
          <Link href="/" className="text-blue-500 hover:underline">
            ← Back to Home
          </Link>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">About the Scoring Model</h2>
        <p className="text-gray-700 mb-4">
          Our Deal-Flow Radar uses a CatBoost binary classifier to identify companies with high potential 
          for top-decile exits. The model analyzes multiple features including:
        </p>
        <ul className="list-disc pl-5 text-gray-700 mb-4">
          <li>Company age and founding date</li>
          <li>GitHub stars and commit velocity</li>
          <li>Investor count and quality</li>
          <li>Founder previous exit count</li>
          <li>Social media traction</li>
          <li>Funding amount and stage</li>
        </ul>
        <p className="text-gray-700">
          The score (CLOS - Classifier Likelihood of Success) represents the probability (0-1) that the 
          company will achieve a top-decile exit based on historical data patterns.
        </p>
      </div>

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">Daily Investment Shortlist</h2>
        <div className="flex items-center">
          <label htmlFor="limit" className="mr-2 text-gray-700">Show top:</label>
          <select
            id="limit"
            value={limit}
            onChange={handleLimitChange}
            className="border rounded p-1"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-center text-gray-700">Loading investment opportunities...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 p-6 rounded-lg border border-red-200">
          <p className="text-red-700">{error}</p>
          <p className="text-gray-700 mt-2">
            Make sure the Deal-Flow Radar service is running at http://localhost:8095
          </p>
        </div>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow-md">
          {companies.length === 0 ? (
            <p className="text-center text-gray-700">No investment opportunities found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="px-4 py-2 text-left">Rank</th>
                    <th className="px-4 py-2 text-left">Company ID</th>
                    <th className="px-4 py-2 text-left">Company Name</th>
                    <th className="px-4 py-2 text-left">CLOS Score</th>
                    <th className="px-4 py-2 text-left">Visual</th>
                  </tr>
                </thead>
                <tbody>
                  {companies.map((company, index) => (
                    <tr key={company.company_id} className="border-t">
                      <td className="px-4 py-3 text-gray-800">{index + 1}</td>
                      <td className="px-4 py-3 text-gray-800 font-mono">{company.company_id}</td>
                      <td className="px-4 py-3 text-gray-800 font-medium">{company.name}</td>
                      <td className="px-4 py-3 text-gray-800">{(company.clos * 100).toFixed(2)}%</td>
                      <td className="px-4 py-3">
                        <div className="w-full bg-gray-200 rounded-full h-4">
                          <div 
                            className={`${getScoreColor(company.clos)} h-4 rounded-full`} 
                            style={{ width: `${company.clos * 100}%` }}
                          ></div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <div className="mt-8 bg-blue-50 p-4 rounded-lg border border-blue-200">
        <h3 className="text-lg font-semibold mb-2">Note</h3>
        <p className="text-gray-700">
          This model reached an AUC ≥ 0.7 on test data, indicating good predictive performance.
          The data is refreshed nightly to include the latest company metrics and market conditions.
        </p>
      </div>
    </div>
  );
}