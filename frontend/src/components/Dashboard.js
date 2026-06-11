import React, { useState, useEffect, useCallback } from 'react';
import { Spin, Upload, message } from 'antd';
import { UploadOutlined, RiseOutlined, WarningOutlined, DashboardOutlined } from '@ant-design/icons';
import api from '../config/api';
import FinancialCharts from '../charts/FinancialCharts';
import Recommendations from './Recommendations';

const SCORE_COLOR = (s) => s >= 80 ? '#10B981' : s >= 60 ? '#F59E0B' : s >= 40 ? '#F97316' : '#EF4444';
const RISK_COLOR  = { MINIMAL: '#10B981', LOW: '#6366F1', MEDIUM: '#F59E0B', HIGH: '#EF4444' };

function ScoreCard({ title, value, sub }) {
  const color = SCORE_COLOR(value);
  return (
    <div style={{
      background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 14, padding: '20px 22px',
    }}>
      <div style={{ fontSize: 11, color: '#475569', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 10 }}>
        {title}
      </div>
      <div style={{ fontSize: 34, fontWeight: 800, color, letterSpacing: '-0.02em', lineHeight: 1 }}>
        {Math.round(value)}
        <span style={{ fontSize: 16, fontWeight: 500, color: '#475569' }}>/100</span>
      </div>
      {/* Progress bar */}
      <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, marginTop: 12 }}>
        <div style={{ height: '100%', width: `${value}%`, background: color, borderRadius: 2, transition: 'width 0.8s ease' }} />
      </div>
      {sub && <div style={{ fontSize: 11, color: '#475569', marginTop: 8, lineHeight: 1.4 }}>{sub}</div>}
    </div>
  );
}

