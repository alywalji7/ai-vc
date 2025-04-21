'use client';

import Link from 'next/link';
import { trpc } from '@/lib/trpc/client';

export default function HomePage() {
  const { data: fundPerformance, isLoading } = trpc.dashboard.getFundPerformance.useQuery();

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
    return `$${value}`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="space-y-8">
      <div className="text-center py-10">
        <h1 className="text-4xl font-bold">Welcome to the AI.VC LP Portal</h1>
        <p className="text-lg mt-3 text-gray-600 dark:text-gray-400">
          Access real-time fund performance, deal memos, and compliance data
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center">
          <div className="text-xl font-medium">Loading fund data...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Fund Name</h3>
            <p className="text-2xl font-bold">{fundPerformance?.name}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Vintage {fundPerformance?.vintage}</p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Committed Capital</h3>
            <p className="text-2xl font-bold">{formatCurrency(fundPerformance?.committed || 0)}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{formatCurrency(fundPerformance?.contributed || 0)} Contributed</p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Fund Value</h3>
            <p className="text-2xl font-bold">{formatCurrency(fundPerformance?.nav || 0)}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">TVPI: {fundPerformance?.tvpi.toFixed(2)}x</p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Net IRR</h3>
            <p className="text-2xl font-bold">{formatPercentage(fundPerformance?.irr || 0)}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">DPI: {fundPerformance?.dpi.toFixed(2)}x</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link 
          href="/dashboard" 
          className="block bg-white dark:bg-gray-800 rounded-xl shadow hover:shadow-lg transition-shadow p-6"
        >
          <h2 className="text-xl font-semibold flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Fund Dashboard
          </h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">View fund performance metrics, portfolio companies, and sector allocation.</p>
        </Link>

        <Link 
          href="/deal-memos" 
          className="block bg-white dark:bg-gray-800 rounded-xl shadow hover:shadow-lg transition-shadow p-6"
        >
          <h2 className="text-xl font-semibold flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Deal Memos
          </h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Access detailed investment memos for all portfolio companies.</p>
        </Link>

        <Link 
          href="/audit-trail" 
          className="block bg-white dark:bg-gray-800 rounded-xl shadow hover:shadow-lg transition-shadow p-6"
        >
          <h2 className="text-xl font-semibold flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            Audit Trail
          </h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">View compliance audit logs and data integrity verifications.</p>
        </Link>
      </div>
    </div>
  );
}