import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export interface NumberFormatOptions {
  locale?: string;
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
  style?: 'decimal' | 'currency' | 'percent';
  currency?: string;
}

export function formatNumber(value: number, options: NumberFormatOptions = {}): string {
  const {
    locale = 'en-US',
    minimumFractionDigits = 0,
    maximumFractionDigits = 0,
    style = 'decimal',
    currency = 'USD'
  } = options;

  return new Intl.NumberFormat(locale, {
    style,
    currency,
    minimumFractionDigits,
    maximumFractionDigits,
  }).format(value);
}

export function formatCurrency(value: number | undefined, options: NumberFormatOptions = {}): string {
  // Use 0 as default value if undefined
  return formatNumber(value ?? 0, {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    ...options,
  });
}

export function formatPercent(value: number | undefined, options: NumberFormatOptions = {}): string {
  // Use 0 as default value if undefined
  return formatNumber(value ?? 0, {
    style: 'percent',
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
    ...options,
  });
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

export function calculateGrowth(current: number, previous: number): string {
  if (previous === 0) return '+∞%';
  const growth = (current - previous) / previous;
  const sign = growth > 0 ? '+' : '';
  return `${sign}${formatPercent(growth)}`;
}

// Helper to group data by a key
export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
  return array.reduce((result, currentValue) => {
    const groupKey = String(currentValue[key]);
    (result[groupKey] = result[groupKey] || []).push(currentValue);
    return result;
  }, {} as Record<string, T[]>);
}

// Convert a date range to an array of dates
export function dateRange(start: Date, end: Date, step = 1): Date[] {
  const dates: Date[] = [];
  let currentDate = new Date(start);

  while (currentDate <= end) {
    dates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + step);
  }

  return dates;
}

// Get a random color for charts
export function getRandomColor(): string {
  return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
}

// Generate color palette from a base color
export function generateColorPalette(baseColor: string, count: number): string[] {
  // Implementation would go here - simplified for now
  const colors: string[] = [];
  for (let i = 0; i < count; i++) {
    colors.push(getRandomColor());
  }
  return colors;
}