export const config = {
  apiUrl: import.meta.env.VITE_API_URL || '',
  apiKey: import.meta.env.VITE_API_KEY || '',
  appName: 'PAI Chatbot',
  version: '1.0.0',
  maxMessageLength: 4000,
  defaultUserId: 'default-user',
};

// Validate required environment variables
export function validateConfig(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!config.apiUrl) {
    errors.push('VITE_API_URL is not configured');
  }

  if (!config.apiKey) {
    errors.push('VITE_API_KEY is not configured');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
