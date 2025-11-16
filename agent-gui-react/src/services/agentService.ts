import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

const handleApiError = (error: unknown): never => {
    // Check if it's an axios error
    if (axios.isAxiosError && axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ error?: string; message?: string }>;
        
        // Network errors (server not running, CORS, etc.)
        if (!axiosError.response) {
            if (axiosError.code === 'ECONNREFUSED' || axiosError.message.includes('Network Error')) {
                throw new Error(`Network Error: Cannot connect to server at ${API_BASE_URL}. Make sure the backend server is running.`);
            }
            throw new Error(`Network Error: ${axiosError.message}`);
        }
        
        // Server responded with error status
        const message = axiosError.response?.data?.error || 
                       axiosError.response?.data?.message || 
                       axiosError.message || 
                       `Server error (${axiosError.response.status}): ${axiosError.response.statusText}`;
        throw new Error(message);
    }
    if (error instanceof Error) {
        throw error;
    }
    throw new Error('An unknown error occurred');
};

export const planVacation = async (task: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/plan`, { task });
        return response.data;
    } catch (error) {
        handleApiError(error);
    }
};

export const researchPlan = async (plan: string, threadId?: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/research`, { plan, thread_id: threadId });
        return response.data;
    } catch (error) {
        handleApiError(error);
    }
};

export const generateDraft = async (task: string, plan: string, threadId?: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/generate`, { task, plan, thread_id: threadId });
        return response.data;
    } catch (error) {
        handleApiError(error);
    }
};

export const critiqueDraft = async (draft: string, threadId?: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/critique`, { draft, thread_id: threadId });
        return response.data;
    } catch (error) {
        handleApiError(error);
    }
};

// add this wrapper so ResearchPanel can import fetchResearchData
export const fetchResearchData = async (plan: string, threadId?: string) => {
    // maps to the backend research endpoint
    return researchPlan(plan, threadId);
};