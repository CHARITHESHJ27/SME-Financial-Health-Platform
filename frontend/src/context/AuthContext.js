import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../config/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [org, setOrg] = useState(null);
  const [loading, setLoading] = useState(true);

  const setAuth = (data) => {
    setUser(data.user);
    setOrg(data.organization);
    localStorage.setItem('finexri_token', data.access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
  };

  const logout = useCallback(() => {
    setUser(null);
    setOrg(null);
    localStorage.removeItem('finexri_token');
    delete api.defaults.headers.common['Authorization'];
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('finexri_token');
    if (!token) { setLoading(false); return; }
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    api.get('/auth/me')
      .then(res => { setUser(res.data.user); setOrg(res.data.organization); })
      .catch(() => logout())
      .finally(() => setLoading(false));
  }, [logout]);

  return (
    <AuthContext.Provider value={{ user, org, loading, setAuth, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
