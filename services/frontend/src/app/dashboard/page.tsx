'use client';

import React from 'react';
import { trpc } from '@/lib/trpc/client';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function DashboardPage() {
  const { data: fundPerformance, isLoading: isLoadingFund } = 
    trpc.dashboard.getFundPerformance.useQuery();
  
  const { data: companies, isLoading: isLoadingCompanies } = 
    trpc.dashboard.getPortfolioCompanies.useQuery();
  
  const { data: cashflowData, isLoading: isLoadingCashflow } = 
    trpc.dashboard.getCashflowData.useQuery();
  
  const { data: sectorAllocation, isLoading: isLoadingSectors } = 
    trpc.dashboard.getSectorAllocation.useQuery();
  
  if (isLoadingFund || isLoadingCompanies || isLoadingCashflow || isLoadingSectors) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-xl font-medium">Loading dashboard data...</div>
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

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Committed Capital</h3>
          <p className="text-2xl font-bold">{formatCurrency(fundPerformance?.committed || 0)}</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Net Asset Value</h3>
          <p className="text-2xl font-bold">{formatCurrency(fundPerformance?.nav || 0)}</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">TVPI</h3>
          <p className="text-2xl font-bold">{fundPerformance?.tvpi.toFixed(2)}x</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">IRR</h3>
          <p className="text-2xl font-bold">{formatPercentage(fundPerformance?.irr || 0)}</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
          <h2 className="text-lg font-semibold mb-4">Quarterly Cash Flows</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={cashflowData?.quarters.map((quarter, i) => ({
                  quarter,
                  inflow: cashflowData.inflows[i],
                  outflow: cashflowData.outflows[i],
                  net: cashflowData.net[i],
                }))}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="quarter" />
                <YAxis tickFormatter={formatCurrency} />
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), 'Amount']} 
                  labelFormatter={(label) => `Quarter: ${label}`}
                />
                <Legend />
                <Bar dataKey="inflow" name="Capital Calls" fill="#4ade80" />
                <Bar dataKey="outflow" name="Distributions" fill="#f87171" />
                <Bar dataKey="net" name="Net Cash Flow" fill="#60a5fa" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
          <h2 className="text-lg font-semibold mb-4">Sector Allocation</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sectorAllocation}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="allocation"
                  nameKey="sector"
                  label={({ sector, allocation }) => `${sector}: ${allocation}%`}
                >
                  {sectorAllocation?.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value}%`, 'Allocation']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold">Portfolio Companies</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Sector</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Stage</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Investment</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Current Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">MOIC</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {companies?.map((company) => (
                <tr key={company.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 flex-shrink-0 mr-3">
                        <div className="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-500 dark:text-gray-300">
                          {company.name.charAt(0)}
                        </div>
                      </div>
                      <div className="text-sm font-medium">{company.name}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{company.sector}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{company.stage}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{formatCurrency(company.initial_investment)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{formatCurrency(company.current_valuation)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      company.moic >= 2 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                      company.moic >= 1 ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' :
                      'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                    }`}>
                      {company.moic.toFixed(1)}x
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}