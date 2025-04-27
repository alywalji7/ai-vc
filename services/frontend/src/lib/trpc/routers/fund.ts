import { z } from 'zod';
import { publicProcedure, router } from '../init';

// Define types for the fund metrics
export interface FundSector {
  name: string;
  pct: number;
}

export interface FundHolding {
  company: string;
  cost: number;
  value: number;
  tvpi: number;
}

export interface FundMetrics {
  dates: string[];
  nav: number[];
  sectors: FundSector[];
  holdings: FundHolding[];
}

// Input schema for fund metrics
const getFundMetricsSchema = z.object({
  fundId: z.string()
});

export const fundRouter = router({
  // Get fund metrics including NAV history, sector allocation, and top holdings
  getMetrics: publicProcedure
    .input(getFundMetricsSchema)
    .query(async ({ input }) => {
      try {
        // In production, this would fetch from a database or metrics calculation service
        // For now, we'll create some sample fund metrics data
        
        // Generate dates and NAV data for the last 12 months
        const currentDate = new Date();
        const dates: string[] = [];
        const nav: number[] = [];
        
        // Current NAV value (will be seed for time series)
        let currentNAV = input.fundId === 'fund-1' ? 135000000 : 
                       input.fundId === 'fund-2' ? 65000000 : 
                       input.fundId === 'fund-3' ? 33000000 : 100000000;
        
        // Generate 12 months of data going backwards
        for (let i = 11; i >= 0; i--) {
          const date = new Date(currentDate);
          date.setMonth(date.getMonth() - i);
          dates.push(date.toISOString().slice(0, 10)); // YYYY-MM-DD format
          
          // Add some randomness to NAV progression, with general upward trend
          const volatility = 0.04; // 4% volatility
          const monthlyReturn = 0.01 + (Math.random() * 0.02 - 0.01); // 1% +/- 1%
          
          // Only for previous months (not current)
          if (i > 0) {
            const navChange = currentNAV * (monthlyReturn + (Math.random() * volatility - volatility / 2));
            currentNAV += navChange;
            nav.push(Math.round(currentNAV));
          } else {
            // Current month uses exact NAV
            nav.push(Math.round(currentNAV));
          }
        }
        
        // Sector allocation data
        const sectors: FundSector[] = [
          { name: 'AI & ML', pct: 0.35 },
          { name: 'SaaS', pct: 0.25 },
          { name: 'Fintech', pct: 0.15 },
          { name: 'Healthcare', pct: 0.15 },
          { name: 'Consumer', pct: 0.10 }
        ];
        
        // Fund-specific sectors
        if (input.fundId === 'fund-2') {
          sectors[0] = { name: 'Fintech', pct: 0.40 };
          sectors[1] = { name: 'AI & ML', pct: 0.20 };
        } else if (input.fundId === 'fund-3') {
          sectors[0] = { name: 'AI & ML', pct: 0.45 };
          sectors[1] = { name: 'Healthcare', pct: 0.20 };
          sectors[2] = { name: 'SaaS', pct: 0.15 };
        }
        
        // Top holdings data
        const holdings: FundHolding[] = [
          { company: 'NeuralPath AI', cost: 5000000, value: 15000000, tvpi: 3.0 },
          { company: 'QuantumSense', cost: 7500000, value: 18750000, tvpi: 2.5 },
          { company: 'DataMesh', cost: 4500000, value: 9000000, tvpi: 2.0 },
          { company: 'SecureFlow', cost: 6000000, value: 9600000, tvpi: 1.6 },
          { company: 'MedGenix', cost: 8000000, value: 12000000, tvpi: 1.5 },
          { company: 'CloudOps', cost: 5500000, value: 7700000, tvpi: 1.4 },
          { company: 'FinTechX', cost: 7000000, value: 8400000, tvpi: 1.2 },
          { company: 'RetailNext', cost: 4800000, value: 4800000, tvpi: 1.0 },
          { company: 'InnovateLabs', cost: 3500000, value: 3150000, tvpi: 0.9 },
          { company: 'EcoLogistics', cost: 6500000, value: 5200000, tvpi: 0.8 }
        ];
        
        // Fund-specific holdings
        if (input.fundId === 'fund-2') {
          holdings[0] = { company: 'PaymentFlow', cost: 6000000, value: 15000000, tvpi: 2.5 };
          holdings[1] = { company: 'WealthTech', cost: 8000000, value: 16000000, tvpi: 2.0 };
        } else if (input.fundId === 'fund-3') {
          holdings[0] = { company: 'AICore', cost: 10000000, value: 15000000, tvpi: 1.5 };
          holdings[1] = { company: 'GenomicsAI', cost: 8000000, value: 10400000, tvpi: 1.3 };
        }
        
        return {
          dates,
          nav,
          sectors,
          holdings
        };
      } catch (error) {
        console.error('Error fetching fund metrics:', error);
        throw new Error('Failed to fetch fund metrics data');
      }
    })
});