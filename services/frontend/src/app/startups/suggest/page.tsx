'use client';

import { useState } from 'react';
import { z } from 'zod';
import { api } from '@/lib/trpc/provider';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/toast';

// Define the schema for startup suggestion form
const suggestStartupSchema = z.object({
  name: z.string().min(1, "Name is required"),
  website: z.string().url("Please provide a valid URL"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  sector: z.string().min(1, "Sector is required"),
  location: z.string().min(1, "Location is required"),
  foundedYear: z.number().min(2000).max(new Date().getFullYear()),
  contactEmail: z.string().email().optional(),
});

type FormData = z.infer<typeof suggestStartupSchema>;

const sectors = [
  'Fintech',
  'Healthcare',
  'Edtech',
  'Enterprise SaaS',
  'AI/ML',
  'Blockchain',
  'Consumer Tech',
  'Marketplace',
  'Climate Tech',
  'Hardware',
  'Cybersecurity',
  'Other'
];

export default function SuggestStartupPage() {
  const { toast } = useToast();
  const [formData, setFormData] = useState<FormData>({
    name: '',
    website: '',
    description: '',
    sector: '',
    location: '',
    foundedYear: 2023,
    contactEmail: '',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  
  // Use the TRPC mutation
  const suggestStartup = api.startup.suggestStartup.useMutation({
    onSuccess: () => {
      toast({
        title: "Startup Suggested",
        description: "Thank you for your suggestion! We'll review it shortly.",
      });
      
      // Reset form
      setFormData({
        name: '',
        website: '',
        description: '',
        sector: '',
        location: '',
        foundedYear: 2023,
        contactEmail: '',
      });
      setErrors({});
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "There was an error submitting your suggestion.",
        variant: "destructive",
      });
    },
  });
  
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'foundedYear' ? Number(value) : value,
    }));
    
    // Clear error for this field when user types
    if (errors[name as keyof FormData]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };
  
  const handleSelectChange = (name: keyof FormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear error for this field when user selects
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // Validate form data
      suggestStartupSchema.parse(formData);
      
      // Submit the data
      suggestStartup.mutate(formData);
    } catch (error) {
      if (error instanceof z.ZodError) {
        // Convert Zod errors to a more usable format
        const newErrors: Partial<Record<keyof FormData, string>> = {};
        error.errors.forEach((err) => {
          if (err.path) {
            newErrors[err.path[0] as keyof FormData] = err.message;
          }
        });
        setErrors(newErrors);
      }
    }
  };
  
  return (
    <div className="container mx-auto py-10">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl">Suggest a Startup</CardTitle>
          <CardDescription>
            Know an interesting startup that should be on our radar? Let us know!
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="grid gap-6">
            <div className="grid gap-3">
              <Label htmlFor="name">Startup Name</Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Enter the startup name"
              />
              {errors.name && (
                <p className="text-red-500 text-sm">{errors.name}</p>
              )}
            </div>
            
            <div className="grid gap-3">
              <Label htmlFor="website">Website</Label>
              <Input
                id="website"
                name="website"
                value={formData.website}
                onChange={handleChange}
                placeholder="https://example.com"
              />
              {errors.website && (
                <p className="text-red-500 text-sm">{errors.website}</p>
              )}
            </div>
            
            <div className="grid gap-3">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="What does this startup do?"
                rows={4}
              />
              {errors.description && (
                <p className="text-red-500 text-sm">{errors.description}</p>
              )}
            </div>
            
            <div className="grid gap-3">
              <Label htmlFor="sector">Sector</Label>
              <Select
                value={formData.sector}
                onValueChange={(value) => handleSelectChange('sector', value)}
              >
                <SelectTrigger id="sector">
                  <SelectValue placeholder="Select a sector" />
                </SelectTrigger>
                <SelectContent>
                  {sectors.map((sector) => (
                    <SelectItem key={sector} value={sector}>
                      {sector}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.sector && (
                <p className="text-red-500 text-sm">{errors.sector}</p>
              )}
            </div>
            
            <div className="grid gap-3">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="City, Country"
              />
              {errors.location && (
                <p className="text-red-500 text-sm">{errors.location}</p>
              )}
            </div>
            
            <div className="grid gap-3">
              <Label htmlFor="foundedYear">Founded Year</Label>
              <Input
                id="foundedYear"
                name="foundedYear"
                type="number"
                min={2000}
                max={new Date().getFullYear()}
                value={formData.foundedYear}
                onChange={handleChange}
              />
              {errors.foundedYear && (
                <p className="text-red-500 text-sm">{errors.foundedYear}</p>
              )}
            </div>
            
            <div className="grid gap-3">
              <Label htmlFor="contactEmail">Contact Email (Optional)</Label>
              <Input
                id="contactEmail"
                name="contactEmail"
                value={formData.contactEmail}
                onChange={handleChange}
                placeholder="contact@example.com"
              />
              {errors.contactEmail && (
                <p className="text-red-500 text-sm">{errors.contactEmail}</p>
              )}
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button 
              variant="outline" 
              type="button"
              onClick={() => history.back()}
            >
              Cancel
            </Button>
            <Button 
              type="submit"
              disabled={suggestStartup.isLoading} 
              className="min-w-[120px]"
            >
              {suggestStartup.isLoading ? "Submitting..." : "Submit"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}