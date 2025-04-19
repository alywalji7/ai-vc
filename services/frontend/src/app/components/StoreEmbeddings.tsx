'use client';

import { useState } from 'react';

type ItemType = 'text' | 'code' | 'table';

interface StoreItem {
  text?: string;
  code?: string;
  table?: Record<string, any>;
  [key: string]: any;
}

export default function StoreEmbeddings() {
  const [itemType, setItemType] = useState<ItemType>('text');
  const [content, setContent] = useState('');
  const [tableData, setTableData] = useState('');
  const [metadata, setMetadata] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [ids, setIds] = useState<string[]>([]);

  const handleStore = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    setIds([]);

    try {
      const item: StoreItem = {};
      let parsedMetadata = {};

      // Parse metadata if provided
      if (metadata.trim()) {
        try {
          parsedMetadata = JSON.parse(metadata);
        } catch (e) {
          setError('Invalid JSON metadata format');
          setIsLoading(false);
          return;
        }
      }

      // Add content based on item type
      if (itemType === 'text') {
        item.text = content;
      } else if (itemType === 'code') {
        item.code = content;
      } else if (itemType === 'table') {
        try {
          item.table = JSON.parse(tableData);
        } catch (e) {
          setError('Invalid JSON for table data');
          setIsLoading(false);
          return;
        }
      }

      // Merge with metadata
      Object.assign(item, parsedMetadata);

      const response = await fetch('/api/similarity/store', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: [item]
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setIds(data.ids || []);
      setSuccess(`Item stored successfully! ${data.storage_status === 'skipped' ? '(Note: Qdrant storage was skipped, but IDs were generated)' : ''}`);
    } catch (error) {
      setError(`Error storing item: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Store Embeddings</h2>
      
      <form onSubmit={handleStore} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Item Type
          </label>
          <div className="flex space-x-4">
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="itemType"
                value="text"
                checked={itemType === 'text'}
                onChange={() => setItemType('text')}
                className="form-radio h-4 w-4 text-blue-600"
              />
              <span className="ml-2">Text</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="itemType"
                value="code"
                checked={itemType === 'code'}
                onChange={() => setItemType('code')}
                className="form-radio h-4 w-4 text-blue-600"
              />
              <span className="ml-2">Code</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="itemType"
                value="table"
                checked={itemType === 'table'}
                onChange={() => setItemType('table')}
                className="form-radio h-4 w-4 text-blue-600"
              />
              <span className="ml-2">Table</span>
            </label>
          </div>
        </div>

        {itemType === 'table' ? (
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
              {itemType === 'text' ? 'Text Content' : 'Code Snippet'}
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="form-textarea block w-full h-32 border border-gray-300 rounded-md shadow-sm p-3"
              placeholder={itemType === 'text' ? "How to implement a binary search tree in Python" : "def binary_search(arr, x):..."}
              required
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional Metadata (JSON, optional)
          </label>
          <textarea
            value={metadata}
            onChange={(e) => setMetadata(e.target.value)}
            className="form-textarea block w-full h-20 border border-gray-300 rounded-md shadow-sm p-3"
            placeholder='{"source": "stackoverflow", "created_at": "2025-04-19T10:00:00Z"}'
          />
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
          >
            {isLoading ? 'Storing...' : 'Store Item'}
          </button>
        </div>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="mt-4 p-3 bg-green-50 text-green-700 border border-green-200 rounded">
          {success}
        </div>
      )}

      {ids.length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-bold mb-3">Stored Item IDs</h3>
          <div className="bg-gray-100 p-3 rounded">
            <pre className="text-sm overflow-x-auto">{ids.join('\n')}</pre>
          </div>
        </div>
      )}
    </div>
  );
}