import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../config/api';

const SCORE_COLOR = (s) => s >= 75 ? '#10B981' : s >= 50 ? '#F59E0B' : '#EF4444';
const RISK_COLOR = { MINIMAL: '#10B981', LOW: '#6366F1', MEDIUM: '#F59E0B', HIGH: '#EF4444' };

function KPICard({ label, value, sub, color }) {
  return (
    <div style={{
      background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 14, padding: '22px 24px',
    }}>
      <div style={{ fontSize: 12, color: '#475569', fontWeight: 500, marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {label}
      </div>
      <div style={{ fontSize: 32, fontWeight: 800, color: color || '#F1F5F9', letterSpacing: '-0.02em', lineHeight: 1 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 12, color: '#334155', marginTop: 6 }}>{sub}</div>}
    </div>
  );
}

function CompanyRow({ company, onSelect }) {
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
      display: 'grid', gridTemplateColumns: '1fr 120px 110px 100px 120px',
      alignItems: 'center', padding: '14px 20px',
      borderBottom: '1px solid rgba(255,255,255,0.04)',
      cursor: 'pointer', transition: 'background 0.15s',
    }}
      onMouseEnter={e => e.currentTarget.style.background = 'rgba(99,102,241,0.05)'}
      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
    >
      <div>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#E2E8F0' }}>{company.name}</div>
        <div style={{ fontSize: 12, color: '#475569', marginTop: 2, textTransform: 'capitalize' }}>{company.industry}</div>
      </div>
      <div>
        {score != null ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 36, height: 36, borderRadius: '50%',
              border: `2px solid ${SCORE_COLOR(score)}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 11, fontWeight: 700, color: SCORE_COLOR(score),
            }}>{Math.round(score)}</div>
            <span style={{ fontSize: 12, color: '#475569' }}>/100</span>
          </div>
        ) : <span style={{ fontSize: 12, color: '#334155' }}>—</span>}
      </div>
      <div>
        {risk ? (
          <span style={{
            padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600,
            background: `${RISK_COLOR[risk]}18`, color: RISK_COLOR[risk],
            border: `1px solid ${RISK_COLOR[risk]}40`,
          }}>{risk}</span>
        ) : <span style={{ fontSize: 12, color: '#334155' }}>No data</span>}
      </div>
      <div style={{ fontSize: 12, color: '#475569', textTransform: 'capitalize' }}>
        {company.industry}
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button style={{
          padding: '6px 14px', borderRadius: 7, fontSize: 12, fontWeight: 600,
          background: 'rgba(99,102,241,0.12)', color: '#818CF8',
          border: '1px solid rgba(99,102,241,0.2)', cursor: 'pointer',
        }}>View →</button>
      </div>
    </div>
  );
}

export default function OrgOverview() {
  const { user, org } = useAuth();
  const navigate = useNavigate();
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: '', industry: 'services', gst_number: '' });
  const [creating, setCreating] = useState(false);

  const load = () => {
    setLoading(true);
    // Fetch all companies (we show them all for this org)
    // Since backend doesn't filter by org yet, we store locally too
    const stored = JSON.parse(localStorage.getItem('finexri_companies') || '[]');
    setCompanies(stored);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

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

  const healthScores = companies.length;
  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em', marginBottom: 4 }}>
            {greeting()}, {user?.full_name?.split(' ')[0]} 👋
          </h1>
          <p style={{ fontSize: 14, color: '#475569' }}>
            {org?.name} · {companies.length} {companies.length === 1 ? 'company' : 'companies'} in workspace
          </p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + Add Company
        </button>
      </div>

      {/* KPI row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 32 }}>
        <KPICard label="Total Companies" value={companies.length} sub="In your workspace" />
        <KPICard label="Workspace Plan" value={org?.plan?.toUpperCase() || '—'} sub="Current tier" color="#6366F1" />
        <KPICard label="Your Role" value={user?.role?.charAt(0).toUpperCase() + user?.role?.slice(1) || '—'} sub="Access level" color="#10B981" />
        <KPICard label="Assessments Ready" value={healthScores} sub="Companies tracked" color="#F59E0B" />
      </div>

      {/* Companies table */}
      <div style={{
        background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14, overflow: 'hidden',
      }}>
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '18px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)',
        }}>
          <span style={{ fontSize: 15, fontWeight: 700, color: '#E2E8F0' }}>Companies</span>
          <span style={{ fontSize: 12, color: '#334155' }}>{companies.length} total</span>
        </div>

        {/* Table header */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 120px 110px 100px 120px',
          padding: '10px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.04)',
        }}>
          {['Company', 'Health Score', 'Risk Level', 'Industry', ''].map((h, i) => (
            <div key={i} style={{ fontSize: 11, fontWeight: 600, color: '#334155', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              {h}
            </div>
          ))}
        </div>

        {loading ? (
          <div style={{ padding: '48px', textAlign: 'center', color: '#334155' }}>Loading…</div>
        ) : companies.length === 0 ? (
          <div style={{ padding: '64px 24px', textAlign: 'center' }}>
            <div style={{ fontSize: 40, marginBottom: 16 }}>🏭</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: '#475569', marginBottom: 8 }}>No companies yet</div>
            <div style={{ fontSize: 13, color: '#334155', marginBottom: 24 }}>Add your first company to start analyzing financial health</div>
            <button className="btn-primary" onClick={() => setShowModal(true)}>
              + Add First Company
            </button>
          </div>
        ) : (
          companies.map(c => (
            <CompanyRow key={c.id} company={c} onSelect={id => navigate(`/app/companies/${id}`)} />
          ))
        )}
      </div>

      {/* Create company modal */}
      {showModal && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 200,
          background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
        }} onClick={e => { if (e.target === e.currentTarget) setShowModal(false); }}>
          <div style={{
            background: '#131929', border: '1px solid rgba(99,102,241,0.2)',
            borderRadius: 18, padding: 36, width: '100%', maxWidth: 460,
          }}>
            <h2 style={{ fontSize: 20, fontWeight: 800, color: '#F1F5F9', marginBottom: 6, letterSpacing: '-0.02em' }}>
              Add New Company
            </h2>
            <p style={{ fontSize: 13, color: '#475569', marginBottom: 28 }}>
              Register a company to begin financial assessment
            </p>

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
                <label style={{ fontSize: 13, fontWeight: 500, color: '#94A3B8', display: 'block', marginBottom: 6 }}>GST Number <span style={{ color: '#334155' }}>(optional)</span></label>
                <input className="finexri-input" placeholder="27AABCU9603R1ZX"
                  value={form.gst_number} onChange={e => setForm({ ...form, gst_number: e.target.value })} />
              </div>
              <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                <button type="button" className="btn-ghost" style={{ flex: 1 }} onClick={() => setShowModal(false)}>
                  Cancel
                </button>
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
