import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api, { getErrorMessage } from '@/lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem('efuel_user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('efuel_token');
    if (!token) {
      setLoading(false);
      return;
    }
    api.get('/auth/me')
      .then((res) => {
        setUser(res.data);
        localStorage.setItem('efuel_user', JSON.stringify(res.data));
      })
      .catch(() => {
        localStorage.removeItem('efuel_token');
        localStorage.removeItem('efuel_user');
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      const res = await api.post('/auth/login', { email, password });
      localStorage.setItem('efuel_token', res.data.access_token);
      localStorage.setItem('efuel_user', JSON.stringify(res.data.user));
      setUser(res.data.user);
      return { success: true };
    } catch (error) {
      return { success: false, message: getErrorMessage(error, 'Invalid email or password') };
    }
  }, []);

  const register = useCallback(async (name, email, password, role) => {
    try {
      const res = await api.post('/auth/register', { name, email, password, role });
      localStorage.setItem('efuel_token', res.data.access_token);
      localStorage.setItem('efuel_user', JSON.stringify(res.data.user));
      setUser(res.data.user);
      return { success: true };
    } catch (error) {
      return { success: false, message: getErrorMessage(error, 'Registration failed') };
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('efuel_token');
    localStorage.removeItem('efuel_user');
    setUser(null);
    window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
