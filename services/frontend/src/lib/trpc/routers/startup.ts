import { z } from 'zod';
import { publicProcedure, router } from '../init';

// Define the schema for startup suggestion data
const suggestStartupSchema = z.object({
  name: z.string().min(1, "Name is required"),
  website: z.string().url("Please provide a valid URL"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  sector: z.string(),
  location: z.string(),
  foundedYear: z.number().min(2000).max(new Date().getFullYear()),
  contactEmail: z.string().email().optional(),
});

export const startupRouter = router({
  suggestStartup: publicProcedure
    .input(suggestStartupSchema)
    .mutation(async ({ input }) => {
      try {
        // In a real implementation, this would save to a database
        // or call an API endpoint to record the suggestion
        console.log('Received startup suggestion:', input);
        
        // Simulate some processing time
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
          success: true,
          message: "Thank you for your suggestion! We'll review it shortly."
        };
      } catch (error) {
        console.error('Error processing startup suggestion:', error);
        return {
          success: false,
          message: "There was an error processing your suggestion. Please try again."
        };
      }
    }),
});