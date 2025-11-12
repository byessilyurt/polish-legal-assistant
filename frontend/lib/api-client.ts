import axios, { AxiosError } from 'axios';
import { ChatRequest, ChatResponse } from '@/types/legal-types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for AI responses
  headers: {
    'Content-Type': 'application/json',
  },
});

export class APIError extends Error {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
  }
}

export const chatAPI = {
  /**
   * Send a chat message to the backend
   */
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    try {
      const response = await apiClient.post<ChatResponse>('/api/v1/chat', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ detail?: string }>;

        if (axiosError.response) {
          // Server responded with error
          const message = axiosError.response.data?.detail || 'Server error occurred';
          throw new APIError(message, axiosError.response.status);
        } else if (axiosError.request) {
          // Request made but no response
          throw new APIError('No response from server. Please check your connection.');
        }
      }

      // Unknown error
      throw new APIError('An unexpected error occurred. Please try again.');
    }
  },

  /**
   * Health check endpoint
   */
  healthCheck: async (): Promise<boolean> => {
    try {
      await apiClient.get('/health');
      return true;
    } catch {
      return false;
    }
  },
};

export default apiClient;
