import { z } from 'zod';
import { router, procedure } from '../init';
import { StartupInfo } from '@/app/startups/components/StartupCard';

// Define the FilterValues interface to align with the one from FilterDrawer
interface FilterValues {
  minScore: number;
  sectors: string[];
  geography?: 'USA' | 'Europe' | 'Asia' | 'LatAm' | 'Global';
  fundingStage?: string;
  hasRevenue?: boolean;
}

// Mock data for startups
const MOCK_STARTUPS: StartupInfo[] = [
  {
    id: 'acme-inc',
    name: 'Acme Inc.',
    logoUrl: '/logos/acme.svg',
    description: 'Building the future of rocket-powered transportation for coyotes.',
    sector: 'Hardware',
    location: 'USA',
    radarScore: 0.87,
    foundedDate: new Date('2022-01-15'),
    latestFunding: {
      amount: 4500000,
      round: 'Seed',
      date: new Date('2023-05-20'),
    },
  },
  {
    id: 'globex-corp',
    name: 'Globex Corporation',
    logoUrl: '/logos/globex.svg',
    description: 'Revolutionary AI solutions for enterprise knowledge management.',
    sector: 'AI',
    location: 'Europe',
    radarScore: 0.92,
    foundedDate: new Date('2021-08-03'),
    latestFunding: {
      amount: 12000000,
      round: 'Series A',
      date: new Date('2023-11-10'),
    },
  },
  {
    id: 'cyberdyne-systems',
    name: 'Cyberdyne Systems',
    logoUrl: '/logos/cyberdyne.svg',
    description: 'Advanced robotics and neural network learning systems for defense applications.',
    sector: 'AI',
    location: 'USA',
    radarScore: 0.76,
    foundedDate: new Date('2019-04-19'),
    latestFunding: {
      amount: 32000000,
      round: 'Series B',
      date: new Date('2022-12-05'),
    },
  },
  {
    id: 'stark-industries',
    name: 'Stark Industries',
    logoUrl: '/logos/stark.svg',
    description: 'Clean energy solutions and advanced materials for a sustainable future.',
    sector: 'CleanTech',
    location: 'USA',
    radarScore: 0.95,
    foundedDate: new Date('2018-11-30'),
    latestFunding: {
      amount: 75000000,
      round: 'Series C',
      date: new Date('2023-02-15'),
    },
  },
  {
    id: 'initech',
    name: 'Initech',
    logoUrl: '/logos/initech.svg',
    description: 'Enterprise resource planning software that simplifies finance operations.',
    sector: 'SaaS',
    location: 'Europe',
    radarScore: 0.58,
    foundedDate: new Date('2020-07-12'),
    latestFunding: {
      amount: 2300000,
      round: 'Pre-seed',
      date: new Date('2021-09-08'),
    },
  },
  {
    id: 'oceanic-airlines',
    name: 'Oceanic Airlines',
    logoUrl: '/logos/oceanic.svg',
    description: 'Revolutionizing air travel with sustainable aviation and passenger experience.',
    sector: 'CleanTech',
    location: 'Asia',
    radarScore: 0.67,
    foundedDate: new Date('2019-03-22'),
    latestFunding: {
      amount: 18500000,
      round: 'Series A',
      date: new Date('2022-05-30'),
    },
  },
];

export const startupRouter = router({
  // Get startups with optional filters
  getStartups: procedure
    .input(
      z.object({
        minScore: z.number().min(0).max(1).optional().default(0),
        sectors: z.array(z.string()).optional(),
        geography: z.enum(['USA', 'Europe', 'Asia', 'LatAm', 'Global']).optional(),
        hasRevenue: z.boolean().optional(),
      })
    )
    .query(({ input }) => {
      let filteredStartups = [...MOCK_STARTUPS];

      // Apply filters
      if (input.minScore) {
        filteredStartups = filteredStartups.filter(
          (startup) => startup.radarScore >= input.minScore
        );
      }

      if (input.sectors && input.sectors.length > 0) {
        filteredStartups = filteredStartups.filter((startup) =>
          input.sectors?.includes(startup.sector)
        );
      }

      if (input.geography && input.geography !== 'Global') {
        filteredStartups = filteredStartups.filter(
          (startup) => startup.location === input.geography
        );
      }

      if (input.hasRevenue) {
        filteredStartups = filteredStartups.filter(
          (startup) => startup.latestFunding && startup.latestFunding.amount > 0
        );
      }

      return filteredStartups;
    }),

  // Get sector statistics
  getSectorStats: procedure.query(() => {
    const sectors = MOCK_STARTUPS.reduce((acc, startup) => {
      acc[startup.sector] = (acc[startup.sector] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(sectors).map(([name, count]) => ({
      name,
      count,
    }));
  }),

  // Suggest a new startup
  suggestStartup: procedure
    .input(
      z.object({
        name: z.string().min(1),
        website: z.string().url(),
        description: z.string().min(10),
        sector: z.string(),
        location: z.string(),
        contactEmail: z.string().email().optional(),
        foundedYear: z.number().int().min(2000).max(new Date().getFullYear()),
      })
    )
    .mutation(async ({ input }) => {
      // This would typically send data to a backend service or database
      // For now, we'll just return a success message
      return {
        success: true,
        message: `Thanks for suggesting ${input.name}! We'll review it shortly.`,
      };
    }),
});