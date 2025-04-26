import { z } from 'zod';
import { publicProcedure, router } from '@/lib/trpc/init';
import { Startup } from '@/app/startups/components/StartupCard';
import { FilterValues } from '@/app/startups/components/FilterDrawer';

// Sample data for development
const SAMPLE_STARTUPS: Startup[] = [
  {
    id: '1',
    name: 'Quantum AI',
    logoUrl: '/sample/quantum-ai-logo.png',
    sector: 'AI & ML',
    radarScore: 0.92,
    geography: 'USA',
    upvotes: 24,
    description: 'Building conversational AI assistants for enterprise knowledge management',
    founded: 2022,
    website: 'https://quantumai.example'
  },
  {
    id: '2',
    name: 'CarboCapture',
    logoUrl: '/sample/carbocapture-logo.png',
    sector: 'CleanTech',
    radarScore: 0.85,
    geography: 'EU',
    upvotes: 18,
    description: 'Direct air carbon capture technology with minimal energy requirements',
    founded: 2021,
    website: 'https://carbocapture.example'
  },
  {
    id: '3',
    name: 'BioGenomics',
    logoUrl: null,
    sector: 'BioTech',
    radarScore: 0.76,
    geography: 'USA',
    upvotes: 12,
    description: 'Gene editing platform for rare disease therapies',
    founded: 2023,
    website: 'https://biogenomics.example'
  },
  {
    id: '4',
    name: 'SpaceHarbor',
    logoUrl: '/sample/spaceharbor-logo.png',
    sector: 'Space',
    radarScore: 0.88,
    geography: 'USA',
    upvotes: 32,
    description: 'Modular space habitats for low Earth orbit commercial stations',
    founded: 2020,
    website: 'https://spaceharbor.example'
  },
  {
    id: '5',
    name: 'FinFlow',
    logoUrl: null,
    sector: 'FinTech',
    radarScore: 0.68,
    geography: 'APAC',
    upvotes: 7,
    description: 'Cross-border payment infrastructure for emerging markets',
    founded: 2022,
    website: 'https://finflow.example'
  },
  {
    id: '6',
    name: 'HealthSync',
    logoUrl: '/sample/healthsync-logo.png',
    sector: 'HealthTech',
    radarScore: 0.79,
    geography: 'EU',
    upvotes: 15,
    description: 'Remote patient monitoring platform with predictive analytics',
    founded: 2021,
    website: 'https://healthsync.example'
  },
  {
    id: '7',
    name: 'AgriSense',
    logoUrl: '/sample/agrisense-logo.png',
    sector: 'AgTech',
    radarScore: 0.81,
    geography: 'ROW',
    upvotes: 21,
    description: 'Precision agriculture sensors and analytics platform',
    founded: 2022,
    website: 'https://agrisense.example'
  },
  {
    id: '8',
    name: 'QuantumCompute',
    logoUrl: null,
    sector: 'Quantum',
    radarScore: 0.95,
    geography: 'USA',
    upvotes: 42,
    description: 'Error-corrected quantum processors for commercial applications',
    founded: 2019,
    website: 'https://quantumcompute.example'
  }
];

const AVAILABLE_SECTORS = [
  'AI & ML',
  'CleanTech',
  'BioTech',
  'Space',
  'FinTech',
  'HealthTech',
  'AgTech',
  'Quantum',
  'Robotics',
  'Blockchain',
  'AR/VR',
  'Cybersecurity',
  'EdTech',
  'Mobility'
];

export const startupRouter = router({
  getStartups: publicProcedure
    .input(z.object({
      minScore: z.number().min(0).max(1).default(0.5),
      sectors: z.array(z.string()).default([]),
      geography: z.enum(['USA', 'EU', 'APAC', 'ROW']).optional(),
    }))
    .query(async ({ input }) => {
      // TODO: Replace with actual API call to backend
      
      // Filter startups based on input
      return SAMPLE_STARTUPS.filter(startup => {
        // Filter by minimum radar score
        if (startup.radarScore < input.minScore) return false;
        
        // Filter by sectors if any are selected
        if (input.sectors.length > 0 && !input.sectors.includes(startup.sector)) return false;
        
        // Filter by geography if specified
        if (input.geography && startup.geography !== input.geography) return false;
        
        return true;
      });
    }),
    
  getSectors: publicProcedure
    .query(async () => {
      // TODO: Replace with actual API call to backend
      return AVAILABLE_SECTORS;
    }),
    
  getStartupById: publicProcedure
    .input(z.object({
      id: z.string()
    }))
    .query(async ({ input }) => {
      // TODO: Replace with actual API call to backend
      const startup = SAMPLE_STARTUPS.find(s => s.id === input.id);
      if (!startup) throw new Error('Startup not found');
      return startup;
    }),
    
  upvote: publicProcedure
    .input(z.object({
      id: z.string()
    }))
    .mutation(async ({ input }) => {
      // TODO: Replace with actual API call to backend
      console.log(`Upvoted startup ${input.id}`);
      return { success: true };
    }),
    
  suggestStartup: publicProcedure
    .input(z.object({
      name: z.string().min(2),
      website: z.string().url(),
      sector: z.string(),
      description: z.string().optional(),
      notes: z.string().optional(),
    }))
    .mutation(async ({ input }) => {
      // TODO: Replace with actual API call to backend
      console.log('Suggested startup:', input);
      return { success: true, id: 'new-startup-id' };
    }),
});