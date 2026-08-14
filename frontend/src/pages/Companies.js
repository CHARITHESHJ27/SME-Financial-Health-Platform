import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../config/api';

const RISK_COLOR = { MINIMAL: '#10B981', LOW: '#6366F1', MEDIUM: '#F59E0B', HIGH: '#EF4444' };
const SCORE_COLOR = (s) => s >= 75 ? '#10B981' : s >= 50 ? '#F59E0B' : '#EF4444';

function CompanyCard({ company, onSelect }) {
  const [dash, setDash] = useState(null);
  useEffect(() => {
    api.get(`/companies/${company.id}/dashboard`)
      .then(r => { if (r.data?.health_scores) setDash(r.data); })
      .catch(() => {});
  }, [company.id]);

  const score = dash?.health_scores?.overall;
  const risk = dash?.risk_assessment?.level;

  return (
    <div onClick={() => onSelect(company.id)} style={{
      background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 14, padding: 22, cursor: 'pointer',
      transition: 'all 0.2s',
    }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(99,102,241,0.35)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; e.currentTarget.style.transform = 'translateY(0)'; }}
    >
      {/* Icon + name */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{
          width: 44, height: 44, borderRadius: 12,
          background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2))',
          border: '1px solid rgba(99,102,241,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 18, fontWeight: 800, color: '#818CF8',
        }}>
          {company.name?.charAt(0).toUpperCase()}
        </div>
        {risk && (
          <span style={{
            padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600,
            background: `${RISK_COLOR[risk]}18`, color: RISK_COLOR[risk],
            border: `1px solid ${RISK_COLOR[risk]}40`,
          }}>{risk}</span>
        )}
      </div>

      <div style={{ fontSize: 15, fontWeight: 700, color: '#E2E8F0', marginBottom: 4 }}>{company.name}</div>
      <div style={{ fontSize: 12, color: '#475569', textTransform: 'capitalize', marginBottom: 20 }}>{company.industry}</div>

      {/* Score bar */}
      {score != null ? (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span style={{ fontSize: 11, color: '#475569', fontWeight: 500 }}>Health Score</span>
            <span style={{ fontSize: 12, fontWeight: 700, color: SCORE_COLOR(score) }}>{Math.round(score)}/100</span>
          </div>
          <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2 }}>
            <div style={{ height: '100%', width: `${score}%`, background: SCORE_COLOR(score), borderRadius: 2, transition: 'width 0.6s ease' }} />
          </div>
        </div>
      ) : (
        <div style={{
          padding: '8px 12px', borderRadius: 8,
          background: 'rgba(99,102,241,0.06)', border: '1px dashed rgba(99,102,241,0.2)',
          fontSize: 12, color: '#334155', textAlign: 'center',
        }}>
          No assessment yet — upload data to start
        </div>
      )}
    </div>
  );
}

export default function Companies() {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState([]);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: '', industry: 'services', gst_number: '' });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem('finexri_companies') || '[]');
    setCompanies(stored);
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const res = await api.post('/companies/', form);
      const updated = [...companies, res.data];
      setCompanies(updated);
      localStorage.setItem('finexri_companies', JSON.stringify(updated));
      setShowModal(false);
      setForm({ name: '', industry: 'services', gst_number: '' });
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create company');
    } finally {
      setCreating(false);
    }
  };

  const filtered = companies.filter(c => {
    const matchSearch = c.name?.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'all' || c.industry === filter;
    return matchSearch && matchFilter;
  });

  const industries = ['all', ...new Set(companies.map(c => c.industry).filter(Boolean))];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em', marginBottom: 4 }}>Companies</h1>
          <p style={{ fontSize: 13, color: '#475569' }}>{companies.length} {companies.length === 1 ? 'company' : 'companies'} in your workspace</p>
        </div>
        {companies.length > 0 && (
          <button className="btn-primary" onClick={() => setShowModal(true)}>+ Add Company</button>
        )}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
        <input className="finexri-input" placeholder="Search companies…" value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ maxWidth: 260 }} />
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {industries.map(ind => (
            <button key={ind} onClick={() => setFilter(ind)} style={{
              padding: '8px 16px', borderRadius: 8, fontSize: 12, fontWeight: 600,
              border: '1px solid',
              borderColor: filter === ind ? '#6366F1' : 'rgba(255,255,255,0.06)',
              background: filter === ind ? 'rgba(99,102,241,0.15)' : 'transparent',
              color: filter === ind ? '#818CF8' : '#475569',
              cursor: 'pointer', textTransform: 'capitalize',
            }}>{ind === 'all' ? 'All Industries' : ind}</button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '80px 24px' }}>
          <div style={{ fontSize: 40, marginBottom: 16 }}>🔍</div>
          <div style={{ fontSize: 16, fontWeight: 600, color: '#475569', marginBottom: 8 }}>
            {search ? 'No companies match your search' : 'No companies yet'}
          </div>
          {!search && (
            <button className="btn-primary" style={{ marginTop: 16 }} onClick={() => setShowModal(true)}>
              + Add First Company
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 18 }}>
          {filtered.map(c => (
            <CompanyCard key={c.id} company={c} onSelect={id => navigate(`/app/companies/${id}`)} />
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 200,
          background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
        }} onClick={e => { if (e.target === e.currentTarget) setShowModal(false); }}>
          <div style={{
            background: '#131929', border: '1px solid rgba(99,102,241,0.2)',
            borderRadius: 18, padding: 36, width: '100%', maxWidth: 460,
          }}>
            <h2 style={{ fontSize: 20, fontWeight: 800, color: '#F1F5F9', marginBottom: 24, letterSpacing: '-0.02em' }}>
              Add New Company
            </h2>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>Company Name</label>
                <input className="finexri-input" required placeholder="Tech Solutions Pvt Ltd"
                  value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
              </div>
              <div>
                <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>Industry</label>
                <select className="finexri-input" value={form.industry}
                  onChange={e => setForm({ ...form, industry: e.target.value })}>
                  {['manufacturing', 'retail', 'services', 'agriculture', 'logistics', 'e-commerce'].map(i => (
                    <option key={i} value={i} style={{ background: '#131929' }}>
                      {i.charAt(0).toUpperCase() + i.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>
                  GST Number <span style={{ color: '#334155' }}>(optional)</span>
                </label>
                <input className="finexri-input" placeholder="27AABCU9603R1ZX"
                  value={form.gst_number} onChange={e => setForm({ ...form, gst_number: e.target.value })} />
              </div>
              <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                <button type="button" className="btn-ghost" style={{ flex: 1 }} onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary" style={{ flex: 1 }} disabled={creating}>
                  {creating ? 'Creating…' : 'Create Company'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
