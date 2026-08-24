import type {
  RecommendationRequest,
  RecommendationResponse,
  ExplainRequest,
  ExplainResponse,
  AskRequest,
  AskResponse,
  HealthCheckResponse,
} from './types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.message) {
        errorMessage = errorData.message;
      } else if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ');
        }
      } else if (errorData.details && Array.isArray(errorData.details)) {
        errorMessage = errorData.details.join(', ');
      }
    } catch {
      // Keep default statusText error message
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export const api = {
  /**
   * Health check for API server & PostgreSQL connection
   */
  async checkHealth(): Promise<HealthCheckResponse> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      return await handleResponse<HealthCheckResponse>(res);
    } catch (err: any) {
      throw new Error(err.message || 'Unable to connect to Kisima AI backend service.');
    }
  },

  /**
   * Primary Pump Sizing & Recommendation API
   */
  async getRecommendation(data: RecommendationRequest): Promise<RecommendationResponse> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/recommendations/pump`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(data),
      });
      return await handleResponse<RecommendationResponse>(res);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        throw new Error('Recommendation request timed out.');
      }
      throw err;
    }
  },

  /**
   * AI Technical Explanation via RAG
   */
  async getAIExplanation(data: ExplainRequest): Promise<ExplainResponse> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/ai/explain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(data),
      });
      return await handleResponse<ExplainResponse>(res);
    } catch (err: any) {
      throw new Error(err.message || 'Failed to generate AI technical explanation.');
    }
  },

  /**
   * AI Datasheet Q&A Search
   */
  async askAIQuestion(data: AskRequest): Promise<AskResponse> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/ai/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(data),
      });
      return await handleResponse<AskResponse>(res);
    } catch (err: any) {
      throw new Error(err.message || 'Failed to answer technical question.');
    }
  },
};
