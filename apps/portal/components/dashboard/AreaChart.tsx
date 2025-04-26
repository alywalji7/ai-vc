import React from 'react';
import {
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  TooltipProps
} from 'recharts';
import { formatCurrency, formatDate } from '../../lib/utils';

interface NavDataPoint {
  date: string;
  value: number;
}

interface NavOverTimeData {
  dates: string[];
  nav: number[];
}

interface AreaChartProps {
  data: NavOverTimeData;
  isLoading?: boolean;
}

// Custom tooltip for the NAV chart
const CustomTooltip = ({
  active,
  payload,
  label
}: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="p-3 border border-gray-200 bg-white shadow-sm rounded-md">
        <p className="text-sm font-medium">{formatDate(label)}</p>
        <p className="text-lg font-bold">
          {formatCurrency(payload[0].value as number, {
            maximumFractionDigits: 0
          })}
        </p>
      </div>
    );
  }

  return null;
};

const AreaChart: React.FC<AreaChartProps> = ({ data, isLoading = false }) => {
  // Transform data for Recharts
  const chartData = data.dates.map((date, index) => ({
    date,
    value: data.nav[index]
  }));

  if (isLoading) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 h-[350px] animate-pulse">
        <div className="h-full w-full flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-lg font-medium mb-3">Net Asset Value Over Time</h3>
      <ResponsiveContainer width="100%" height={300}>
        <RechartsAreaChart
          data={chartData}
          margin={{
            top: 10,
            right: 0,
            left: 0,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(value) => formatDate(value)}
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            tickFormatter={(value) => formatCurrency(value, {
              maximumFractionDigits: 1
            })} 
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#2563eb"
            fill="#dbeafe"
            activeDot={{ r: 6 }}
            isAnimationActive={true}
            animationDuration={1000}
          />
        </RechartsAreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AreaChart;