const Dashboard = ({ companyId }) => {
  const [loading, setLoading]       = useState(true);
  const [dashboardData, setData]    = useState(null);
  const [uploading, setUploading]   = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get(`/companies/${companyId}/dashboard`);
      setData(res.data);
    } catch {
      message.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => { if (companyId) fetchDashboardData(); }, [companyId, fetchDashboardData]);

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      setUploading(true);
      await api.post(`/upload-financial-data/${companyId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      message.success('Financial data uploaded & assessment completed');
      fetchDashboardData();
    } catch {
      message.error('Failed to upload financial data');
    } finally {
      setUploading(false);
    }
    return false;
  };

  const getIndustryBenchmark = (industry, score) => {
    const avgs = { retail: 65, services: 70, manufacturing: 60, logistics: 55, agriculture: 50, 'e-commerce': 75 };
    const avg = avgs[industry] || 70;
    const diff = Math.abs(score - avg).toFixed(0);
    const dir  = score > avg ? 'above' : 'below';
    return `${diff}pts ${dir} ${industry} average`;
  };

  // ── Loading ──────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 80, gap: 16 }}>
        <Spin size="large" />
        <span style={{ color: '#475569', fontSize: 13 }}>Loading financial dashboard…</span>
      </div>
    );
  }

  // ── Empty state ──────────────────────────────────────────────────────────────
  if (!dashboardData || dashboardData.message === 'No assessments found' || dashboardData.status === 'error') {
    return (
      <div style={{
        background: '#131929', border: '1px dashed rgba(99,102,241,0.3)',
        borderRadius: 16, padding: '60px 24px', textAlign: 'center',
      }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📂</div>
        <div style={{ fontSize: 18, fontWeight: 700, color: '#E2E8F0', marginBottom: 8 }}>No Assessment Data</div>
        <div style={{ fontSize: 13, color: '#475569', marginBottom: 28 }}>
          Upload a CSV or Excel file with your financial data to generate a full health assessment
        </div>
        <Upload beforeUpload={handleFileUpload} accept=".csv,.xlsx,.xls" showUploadList={false}>
          <button className="btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
            <UploadOutlined /> {uploading ? 'Uploading…' : 'Upload Financial Data'}
          </button>
        </Upload>
      </div>
    );
  }

  const { company_info, health_scores, risk_assessment, recommendations, cost_optimization, last_updated } = dashboardData;
  const riskColor = RISK_COLOR[risk_assessment.level] || '#64748B';

  const creditStatus = () => {
    const s = health_scores.overall;
    if (s >= 80) return { label: 'Excellent Credit', color: '#10B981' };
    if (s >= 70) return { label: 'Good Credit',      color: '#6366F1' };
    if (s >= 50) return { label: 'Moderate Credit',  color: '#F59E0B' };
    return       { label: 'Weak Credit',             color: '#EF4444' };
  };
  const credit = creditStatus();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* ── Header card ── */}
      <div style={{
        background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14, padding: '20px 24px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16,
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
            <DashboardOutlined style={{ color: '#6366F1', fontSize: 18 }} />
            <span style={{ fontSize: 20, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>
              {company_info.name}
            </span>
          </div>
          <div style={{ fontSize: 12, color: '#475569', marginBottom: 10, textTransform: 'capitalize' }}>
            {company_info.industry} · Last updated {new Date(last_updated).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
          </div>
          <span style={{
            padding: '4px 14px', borderRadius: 20, fontSize: 12, fontWeight: 700,
            background: `${credit.color}18`, color: credit.color, border: `1px solid ${credit.color}40`,
          }}>
            {credit.label}
          </span>
        </div>

        <Upload beforeUpload={handleFileUpload} accept=".csv,.xlsx,.xls" showUploadList={false}>
          <button className="btn-ghost" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
            <UploadOutlined /> {uploading ? 'Uploading…' : 'Upload New Data'}
          </button>
        </Upload>
      </div>

      {/* ── Score cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
        <ScoreCard title="Overall Health" value={health_scores.overall} />
        <ScoreCard title="Liquidity" value={health_scores.liquidity} />
        <ScoreCard
          title="Profitability"
          value={health_scores.profitability}
          sub={getIndustryBenchmark(company_info.industry, health_scores.profitability)}
        />
        <ScoreCard title="Leverage" value={health_scores.leverage} />
      </div>

      {/* ── Score explanation ── */}
      <div style={{
        background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.15)',
        borderRadius: 12, padding: '14px 18px',
        fontSize: 13, color: '#94A3B8', lineHeight: 1.7,
      }}>
        <span style={{ color: '#818CF8', fontWeight: 600 }}>How is this scored? </span>
        Based on <span style={{ color: '#E2E8F0', fontWeight: 600 }}>liquidity</span> ({Math.round(health_scores.liquidity)}/100),{' '}
        <span style={{ color: '#E2E8F0', fontWeight: 600 }}>profitability</span> ({Math.round(health_scores.profitability)}/100),{' '}
        <span style={{ color: '#E2E8F0', fontWeight: 600 }}>leverage</span> ({Math.round(health_scores.leverage)}/100) and cash flow stability.
        Higher scores indicate stronger creditworthiness.
      </div>

      {/* ── Risk + Charts ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 20 }}>

        {/* Risk panel */}
        <div style={{
          background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: 14, padding: 22,
        }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#E2E8F0', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <WarningOutlined style={{ color: riskColor }} /> Risk Assessment
          </div>

          <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <div style={{
              display: 'inline-block', padding: '8px 20px', borderRadius: 20,
              background: `${riskColor}18`, color: riskColor,
              border: `1px solid ${riskColor}40`,
              fontSize: 14, fontWeight: 800, letterSpacing: '0.05em',
            }}>
              {risk_assessment.level} RISK
            </div>
          </div>

          {risk_assessment.risks && risk_assessment.risks.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ fontSize: 11, color: '#475569', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>
                Identified Risks
              </div>
              {risk_assessment.risks.map((risk, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 10, padding: '10px 12px',
                  background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.15)',
                  borderRadius: 8,
                }}>
                  <span style={{ color: '#EF4444', fontSize: 12, flexShrink: 0, marginTop: 1 }}>⚠</span>
                  <span style={{ fontSize: 12, color: '#CBD5E1', lineHeight: 1.5 }}>{risk}</span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px',
              background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)',
              borderRadius: 8, fontSize: 13, color: '#10B981',
            }}>
              ✓ No significant risks identified
            </div>
          )}
        </div>

        {/* Charts */}
        <FinancialCharts companyId={companyId} />
      </div>

      {/* ── Recommendations + Cost Optimization ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <Recommendations
          recommendations={recommendations}
          title="AI Recommendations"
          icon={<RiseOutlined style={{ color: '#6366F1' }} />}
        />
        <Recommendations
          recommendations={cost_optimization}
          title="Cost Optimization"
          icon={<span style={{ fontSize: 14 }}>💡</span>}
          type="cost"
        />
      </div>

    </div>
  );
};

export default Dashboard;
