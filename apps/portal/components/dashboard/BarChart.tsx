import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps
} from 'recharts';
import { formatPercent } from '../../lib/utils';

interface SectorAllocation {
  name: string;
  pct: number;
}

interface BarChartProps {
  data: SectorAllocation[];
  isLoading?: boolean;
}

// Define color scheme for the sectors
const SECTOR_COLORS = [
  '#3b82f6', // blue-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#6366f1', // indigo-500
  '#ec4899', // pink-500
  '#8b5cf6', // violet-500
  '#14b8a6', // teal-500
  '#f43f5e', // rose-500
  '#0ea5e9', // sky-500
  '#84cc16', // lime-500
];

// Custom tooltip for the sector allocation chart
const CustomTooltip = ({
  active,
  payload,
}: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div className="p-3 border border-gray-200 bg-white shadow-sm rounded-md">
        <p className="text-sm font-medium">{data.name}</p>
        <p className="text-lg font-bold" style={{ color: data.color }}>
          {formatPercent(data.value as number)}
        </p>
      </div>
    );
  }
  return null;
};

const BarChart: React.FC<BarChartProps> = ({ data, isLoading = false }) => {
  // Transform data for the recharts-friendly format
  const chartData = data.map((sector) => ({
    name: sector.name,
    [sector.name]: sector.pct,
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
      <h3 className="text-lg font-medium mb-3">Sector Allocation</h3>
      <ResponsiveContainer width="100%" height={300}>
        <RechartsBarChart
          data={chartData}
          margin={{
            top: 10,
            right: 0,
            left: 0,
            bottom: 0,
          }}
          layout="vertical"
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
          <XAxis
            type="number"
            tickFormatter={(value: number) => formatPercent(value)}
            domain={[0, 1]}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 12 }}
            hide={true}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend layout="horizontal" verticalAlign="bottom" align="center" />
          {data.map((sector, index) => (
            <Bar
              key={sector.name}
              dataKey={sector.name}
              stackId="a"
              fill={SECTOR_COLORS[index % SECTOR_COLORS.length]}
              isAnimationActive={true}
              animationDuration={1000}
            />
          ))}
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BarChart;