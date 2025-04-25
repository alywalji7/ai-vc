'use client';

import { useState, useEffect } from 'react';
import { getPortfolioHoldings } from '@/app/api/portfolio/utils';
import { ReloadIcon, ExclamationTriangleIcon, ArrowUpIcon, ArrowDownIcon } from '@radix-ui/react-icons';

interface Holding {
  id: number;
  lp_id: string;
  company_name: string;
  cost_basis: number;
  current_value: number;
  currency: string;
  acquisition_date: string | null;
  valuation_date: string;
  notes: string | null;
  file_id: number;
}

interface HoldingsTableProps {
  lpId: string;
  refreshTrigger: number;
}

export default function HoldingsTable({ lpId, refreshTrigger }: HoldingsTableProps) {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortField, setSortField] = useState<keyof Holding>('company_name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    const fetchHoldings = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getPortfolioHoldings(lpId);
        setHoldings(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch portfolio holdings');
      } finally {
        setLoading(false);
      }
    };

    fetchHoldings();
  }, [lpId, refreshTrigger]);

  // Format currency
  const formatCurrency = (value: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Calculate multiple
  const calculateMultiple = (current: number, cost: number) => {
    if (cost === 0) return '-';
    return (current / cost).toFixed(2) + 'x';
  };

  // Toggle sort direction or set new sort field
  const handleSort = (field: keyof Holding) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Sort holdings based on current sort field and direction
  const sortedHoldings = [...holdings].sort((a, b) => {
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
        <p className="mt-2 text-gray-600">Loading holdings...</p>
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

  if (holdings.length === 0) {
    return (
      <div className="py-10 text-center border border-dashed rounded-lg">
        <p className="text-gray-500">No holdings data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Direct Holdings</h3>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900/50">
              <tr>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('company_name')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Company</span>
                    {sortField === 'company_name' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('cost_basis')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Cost Basis</span>
                    {sortField === 'cost_basis' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('current_value')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Current Value</span>
                    {sortField === 'current_value' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Multiple
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('acquisition_date')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Acquisition Date</span>
                    {sortField === 'acquisition_date' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('valuation_date')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Valuation Date</span>
                    {sortField === 'valuation_date' && (
                      sortDirection === 'asc' ? <ArrowUpIcon className="h-4 w-4" /> : <ArrowDownIcon className="h-4 w-4" />
                    )}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {sortedHoldings.map((holding) => {
                const multiple = holding.cost_basis > 0 
                  ? holding.current_value / holding.cost_basis 
                  : 0;
                const isPositive = multiple >= 1;
                
                return (
                  <tr key={holding.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                      {holding.company_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(holding.cost_basis, holding.currency)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(holding.current_value, holding.currency)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <span className={isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                        {calculateMultiple(holding.current_value, holding.cost_basis)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(holding.acquisition_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(holding.valuation_date)}
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