'use client';

import { useState, useEffect } from 'react';
import { getPortfolioFunds } from '@/app/api/portfolio/utils';
import { ReloadIcon, ExclamationTriangleIcon, ArrowUpIcon, ArrowDownIcon } from '@radix-ui/react-icons';

interface Fund {
  id: number;
  lp_id: string;
  fund_name: string;
  committed_capital: number;
  contributed_capital: number;
  remaining_capital: number;
  distributed_capital: number;
  nav: number;
  vintage_year: number | null;
  currency: string;
  valuation_date: string;
  irr: number | null;
  tvpi: number | null;
  dpi: number | null;
  file_id: number;
}

interface FundsTableProps {
  lpId: string;
  refreshTrigger: number;
}

export default function FundsTable({ lpId, refreshTrigger }: FundsTableProps) {
  const [funds, setFunds] = useState<Fund[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortField, setSortField] = useState<keyof Fund>('fund_name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    const fetchFunds = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getPortfolioFunds(lpId);
        setFunds(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch fund positions');
      } finally {
        setLoading(false);
      }
    };

    fetchFunds();
  }, [lpId, refreshTrigger]);

  // Format currency
  const formatCurrency = (value: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format percentage
  const formatPercentage = (value: number | null) => {
    if (value === null) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(value);
  };

  // Format multiplier
  const formatMultiplier = (value: number | null) => {
    if (value === null) return '-';
    return value.toFixed(2) + 'x';
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Toggle sort direction or set new sort field
  const handleSort = (field: keyof Fund) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Sort funds based on current sort field and direction
  const sortedFunds = [...funds].sort((a, b) => {
    const aValue = a[sortField];
    const bValue = b[sortField];
    
    if (aValue === null) return sortDirection === 'asc' ? 1 : -1;
    if (bValue === null) return sortDirection === 'asc' ? -1 : 1;
    
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortDirection === 'asc' 
        ? aValue.localeCompare(bValue) 
        : bValue.localeCompare(aValue);
    }
    
    // @ts-ignore - we know these are comparable
    return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
  });

  if (loading) {
    return (
      <div className="py-10 text-center">
        <ReloadIcon className="w-8 h-8 mx-auto text-blue-600 animate-spin" />
        <p className="mt-2 text-gray-600">Loading fund positions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-10 text-center">
        <ExclamationTriangleIcon className="w-8 h-8 mx-auto text-red-600" />
        <p className="mt-2 text-red-600">{error}</p>
      </div>
    );
  }

  if (funds.length === 0) {
    return (
      <div className="py-10 text-center border border-dashed rounded-lg">
        <p className="text-gray-500">No fund position data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Fund Positions</h3>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900/50">
              <tr>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('fund_name')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Fund</span>
                    {sortField === 'fund_name' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('vintage_year')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Vintage</span>
                    {sortField === 'vintage_year' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('committed_capital')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Committed</span>
                    {sortField === 'committed_capital' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('contributed_capital')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Contributed</span>
                    {sortField === 'contributed_capital' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('remaining_capital')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Remaining</span>
                    {sortField === 'remaining_capital' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('nav')}
                >
                  <div className="flex items-center space-x-1">
                    <span>NAV</span>
                    {sortField === 'nav' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('irr')}
                >
                  <div className="flex items-center space-x-1">
                    <span>IRR</span>
                    {sortField === 'irr' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('tvpi')}
                >
                  <div className="flex items-center space-x-1">
                    <span>TVPI</span>
                    {sortField === 'tvpi' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('dpi')}
                >
                  <div className="flex items-center space-x-1">
                    <span>DPI</span>
                    {sortField === 'dpi' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {sortedFunds.map((fund) => {
                const isPositiveIRR = fund.irr !== null && fund.irr > 0;
                
                return (
                  <tr key={fund.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                      {fund.fund_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {fund.vintage_year || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(fund.committed_capital, fund.currency)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(fund.contributed_capital, fund.currency)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(fund.remaining_capital, fund.currency)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(fund.nav, fund.currency)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {fund.irr !== null && (
                        <span className={isPositiveIRR ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                          {formatPercentage(fund.irr)}
                        </span>
                      )}
                      {fund.irr === null && (
                        <span className="text-gray-500 dark:text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-600 dark:text-gray-300">
                      {formatMultiplier(fund.tvpi)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-600 dark:text-gray-300">
                      {formatMultiplier(fund.dpi)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}