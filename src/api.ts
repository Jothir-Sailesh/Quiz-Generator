// frontend/src/services/api.ts

const BASE_URL = "http://localhost:8000/api"; // FastAPI backend

interface LoginPayload {
  username: string;
  password: string;
}

interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export const authAPI = {
  login: async (payload: LoginPayload) => {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Login failed");
    }

    return res.json(); // { access_token: string, token_type: 'bearer', user: {...} }
  },

  register: async (payload: RegisterPayload) => {
    const res = await fetch(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Registration failed");
    }

    return res.json(); // { user: {...} }
  },

  verifyToken: async () => {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("No token found");

    const res = await fetch(`${BASE_URL}/auth/verify-token`, {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error("Token verification failed");
    }

    return res.json(); // { valid: true, user: string, message: string }
  },
};
