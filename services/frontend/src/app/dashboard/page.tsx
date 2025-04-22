'use client';

import React from 'react';
import { trpc } from '@/lib/trpc/client';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
} from 'recharts';
import { CustomTooltip } from '@/components/ui/CustomTooltip';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { cn } from '@/lib/utils';

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
    <div className="space-y-8 pb-16">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">Committed Capital</h3>
          <p className="text-2xl font-bold text-foreground">{formatCurrency(fundPerformance?.committed || 0)}</p>
        </div>
        
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">Net Asset Value</h3>
          <p className="text-2xl font-bold text-foreground">{formatCurrency(fundPerformance?.nav || 0)}</p>
        </div>
        
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">TVPI</h3>
          <p className="text-2xl font-bold text-foreground">{fundPerformance?.tvpi.toFixed(2)}x</p>
        </div>
        
        <div className="bg-card rounded-xl shadow p-4">
          <h3 className="text-sm font-medium text-muted-foreground">IRR</h3>
          <p className="text-2xl font-bold text-foreground">{formatPercentage(fundPerformance?.irr || 0)}</p>
        </div>
      </div>
      
      <Tabs defaultValue="charts" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="charts">Charts</TabsTrigger>
          <TabsTrigger value="companies">Portfolio Companies</TabsTrigger>
        </TabsList>
        
        <TabsContent value="charts" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-card rounded-xl shadow p-4">
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
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="quarter" stroke="var(--muted-foreground)" />
                    <YAxis tickFormatter={formatCurrency} stroke="var(--muted-foreground)" />
                    <RechartsTooltip 
                      content={({ active, payload, label }) => (
                        <CustomTooltip 
                          active={active} 
                          payload={payload} 
                          label={label}
                          labelFormatter={(label) => `Quarter: ${label}`}
                          valueFormatter={formatCurrency}
                        />
                      )} 
                    />
                    <Legend />
                    <Bar dataKey="inflow" name="Capital Calls" fill="hsl(var(--brand-primary))" />
                    <Bar dataKey="outflow" name="Distributions" fill="hsl(var(--destructive))" />
                    <Bar dataKey="net" name="Net Cash Flow" fill="hsl(var(--brand-accent))" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="bg-card rounded-xl shadow p-4">
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
                    <RechartsTooltip 
                      content={({ active, payload }) => (
                        <CustomTooltip 
                          active={active} 
                          payload={payload} 
                          label=""
                          showLabel={false}
                          valueFormatter={(value) => `${value}%`}
                        />
                      )}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="companies">
          <div className="bg-card rounded-xl shadow overflow-hidden">
            <div className="p-4 border-b border-border">
              <h2 className="text-lg font-semibold">Portfolio Companies</h2>
            </div>
            
            <div className="md:hidden">
              <Accordion type="single" collapsible className="w-full">
                {companies?.map((company) => (
                  <AccordionItem key={company.id} value={company.id.toString()}>
                    <AccordionTrigger className="px-4 py-2">
                      <div className="flex items-center w-full">
                        <div className="h-8 w-8 flex-shrink-0 mr-2">
                          <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center text-muted-foreground">
                            {company.name.charAt(0)}
                          </div>
                        </div>
                        <div className="text-sm font-medium">{company.name}</div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="px-4 py-2 space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Sector:</span>
                          <span>{company.sector}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Stage:</span>
                          <span>{company.stage}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Investment:</span>
                          <span>{formatCurrency(company.initial_investment)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Current Value:</span>
                          <span>{formatCurrency(company.current_valuation)}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">MOIC:</span>
                          <span className={cn(
                            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                            company.moic >= 2 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                            company.moic >= 1 ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' :
                            'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                          )}>
                            {company.moic.toFixed(1)}x
                          </span>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </div>
            
            <div className="hidden md:block overflow-x-auto">
              <table className="min-w-full divide-y divide-border">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Company</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Sector</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Stage</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Investment</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Current Value</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">MOIC</th>
                  </tr>
                </thead>
                <tbody className="bg-card divide-y divide-border">
                  {companies?.map((company) => (
                    <tr key={company.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 flex-shrink-0 mr-3">
                            <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center text-muted-foreground">
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
                        <span className={cn(
                          "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                          company.moic >= 2 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                          company.moic >= 1 ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' :
                          'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                        )}>
                          {company.moic.toFixed(1)}x
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}