'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface DataRoom {
  id: string;
  name: string;
  radar_score: number;
  generation_timestamp: string;
}

export default function DataRoomPage() {
  const [dataRooms, setDataRooms] = useState<DataRoom[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDataRooms = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/dataroom');
        
        if (!response.ok) {
          throw new Error(`Error fetching datarooms: ${response.statusText}`);
        }
        
        const data = await response.json();
        setDataRooms(data.datarooms || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        console.error('Error fetching datarooms:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDataRooms();
  }, []);

  const formatTimestamp = (timestamp: string) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const formatScore = (score: number) => {
    return (score * 100).toFixed(0) + '%';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Data Rooms</h1>
      
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
      
      {!loading && dataRooms.length === 0 && !error && (
        <div className="bg-gray-100 p-6 rounded-lg text-center">
          <p className="text-gray-700">No data rooms available yet.</p>
        </div>
      )}
      
      {dataRooms.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dataRooms.map((dataRoom) => (
            <Link href={`/dataroom/${dataRoom.id}`} key={dataRoom.id}>
              <div className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition duration-200 h-full flex flex-col">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-xl font-semibold">{dataRoom.name}</h2>
                  <div className={`px-3 py-1 rounded-full text-sm ${
                    dataRoom.radar_score >= 0.8 ? 'bg-green-100 text-green-800' :
                    dataRoom.radar_score >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {formatScore(dataRoom.radar_score)}
                  </div>
                </div>
                
                <div className="mt-auto pt-4 text-sm text-gray-500">
                  Generated: {formatTimestamp(dataRoom.generation_timestamp)}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}