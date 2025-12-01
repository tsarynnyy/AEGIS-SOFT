import Constants from 'expo-constants';

const API_BASE_URL = Constants.expoConfig?.extra?.backendUrl || process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  role: string;
  first_name?: string;
  last_name?: string;
}

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export const api = {
  // Auth endpoints
  login: async (credentials: LoginCredentials): Promise<ApiResponse<any>> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || 'Login failed' };
      }

      return { data };
    } catch (error) {
      return { error: 'Network error. Please check your connection.' };
    }
  },

  register: async (registerData: RegisterData): Promise<ApiResponse<any>> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
      });

      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || 'Registration failed' };
      }

      return { data };
    } catch (error) {
      return { error: 'Network error. Please check your connection.' };
    }
  },

  // Member endpoints
  getMemberProfile: async (token: string): Promise<ApiResponse<any>> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/members/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || 'Failed to fetch profile' };
      }

      return { data };
    } catch (error) {
      return { error: 'Network error. Please check your connection.' };
    }
  },

  // Risk/Alerts endpoints
  getCurrentRisk: async (token: string, memberId: string): Promise<ApiResponse<any>> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/members/${memberId}/current-risk`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.status === 404) {
        return { data: null }; // No risk detected
      }

      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || 'Failed to fetch risk status' };
      }

      return { data };
    } catch (error) {
      return { error: 'Network error. Please check your connection.' };
    }
  },

  getMetrics: async (token: string, memberId: string, days: number = 7): Promise<ApiResponse<any>> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/members/${memberId}/metrics?days=${days}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || 'Failed to fetch metrics' };
      }

      return { data };
    } catch (error) {
      return { error: 'Network error. Please check your connection.' };
    }
  },

  getDevices: async (token: string, memberId: string): Promise<ApiResponse<any>> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/members/${memberId}/devices`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || 'Failed to fetch devices' };
      }

      return { data };
    } catch (error) {
      return { error: 'Network error. Please check your connection.' };
    }
  },
};
