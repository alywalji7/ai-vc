// Utility functions for portfolio API operations

/**
 * Upload a portfolio file to the backend
 * 
 * @param file - The file to upload
 * @param lpId - The LP ID to associate the file with
 * @returns An object containing the uploaded file ID
 */
export async function uploadPortfolioFile(file: File, lpId: string) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('lpId', lpId);
  
  const response = await fetch('/api/portfolio/upload', {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to upload file');
  }
  
  return response.json();
}

/**
 * Get all portfolio files for a specific LP
 * 
 * @param lpId - The LP ID to get files for
 * @returns An array of file objects
 */
export async function getPortfolioFiles(lpId: string) {
  const response = await fetch(`/api/portfolio/files/${lpId}`, {
    method: 'GET',
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch files');
  }
  
  return response.json();
}

/**
 * Get details for a specific portfolio file
 * 
 * @param fileId - The file ID to get details for
 * @returns A file details object
 */
export async function getPortfolioFileDetails(fileId: number) {
  const response = await fetch(`/api/portfolio/file/${fileId}`, {
    method: 'GET',
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch file details');
  }
  
  return response.json();
}

/**
 * Get portfolio summary for a specific LP
 * 
 * @param lpId - The LP ID to get summary for
 * @returns A portfolio summary object
 */
export async function getPortfolioSummary(lpId: string) {
  const response = await fetch(`/api/portfolio/summary/${lpId}`, {
    method: 'GET',
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch portfolio summary');
  }
  
  return response.json();
}

/**
 * Get portfolio holdings for a specific LP
 * 
 * @param lpId - The LP ID to get holdings for
 * @returns An array of holding objects
 */
export async function getPortfolioHoldings(lpId: string) {
  const response = await fetch(`/api/portfolio/holdings/${lpId}`, {
    method: 'GET',
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch portfolio holdings');
  }
  
  return response.json();
}

/**
 * Get portfolio funds for a specific LP
 * 
 * @param lpId - The LP ID to get funds for
 * @returns An array of fund objects
 */
export async function getPortfolioFunds(lpId: string) {
  const response = await fetch(`/api/portfolio/funds/${lpId}`, {
    method: 'GET',
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch portfolio funds');
  }
  
  return response.json();
}