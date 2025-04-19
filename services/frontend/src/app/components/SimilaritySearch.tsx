'use client';

import { useState } from 'react';

type SearchType = 'text' | 'code' | 'table';

interface SimilarityResult {
  id: string;
  score: number;
  metadata: Record<string, any>;
}

interface SimilarityResponse {
  results: SimilarityResult[];
  query_type: SearchType;
}

export default function SimilaritySearch() {
  const [searchType, setSearchType] = useState<SearchType>('text');
  const [searchQuery, setSearchQuery] = useState('');
  const [tableData, setTableData] = useState('');
  const [topK, setTopK] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SimilarityResult[]>([]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const payload: Record<string, any> = {
        top_k: topK,
      };

      if (searchType === 'text') {
        payload.text = searchQuery;
      } else if (searchType === 'code') {
        payload.code = searchQuery;
      } else if (searchType === 'table') {
        try {
          payload.table = JSON.parse(tableData);
        } catch (e) {
          setError('Invalid JSON for table data');
          setIsLoading(false);
          return;
        }
      }

      const response = await fetch('/api/similarity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data: SimilarityResponse = await response.json();
      setResults(data.results);
    } catch (error) {
      setError(`Error searching: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Similarity Search</h2>
      
      <form onSubmit={handleSearch} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Type
          </label>
          <div className="flex space-x-4">
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="searchType"
                value="text"
                checked={searchType === 'text'}
                onChange={() => setSearchType('text')}
                className="form-radio h-4 w-4 text-blue-600"
              />
              <span className="ml-2">Text</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="searchType"
                value="code"
                checked={searchType === 'code'}
                onChange={() => setSearchType('code')}
                className="form-radio h-4 w-4 text-blue-600"
              />
              <span className="ml-2">Code</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="searchType"
                value="table"
                checked={searchType === 'table'}
                onChange={() => setSearchType('table')}
                className="form-radio h-4 w-4 text-blue-600"
              />
              <span className="ml-2">Table</span>
            </label>
          </div>
        </div>

        {searchType === 'table' ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Table Data (JSON)
            </label>
            <textarea
              value={tableData}
              onChange={(e) => setTableData(e.target.value)}
              className="form-textarea block w-full h-32 border border-gray-300 rounded-md shadow-sm p-3"
              placeholder='{"name": "Binary Search", "time_complexity": "O(log n)"}'
              required
            />
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {searchType === 'text' ? 'Search Text' : 'Code Snippet'}
            </label>
            <textarea
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="form-textarea block w-full h-32 border border-gray-300 rounded-md shadow-sm p-3"
              placeholder={searchType === 'text' ? "How to implement a binary search tree in Python" : "def binary_search(arr, x):..."}
              required
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of Results (top-k)
          </label>
          <input
            type="number"
            min="1"
            max="50"
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value, 10))}
            className="form-input block w-24 border border-gray-300 rounded-md shadow-sm p-3"
          />
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded">
          {error}
        </div>
      )}

      {results.length > 0 ? (
        <div className="mt-6">
          <h3 className="text-xl font-bold mb-3">Results</h3>
          <div className="space-y-4">
            {results.map((result, index) => (
              <div key={index} className="p-4 border rounded-md shadow-sm">
                <div className="flex justify-between">
                  <span className="font-bold">Result #{index + 1}</span>
                  <span className="text-blue-600 font-medium">Score: {result.score.toFixed(4)}</span>
                </div>
                <div className="mt-2">
                  <h4 className="font-medium text-gray-700">Metadata:</h4>
                  <pre className="bg-gray-100 p-2 rounded text-sm mt-1 overflow-x-auto">
                    {JSON.stringify(result.metadata, null, 2)}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : isLoading ? (
        <div className="mt-6 text-center text-gray-600">Searching...</div>
      ) : (
        <div className="mt-6 text-center text-gray-600">No results to display</div>
      )}
    </div>
  );
}