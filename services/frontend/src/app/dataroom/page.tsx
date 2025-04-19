'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface DataRoom {
  company_id: string;
  name: string;
  radar_score: number;
}

export default function DataRoomListPage() {
  const [datarooms, setDatarooms] = useState<DataRoom[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDataRooms() {
      try {
        const response = await fetch('/api/dataroom');
        if (!response.ok) {
          throw new Error(`Error fetching data rooms: ${response.statusText}`);
        }
        const data = await response.json();
        setDatarooms(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data rooms:', err);
        setError('Failed to load data rooms');
        setLoading(false);
      }
    }

    fetchDataRooms();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Data Rooms</h1>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <p className="text-gray-500">Loading data rooms...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Data Rooms</h1>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <p className="text-red-500">{error}</p>
            <p className="mt-4">
              No data rooms available. Data rooms are created automatically when companies are green-lit by the radar service.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Data Rooms</h1>
        
        {datarooms.length === 0 ? (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <p className="text-gray-500">
              No data rooms available. Data rooms are created automatically when companies are green-lit by the radar service.
            </p>
          </div>
        ) : (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Radar Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {datarooms.map((dataroom) => (
                    <tr key={dataroom.company_id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{dataroom.name}</div>
                        <div className="text-sm text-gray-500">ID: {dataroom.company_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {(dataroom.radar_score * 100).toFixed(1)}%
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Link href={`/dataroom/${dataroom.company_id}`} className="text-indigo-600 hover:text-indigo-900">
                          View Data Room
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
        
        <div className="mt-8">
          <Link href="/radar" className="text-indigo-600 hover:text-indigo-900">
            &larr; Back to Radar
          </Link>
        </div>
      </div>
    </div>
  );
}