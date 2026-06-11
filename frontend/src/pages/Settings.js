import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Settings() {
  const { user, org, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div style={{ maxWidth: 640 }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em', marginBottom: 4 }}>Settings</h1>
        <p style={{ fontSize: 13, color: '#475569' }}>Manage your account and workspace preferences</p>
      </div>

      {/* Profile */}
      <Section title="Your Profile">
        <Row label="Full Name" value={user?.full_name} />
        <Row label="Email" value={user?.email} />
        <Row label="Role" value={user?.role?.charAt(0).toUpperCase() + user?.role?.slice(1)} />
      </Section>

      {/* Workspace */}
      <Section title="Workspace">
        <Row label="Organization" value={org?.name} />
        <Row label="Slug / Handle" value={org?.slug} mono />
        <Row label="Plan" value={org?.plan?.toUpperCase()} badge />
      </Section>

      {/* Danger */}
      <Section title="Account">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 0' }}>
          <div>
            <div style={{ fontSize: 14, fontWeight: 500, color: '#E2E8F0' }}>Sign out</div>
            <div style={{ fontSize: 12, color: '#475569', marginTop: 2 }}>Sign out of your Finexri account</div>
          </div>
          <button className="btn-ghost" style={{ borderColor: 'rgba(239,68,68,0.3)', color: '#EF4444' }}
            onClick={() => { logout(); navigate('/login'); }}>
            Sign Out
          </button>
        </div>
      </Section>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div style={{
      background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 14, padding: '20px 24px', marginBottom: 20,
    }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function Row({ label, value, mono, badge }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.04)',
    }}>
      <span style={{ fontSize: 13, color: '#64748B' }}>{label}</span>
      {badge ? (
        <span style={{
          padding: '3px 12px', borderRadius: 20, fontSize: 11, fontWeight: 700,
          background: 'rgba(99,102,241,0.15)', color: '#818CF8',
          border: '1px solid rgba(99,102,241,0.3)',
        }}>{value}</span>
      ) : (
        <span style={{
          fontSize: 13, fontWeight: 500, color: '#E2E8F0',
          fontFamily: mono ? 'monospace' : 'inherit',
        }}>{value || '—'}</span>
      )}
    </div>
  );
}
