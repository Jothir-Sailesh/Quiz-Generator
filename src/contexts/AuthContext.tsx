// frontend/src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { authAPI } from '../services/api';

interface User {
  username: string;
  email: string;
  full_name?: string;
  id?: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (payload: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await authAPI.login({ username, password }) as { user: User; access_token: string };
      setUser(res.user);
      localStorage.setItem('token', res.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (payload: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }) => {
    setIsLoading(true);
    try {
      await authAPI.register(payload);
      // After registration, you can auto-login
      await login(payload.username, payload.password);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  // On mount, verify token
  useEffect(() => {
    const verify = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      try {
        const res = await authAPI.verifyToken() as { user: User };
        setUser(res.user);
      } catch {
        logout();
      }
    };
    verify();
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

// ✅ This is the key: export useAuth
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
