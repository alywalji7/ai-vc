/**
 * Utility functions for interacting with the Beta Feedback Service
 */

export interface FeedbackData {
  user_id: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  message: string;
}

export interface LPData {
  email: string;
  name?: string | null;
  organization?: string | null;
}

export interface FounderData {
  email: string;
  name?: string | null;
  company_name?: string | null;
  deck_url?: string | null;
}

const BETA_FEEDBACK_URL = process.env.BETA_FEEDBACK_URL || 'http://localhost:8200';

/**
 * Submit user feedback to the Beta Feedback Service
 */
export async function submitFeedback(data: FeedbackData): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${BETA_FEEDBACK_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error submitting feedback:', errorText);
      return { success: false, message: 'Failed to submit feedback' };
    }

    return { success: true, message: 'Feedback submitted successfully' };
  } catch (error: any) {
    console.error('Error in feedback submission:', error);
    return { success: false, message: error.message || 'An error occurred' };
  }
}

/**
 * Register a new LP user
 */
export async function registerLP(data: LPData): Promise<{ success: boolean; message: string; id?: number }> {
  try {
    const response = await fetch(`${BETA_FEEDBACK_URL}/lp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      console.error('Error registering LP:', result);
      return { success: false, message: result.message || 'Failed to register LP' };
    }

    return { 
      success: result.status === 'success', 
      message: result.message,
      id: result.id
    };
  } catch (error: any) {
    console.error('Error in LP registration:', error);
    return { success: false, message: error.message || 'An error occurred' };
  }
}

/**
 * Register a new founder
 */
export async function registerFounder(data: FounderData): Promise<{ success: boolean; message: string; id?: number }> {
  try {
    const response = await fetch(`${BETA_FEEDBACK_URL}/founder`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      console.error('Error registering founder:', result);
      return { success: false, message: result.message || 'Failed to register founder' };
    }

    return { 
      success: result.status === 'success', 
      message: result.message,
      id: result.id
    };
  } catch (error: any) {
    console.error('Error in founder registration:', error);
    return { success: false, message: error.message || 'An error occurred' };
  }
}