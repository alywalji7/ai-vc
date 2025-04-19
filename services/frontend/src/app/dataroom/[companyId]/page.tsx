'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface DataRoomMetadata {
  company_id: string;
  name: string;
  available_files: string[];
  summary_html: string | null;
  generation_timestamp: string | null;
}

export default function DataRoomPage({ params }: { params: { companyId: string } }) {
  const [dataroom, setDataroom] = useState<DataRoomMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDataRoom() {
      try {
        const response = await fetch(`/api/dataroom/${params.companyId}`);
        if (!response.ok) {
          throw new Error(`Error fetching data room: ${response.statusText}`);
        }
        const data = await response.json();
        setDataroom(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data room:', err);
        setError('Failed to load data room');
        setLoading(false);
      }
    }

    fetchDataRoom();
  }, [params.companyId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Data Room</h1>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <p className="text-gray-500">Loading data room...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !dataroom) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Data Room</h1>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <p className="text-red-500">{error || 'Data room not found'}</p>
          </div>
          <div className="mt-8">
            <Link href="/dataroom" className="text-indigo-600 hover:text-indigo-900">
              &larr; Back to Data Rooms
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">{dataroom.name} Data Room</h1>
        <p className="text-gray-500 mb-8">Company ID: {dataroom.company_id}</p>
        
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          {dataroom.summary_html ? (
            <div 
              dangerouslySetInnerHTML={{ __html: dataroom.summary_html }} 
              className="prose max-w-none"
            />
          ) : (
            <p className="text-gray-500">No summary available</p>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-xl font-semibold mb-4">Available Files</h2>
          {dataroom.available_files && dataroom.available_files.length > 0 ? (
            <ul className="space-y-2">
              {dataroom.available_files.map((file) => (
                <li key={file}>
                  <a 
                    href={`/api/dataroom/${dataroom.company_id}/file/${file}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    {file}
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No files available</p>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-xl font-semibold mb-4">API Access</h2>
          <p className="mb-4">
            Raw JSON data is available at the following endpoint:
          </p>
          <div className="bg-gray-100 p-4 rounded font-mono text-sm">
            <code>GET /api/dataroom/{dataroom.company_id}/data</code>
          </div>
        </div>
        
        <div className="mt-8">
          <Link href="/dataroom" className="text-indigo-600 hover:text-indigo-900">
            &larr; Back to Data Rooms
          </Link>
        </div>
      </div>
    </div>
  );
}