import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../config/api';

export default function Signup() {
  const navigate = useNavigate();
  const { setAuth } = useAuth();
  const [form, setForm] = useState({ full_name: '', email: '', password: '', org_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 2-step signup

  const handleNext = (e) => {
    e.preventDefault();
    if (!form.full_name || !form.email || !form.password) return;
    if (form.password.length < 8) { setError('Password must be at least 8 characters'); return; }
    setError('');
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.org_name) return;
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/auth/register', form);
      setAuth(res.data);
      navigate('/app');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: '#0A0F1E' }}>
      {/* Left panel */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        justifyContent: 'center', alignItems: 'center', padding: '48px',
      }}>
        <div style={{ width: '100%', maxWidth: 420 }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 48, textDecoration: 'none' }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18, fontWeight: 800, color: 'white',
            }}>F</div>
            <span style={{ fontSize: 22, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>finexri</span>
          </Link>

          {/* Step indicator */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 36 }}>
            {[1, 2].map(s => (
              <div key={s} style={{
                height: 3, flex: 1, borderRadius: 2,
                background: s <= step ? '#6366F1' : 'rgba(99,102,241,0.2)',
                transition: 'background 0.3s',
              }} />
            ))}
          </div>

          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#F1F5F9', marginBottom: 8, letterSpacing: '-0.02em' }}>
            {step === 1 ? 'Create your account' : 'Name your workspace'}
          </h1>
          <p style={{ fontSize: 14, color: '#64748B', marginBottom: 32 }}>
            {step === 1 ? 'Start with your personal details' : 'Your team will collaborate here'}
          </p>

          {error && (
            <div style={{
              padding: '12px 16px', borderRadius: 8, marginBottom: 20,
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              color: '#EF4444', fontSize: 13,
            }}>{error}</div>
          )}

          {step === 1 ? (
            <form onSubmit={handleNext} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>
                  Full name
                </label>
                <input className="finexri-input" type="text" required autoFocus
                  placeholder="Alex Johnson"
                  value={form.full_name}
                  onChange={e => setForm({ ...form, full_name: e.target.value })} />
              </div>
              <div>
                <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>
                  Work email
                </label>
                <input className="finexri-input" type="email" required
                  placeholder="alex@company.com"
                  value={form.email}
                  onChange={e => setForm({ ...form, email: e.target.value })} />
              </div>
              <div>
                <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>
                  Password
                </label>
                <input className="finexri-input" type="password" required
                  placeholder="Min. 8 characters"
                  value={form.password}
                  onChange={e => setForm({ ...form, password: e.target.value })} />
              </div>
              <button className="btn-primary" type="submit" style={{ marginTop: 8, padding: '13px', fontSize: 15 }}>
                Continue →
              </button>
            </form>
          ) : (
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>
                  Organization / Workspace name
                </label>
                <input className="finexri-input" type="text" required autoFocus
                  placeholder="Acme Capital Partners"
                  value={form.org_name}
                  onChange={e => setForm({ ...form, org_name: e.target.value })} />
                <p style={{ fontSize: 12, color: '#334155', marginTop: 6 }}>
                  This is your team's shared workspace. You can change it later.
                </p>
              </div>

              <button className="btn-primary" type="submit" disabled={loading}
                style={{ marginTop: 8, padding: '13px', fontSize: 15 }}>
                {loading ? 'Creating workspace…' : 'Create Workspace →'}
              </button>
              <button type="button" className="btn-ghost"
                onClick={() => { setStep(1); setError(''); }}
                style={{ padding: '11px', fontSize: 14 }}>
                ← Back
              </button>
            </form>
          )}

          <p style={{ marginTop: 28, fontSize: 13, color: '#475569', textAlign: 'center' }}>
            Already have a workspace?{' '}
            <Link to="/login" style={{ color: '#818CF8', fontWeight: 600, textDecoration: 'none' }}>
              Sign in
            </Link>
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
        alignItems: 'center', padding: '48px',
        background: 'linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.05) 100%)',
        borderLeft: '1px solid rgba(99,102,241,0.1)',
      }}>
        <div style={{ maxWidth: 400 }}>
          <div style={{ fontSize: 48, marginBottom: 24, textAlign: 'center' }}>🏢</div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#F1F5F9', marginBottom: 12, letterSpacing: '-0.02em', textAlign: 'center' }}>
            One workspace, your entire SME portfolio
          </h2>

          <div style={{ marginTop: 32, display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              { icon: '👥', title: 'Team collaboration', desc: 'Invite analysts and managers with role-based access' },
              { icon: '🏭', title: 'Multi-company management', desc: 'Track all your SME clients from a single dashboard' },
              { icon: '🔐', title: 'Enterprise security', desc: 'JWT auth, encrypted data, SOC2-ready architecture' },
            ].map((item, i) => (
              <div key={i} style={{
                display: 'flex', gap: 14,
                background: 'rgba(19,25,41,0.6)', border: '1px solid rgba(99,102,241,0.12)',
                borderRadius: 12, padding: '16px',
              }}>
                <div style={{ fontSize: 24, flexShrink: 0 }}>{item.icon}</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#E2E8F0', marginBottom: 4 }}>{item.title}</div>
                  <div style={{ fontSize: 12, color: '#475569', lineHeight: 1.5 }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
