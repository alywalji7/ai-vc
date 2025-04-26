import React, { useState } from 'react';
import { formatCurrency, formatPercent } from '../../lib/utils';

interface Holding {
  id: string;
  name: string;
  value: number;
  tvpi: number;
  sector: string;
}

interface DataTableProps {
  data: Holding[];
  isLoading?: boolean;
}

const DataTable: React.FC<DataTableProps> = ({ data, isLoading = false }) => {
  const [sortField, setSortField] = useState<keyof Holding>('value');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Handle sorting
  const handleSort = (field: keyof Holding) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc'); // Default to descending when changing sort field
    }
  };

  // Apply sorting to data
  const sortedData = React.useMemo(() => {
    if (!data) return [];
    return [...data].sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      } else {
        // For numbers
        return sortDirection === 'asc'
          ? (aValue as number) - (bValue as number)
          : (bValue as number) - (aValue as number);
      }
    });
  }, [data, sortField, sortDirection]);

  // Loading state UI
  if (isLoading) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 animate-pulse">
        <div className="h-12 bg-gray-200"></div>
        <div className="p-4 space-y-3">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-10 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
      <h3 className="text-lg font-medium p-4 border-b border-gray-200">Top Holdings</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort('name')}
              >
                Company
                {sortField === 'name' && (
                  <span className="ml-1">
                    {sortDirection === 'asc' ? '▲' : '▼'}
                  </span>
                )}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort('sector')}
              >
                Sector
                {sortField === 'sector' && (
                  <span className="ml-1">
                    {sortDirection === 'asc' ? '▲' : '▼'}
                  </span>
                )}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort('value')}
              >
                FMV
                {sortField === 'value' && (
                  <span className="ml-1">
                    {sortDirection === 'asc' ? '▲' : '▼'}
                  </span>
                )}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort('tvpi')}
              >
                TVPI
                {sortField === 'tvpi' && (
                  <span className="ml-1">
                    {sortDirection === 'asc' ? '▲' : '▼'}
                  </span>
                )}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedData.map((holding) => (
              <tr key={holding.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {holding.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {holding.sector}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">
                  {formatCurrency(holding.value)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                  <span className={`font-medium ${(holding.tvpi ?? 0) >= 100 ? 'text-green-600' : (holding.tvpi ?? 0) < 50 ? 'text-red-600' : 'text-yellow-600'}`}>
                    {formatPercent((holding.tvpi ?? 0) / 100)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;