'use client';

import { useState, useEffect } from 'react';
import { getPortfolioSummary } from '@/app/api/portfolio/utils';
import { ExclamationTriangleIcon, UpdateIcon, PieChartIcon } from '@radix-ui/react-icons';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

interface PortfolioSummaryProps {
  lpId: string;
  refreshTrigger: number;
}

interface AssetAllocation {
  category: string;
  value: number;
  percentage: number;
}

interface IndustryExposure {
  industry: string;
  value: number;
  percentage: number;
}

interface PerformanceMetrics {
  irr: number;
  moic: number;
  tvpi: number;
  dpi: number;
}

interface PortfolioSummaryData {
  totalValue: number;
  totalCompanies: number;
  totalFunds: number;
  totalDeals: number;
  assetAllocation: AssetAllocation[];
  industryExposure: IndustryExposure[];
  performanceMetrics: PerformanceMetrics;
  lastUpdated: string;
}

export default function PortfolioSummary({ lpId, refreshTrigger }: PortfolioSummaryProps) {
  const [summaryData, setSummaryData] = useState<PortfolioSummaryData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    async function fetchSummaryData() {
      setIsLoading(true);
      setError(null);
      
      try {
        const data = await getPortfolioSummary(lpId);
        setSummaryData(data);
      } catch (error: any) {
        setError(error.message || 'Failed to fetch portfolio summary');
      } finally {
        setIsLoading(false);
      }
    }
    
    if (lpId) {
      fetchSummaryData();
    }
  }, [lpId, refreshTrigger]);
  
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(value);
  };
  
  const formatPercentage = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(value);
  };
  
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const COLORS = [
    '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
    '#82CA9D', '#A4DE6C', '#D0ED57', '#FAD000', '#F28A22'
  ];
  
  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-muted/50 p-4 rounded-lg h-24">
              <div className="h-4 bg-muted rounded w-3/4 mb-3"></div>
              <div className="h-6 bg-muted rounded w-1/2"></div>
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-muted/50 p-4 rounded-lg h-64">
            <div className="h-4 bg-muted rounded w-1/3 mb-3"></div>
            <div className="flex items-center justify-center h-48">
              <div className="h-48 w-48 bg-muted rounded-full"></div>
            </div>
          </div>
          
          <div className="bg-muted/50 p-4 rounded-lg h-64">
            <div className="h-4 bg-muted rounded w-1/3 mb-3"></div>
            <div className="h-48 bg-muted rounded w-full"></div>
          </div>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-4 border border-red-200 rounded-lg bg-red-50 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
        <div className="flex items-center mb-2">
          <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
          <p className="font-medium">Error Loading Portfolio Summary</p>
        </div>
        <p>{error}</p>
      </div>
    );
  }
  
  if (!summaryData) {
    return (
      <div className="text-center py-12">
        <PieChartIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-medium mb-2">No Portfolio Data Available</h3>
        <p className="text-muted-foreground">
          Upload your portfolio files to see a summary of your investments.
        </p>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Portfolio Overview</h3>
        <div className="text-xs text-muted-foreground flex items-center">
          <UpdateIcon className="h-3 w-3 mr-1" />
          Last updated: {formatDate(summaryData.lastUpdated)}
        </div>
      </div>
      
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-muted/30 p-4 rounded-lg">
          <p className="text-sm text-muted-foreground">Total Value</p>
          <p className="text-2xl font-semibold">
            {formatCurrency(summaryData.totalValue)}
          </p>
        </div>
        
        <div className="bg-muted/30 p-4 rounded-lg">
          <p className="text-sm text-muted-foreground">Companies</p>
          <p className="text-2xl font-semibold">
            {summaryData.totalCompanies}
          </p>
        </div>
        
        <div className="bg-muted/30 p-4 rounded-lg">
          <p className="text-sm text-muted-foreground">Funds</p>
          <p className="text-2xl font-semibold">
            {summaryData.totalFunds}
          </p>
        </div>
        
        <div className="bg-muted/30 p-4 rounded-lg">
          <p className="text-sm text-muted-foreground">Total Deals</p>
          <p className="text-2xl font-semibold">
            {summaryData.totalDeals}
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="border border-border rounded-lg p-4">
          <h4 className="text-sm font-medium mb-4">Asset Allocation</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={summaryData.assetAllocation}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ category, percentage }) => `${category}: ${formatPercentage(percentage)}`}
                >
                  {summaryData.assetAllocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => formatCurrency(value)}
                  contentStyle={{ 
                    backgroundColor: 'var(--background)', 
                    borderColor: 'var(--border)',
                    borderRadius: '0.375rem'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {summaryData.assetAllocation.map((item, index) => (
              <div key={index} className="flex items-center">
                <div 
                  className="w-3 h-3 rounded-full mr-2" 
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                ></div>
                <span className="text-xs truncate">{item.category}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="border border-border rounded-lg p-4">
          <h4 className="text-sm font-medium mb-4">Industry Exposure</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={summaryData.industryExposure.slice().sort((a, b) => b.value - a.value)}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(value) => formatCurrency(value)} />
                <YAxis 
                  type="category" 
                  dataKey="industry" 
                  width={100}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  formatter={(value: number) => formatCurrency(value)}
                  contentStyle={{ 
                    backgroundColor: 'var(--background)', 
                    borderColor: 'var(--border)',
                    borderRadius: '0.375rem'
                  }}
                />
                <Bar dataKey="value" fill="#0088FE" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="border border-border rounded-lg p-4">
        <h4 className="text-sm font-medium mb-4">Performance Metrics</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">IRR</p>
            <p className="text-xl font-semibold">
              {formatPercentage(summaryData.performanceMetrics.irr)}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">MOIC</p>
            <p className="text-xl font-semibold">
              {summaryData.performanceMetrics.moic.toFixed(1)}x
            </p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">TVPI</p>
            <p className="text-xl font-semibold">
              {summaryData.performanceMetrics.tvpi.toFixed(1)}x
            </p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">DPI</p>
            <p className="text-xl font-semibold">
              {summaryData.performanceMetrics.dpi.toFixed(1)}x
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}