'use client';

import React from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { trpc } from '@/lib/trpc/client';

export default function DealMemoDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { data: memo, isLoading } = trpc.dealMemos.getDealMemoById.useQuery({ id: params.id });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-xl font-medium">Loading deal memo...</div>
      </div>
    );
  }

  if (!memo) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <div className="text-xl font-medium">Deal memo not found</div>
        <button 
          onClick={() => router.back()} 
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md"
        >
          Go Back
        </button>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
    return `$${value}`;
  };

  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'rejected':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2">
            <Link href="/deal-memos" className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">
              ← Back to Deal Memos
            </Link>
          </div>
          <h1 className="text-3xl font-bold mt-2">{memo.company_name}</h1>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-gray-500 dark:text-gray-400">{memo.stage}</span>
            <span className="text-gray-500 dark:text-gray-400">•</span>
            <span className="text-gray-500 dark:text-gray-400">{formatDate(memo.memo_date)}</span>
            <span className="text-gray-500 dark:text-gray-400">•</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(memo.decision)}`}>
              {memo.decision.charAt(0).toUpperCase() + memo.decision.slice(1)}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Investment Thesis</h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">{memo.investment_thesis}</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Market Analysis</h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">{memo.market_analysis}</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Team Assessment</h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">{memo.team_assessment}</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Product Analysis</h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">{memo.product_analysis}</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Financial Overview</h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">{memo.financial_overview}</p>
          </div>

          {memo.decision_rationale && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Decision Rationale</h2>
              <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">{memo.decision_rationale}</p>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Investment Details</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Valuation</h3>
                <p className="text-xl font-bold">{formatCurrency(memo.valuation)}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Proposed Investment</h3>
                <p className="text-xl font-bold">{formatCurrency(memo.proposed_investment)}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Recommended Allocation</h3>
                <p className="text-xl font-bold">{memo.recommended_allocation}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">IC Members</h2>
            <div className="space-y-2">
              {memo.ic_members.map((member, index) => (
                <div key={index} className="flex items-center">
                  <div className="h-8 w-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-800 dark:text-indigo-200 mr-3">
                    {member.split(' ').map(n => n[0]).join('')}
                  </div>
                  <span>{member}</span>
                </div>
              ))}
            </div>
          </div>

          {memo.attachments && memo.attachments.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Attachments</h2>
              <div className="space-y-2">
                {memo.attachments.map((attachment) => (
                  <div key={attachment.id} className="flex items-center">
                    <span className="flex-1">{attachment.name}</span>
                    <Link 
                      href={attachment.url}
                      className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
                    >
                      Download
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}