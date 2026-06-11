import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const NAV = [
  { to: '/app', label: 'Overview', icon: '⬡', end: true },
  { to: '/app/companies', label: 'Companies', icon: '🏭' },
  { to: '/app/analytics', label: 'Analytics', icon: '📈' },
  { to: '/app/settings', label: 'Settings', icon: '⚙️' },
];

const PLAN_COLORS = { free: '#64748B', pro: '#6366F1', enterprise: '#10B981' };

export default function AppLayout() {
  const { user, org, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0A0F1E' }}>

      {/* Sidebar */}
      <aside style={{
        width: collapsed ? 64 : 240,
        minHeight: '100vh',
        background: '#0D1220',
        borderRight: '1px solid rgba(255,255,255,0.05)',
        display: 'flex', flexDirection: 'column',
        transition: 'width 0.25s cubic-bezier(0.4,0,0.2,1)',
        flexShrink: 0, position: 'fixed', top: 0, left: 0, bottom: 0, zIndex: 50,
        overflow: 'hidden',
      }}>

        {/* Logo */}
        <div style={{
          height: 60, display: 'flex', alignItems: 'center',
          padding: collapsed ? '0 16px' : '0 20px',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
          gap: 10, flexShrink: 0,
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8, flexShrink: 0,
            background: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 16, fontWeight: 800, color: 'white', cursor: 'pointer',
          }} onClick={() => setCollapsed(!collapsed)}>F</div>
          {!collapsed && (
            <span style={{ fontSize: 17, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em', whiteSpace: 'nowrap' }}>
              finexri
            </span>
          )}
        </div>

        {/* Org badge */}
        {!collapsed && org && (
          <div style={{
            margin: '12px 12px 4px',
            padding: '10px 12px',
            background: 'rgba(99,102,241,0.08)',
            border: '1px solid rgba(99,102,241,0.15)',
            borderRadius: 10,
          }}>
            <div style={{ fontSize: 11, color: '#475569', fontWeight: 500, marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Workspace
            </div>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#E2E8F0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {org.name}
            </div>
            <div style={{
              display: 'inline-block', marginTop: 4,
              padding: '1px 8px', borderRadius: 10,
              fontSize: 10, fontWeight: 700,
              background: 'rgba(99,102,241,0.15)',
              color: PLAN_COLORS[org.plan] || '#64748B',
              textTransform: 'uppercase', letterSpacing: '0.05em',
            }}>{org.plan}</div>
          </div>
        )}

        {/* Nav */}
        <nav style={{ flex: 1, padding: '8px 0', overflowY: 'auto' }}>
          {NAV.map(({ to, label, icon, end }) => (
            <NavLink key={to} to={to} end={end} style={({ isActive }) => ({
              display: 'flex', alignItems: 'center',
              gap: 12, padding: collapsed ? '10px 16px' : '10px 20px',
              margin: '2px 8px', borderRadius: 8,
              textDecoration: 'none', fontSize: 13, fontWeight: 500,
              color: isActive ? '#F1F5F9' : '#64748B',
              background: isActive ? 'rgba(99,102,241,0.15)' : 'transparent',
              borderLeft: isActive ? '2px solid #6366F1' : '2px solid transparent',
              transition: 'all 0.15s',
              whiteSpace: 'nowrap',
            })}>
              <span style={{ fontSize: 15, flexShrink: 0 }}>{icon}</span>
              {!collapsed && label}
            </NavLink>
          ))}
        </nav>

        {/* User */}
        <div style={{
          padding: collapsed ? '12px 12px' : '12px 16px',
          borderTop: '1px solid rgba(255,255,255,0.05)',
          display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
            background: 'linear-gradient(135deg, #6366F1, #06B6D4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 12, fontWeight: 700, color: 'white',
          }}>
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          {!collapsed && (
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: '#E2E8F0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.full_name}
              </div>
              <div style={{ fontSize: 11, color: '#334155', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.email}
              </div>
            </div>
          )}
          {!collapsed && (
            <button onClick={handleLogout} style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: '#475569', fontSize: 16, padding: '4px', borderRadius: 4,
              display: 'flex', alignItems: 'center',
            }} title="Sign out">⇥</button>
          )}
        </div>
      </aside>

      {/* Main */}
      <main style={{
        flex: 1, marginLeft: collapsed ? 64 : 240,
        transition: 'margin-left 0.25s cubic-bezier(0.4,0,0.2,1)',
        minHeight: '100vh', display: 'flex', flexDirection: 'column',
      }}>
        {/* Topbar */}
        <header style={{
          height: 60, display: 'flex', alignItems: 'center', justifyContent: 'flex-end',
          padding: '0 32px', borderBottom: '1px solid rgba(255,255,255,0.05)',
          background: 'rgba(10,15,30,0.95)', backdropFilter: 'blur(10px)',
          position: 'sticky', top: 0, zIndex: 40, flexShrink: 0,
          gap: 12,
        }}>
          <div style={{
            padding: '5px 14px',
            background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
            borderRadius: 20, fontSize: 12, color: '#818CF8', fontWeight: 600,
          }}>
            {org?.plan?.toUpperCase()} PLAN
          </div>
          <div style={{
            width: 32, height: 32, borderRadius: '50%',
            background: 'linear-gradient(135deg, #6366F1, #06B6D4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 12, fontWeight: 700, color: 'white', cursor: 'pointer',
          }}>
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
        </header>

        <div style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
