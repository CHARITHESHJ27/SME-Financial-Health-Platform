import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import api from '../config/api';

const COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

export default function Analytics() {
  const [companies, setCompanies] = useState([]);
  const [dashboards, setDashboards] = useState([]);

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem('finexri_companies') || '[]');
    setCompanies(stored);

    Promise.all(
      stored.map(c => api.get(`/companies/${c.id}/dashboard`).then(r => ({ ...r.data, company: c })).catch(() => null))
    ).then(results => setDashboards(results.filter(Boolean).filter(r => r.health_scores)));
  }, []);

  // Industry distribution
  const byIndustry = companies.reduce((acc, c) => {
    acc[c.industry] = (acc[c.industry] || 0) + 1;
    return acc;
  }, {});
  const industryData = Object.entries(byIndustry).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1), value,
  }));

  // Health score distribution
  const scoreData = dashboards.map(d => ({
    name: d.company?.name?.split(' ')[0] || `Co.${d.company?.id}`,
    score: Math.round(d.health_scores?.overall || 0),
    liquidity: Math.round(d.health_scores?.liquidity || 0),
    profitability: Math.round(d.health_scores?.profitability || 0),
  }));

  // Risk breakdown
  const riskCounts = dashboards.reduce((acc, d) => {
    const r = d.risk_assessment?.level || 'UNKNOWN';
    acc[r] = (acc[r] || 0) + 1;
    return acc;
  }, {});
  const riskData = Object.entries(riskCounts).map(([name, value]) => ({ name, value }));

  const RISK_COLORS = { MINIMAL: '#10B981', LOW: '#6366F1', MEDIUM: '#F59E0B', HIGH: '#EF4444', UNKNOWN: '#334155' };

  const avgScore = dashboards.length
    ? Math.round(dashboards.reduce((s, d) => s + (d.health_scores?.overall || 0), 0) / dashboards.length)
    : null;

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em', marginBottom: 4 }}>
          Portfolio Analytics
        </h1>
        <p style={{ fontSize: 13, color: '#475569' }}>Aggregate insights across your entire SME portfolio</p>
      </div>

      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16, marginBottom: 32 }}>
        {[
          { label: 'Portfolio Companies', value: companies.length },
          { label: 'Assessed Companies', value: dashboards.length },
          { label: 'Avg Health Score', value: avgScore != null ? `${avgScore}/100` : '—', color: avgScore >= 70 ? '#10B981' : avgScore >= 50 ? '#F59E0B' : '#EF4444' },
          { label: 'Industries Covered', value: Object.keys(byIndustry).length },
        ].map((k, i) => (
          <div key={i} style={{
            background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 14, padding: '22px 20px',
          }}>
            <div style={{ fontSize: 11, color: '#475569', fontWeight: 500, marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{k.label}</div>
            <div style={{ fontSize: 28, fontWeight: 800, color: k.color || '#F1F5F9', letterSpacing: '-0.02em' }}>{k.value}</div>
          </div>
        ))}
      </div>

      {companies.length === 0 ? (
        <div style={{
          background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: 14, padding: '80px 24px', textAlign: 'center',
        }}>
          <div style={{ fontSize: 40, marginBottom: 16 }}>📊</div>
          <div style={{ fontSize: 16, fontWeight: 600, color: '#475569' }}>No data yet</div>
          <div style={{ fontSize: 13, color: '#334155', marginTop: 8 }}>Add companies and upload financial data to see analytics</div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 20 }}>

          {/* Industry distribution */}
          <div style={{ background: '#131929', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 24 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#E2E8F0', marginBottom: 20 }}>Industry Distribution</div>
            {industryData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie data={industryData} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                    paddingAngle={3} dataKey="value">
                    {industryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1A2235', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, color: '#F1F5F9' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : <div style={{ color: '#334155', textAlign: 'center', padding: '40px 0' }}>No data</div>}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
              {industryData.map((d, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: COLORS[i % COLORS.length] }} />
                  <span style={{ fontSize: 12, color: '#64748B' }}>{d.name} ({d.value})</span>
                </div>
              ))}
            </div>
          </div>

          {/* Risk breakdown */}
          <div style={{ background: '#131929', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 24 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#E2E8F0', marginBottom: 20 }}>Risk Distribution</div>
            {riskData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie data={riskData} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                    paddingAngle={3} dataKey="value">
                    {riskData.map((d, i) => <Cell key={i} fill={RISK_COLORS[d.name] || '#334155'} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1A2235', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, color: '#F1F5F9' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : <div style={{ color: '#334155', textAlign: 'center', padding: '40px 0' }}>Upload financial data to see risk breakdown</div>}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
              {riskData.map((d, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: RISK_COLORS[d.name] || '#334155' }} />
                  <span style={{ fontSize: 12, color: '#64748B' }}>{d.name} ({d.value})</span>
                </div>
              ))}
            </div>
          </div>

          {/* Health scores bar */}
          {scoreData.length > 0 && (
            <div style={{ background: '#131929', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 24, gridColumn: '1 / -1' }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#E2E8F0', marginBottom: 20 }}>Health Score Comparison</div>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={scoreData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="name" tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ background: '#1A2235', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, color: '#F1F5F9' }} />
                  <Bar dataKey="score" fill="#6366F1" radius={[4, 4, 0, 0]} name="Overall" />
                  <Bar dataKey="liquidity" fill="#10B981" radius={[4, 4, 0, 0]} name="Liquidity" />
                  <Bar dataKey="profitability" fill="#F59E0B" radius={[4, 4, 0, 0]} name="Profitability" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
