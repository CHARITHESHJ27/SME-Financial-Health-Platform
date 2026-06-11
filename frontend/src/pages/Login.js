import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../config/api';

export default function Login() {
  const navigate = useNavigate();
  const { setAuth } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/auth/login', form);
      setAuth(res.data);
      navigate('/app');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      background: '#0A0F1E',
    }}>
      {/* Left panel */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        justifyContent: 'center', alignItems: 'center', padding: '48px',
      }}>
        {/* Logo */}
        <div style={{ width: '100%', maxWidth: 400 }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 48, textDecoration: 'none' }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18, fontWeight: 800, color: 'white',
            }}>F</div>
            <span style={{ fontSize: 22, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>finexri</span>
          </Link>

          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#F1F5F9', marginBottom: 8, letterSpacing: '-0.02em' }}>
            Welcome back
          </h1>
          <p style={{ fontSize: 14, color: '#64748B', marginBottom: 36 }}>
            Sign in to your workspace
          </p>

          {error && (
            <div style={{
              padding: '12px 16px', borderRadius: 8, marginBottom: 20,
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              color: '#EF4444', fontSize: 13,
            }}>{error}</div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>
                Work email
              </label>
              <input
                className="finexri-input"
                type="email" required autoFocus
                placeholder="you@company.com"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
              />
            </div>
            <div>
              <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>
                Password
              </label>
              <input
                className="finexri-input"
                type="password" required
                placeholder="••••••••"
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
              />
            </div>

            <button className="btn-primary" type="submit" disabled={loading}
              style={{ marginTop: 8, padding: '13px', fontSize: 15, width: '100%' }}>
              {loading ? 'Signing in…' : 'Sign in →'}
            </button>
          </form>

          <p style={{ marginTop: 28, fontSize: 13, color: '#475569', textAlign: 'center' }}>
            Don't have a workspace?{' '}
            <Link to="/signup" style={{ color: '#818CF8', fontWeight: 600, textDecoration: 'none' }}>
              Create one free
            </Link>
          </p>
        </div>
      </div>

      {/* Right panel — decorative */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
        alignItems: 'center', padding: '48px',
        background: 'linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.05) 100%)',
        borderLeft: '1px solid rgba(99,102,241,0.1)',
      }}>
        <div style={{ maxWidth: 420, textAlign: 'center' }}>
          <div style={{ fontSize: 64, marginBottom: 24 }}>📊</div>
          <h2 style={{ fontSize: 26, fontWeight: 700, color: '#F1F5F9', marginBottom: 16, letterSpacing: '-0.02em' }}>
            Real-time financial intelligence
          </h2>
          <p style={{ fontSize: 15, color: '#475569', lineHeight: 1.7 }}>
            Analyze creditworthiness, benchmark against industry peers, and surface AI recommendations — all in seconds.
          </p>

          <div style={{ marginTop: 40, display: 'flex', flexDirection: 'column', gap: 12 }}>
            {[
              { icon: '✅', text: 'Credit scoring with 20+ financial ratios' },
              { icon: '✅', text: 'Industry benchmarking across 6 sectors' },
              { icon: '✅', text: 'AI-powered risk & optimization insights' },
              { icon: '✅', text: 'Team workspaces with role-based access' },
            ].map((item, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 12,
                background: 'rgba(19,25,41,0.6)', border: '1px solid rgba(99,102,241,0.12)',
                borderRadius: 10, padding: '12px 16px', textAlign: 'left',
              }}>
                <span style={{ fontSize: 14 }}>{item.icon}</span>
                <span style={{ fontSize: 13, color: '#94A3B8' }}>{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
