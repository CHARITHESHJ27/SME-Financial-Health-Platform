import React, { useState, useEffect, useCallback } from 'react';
import { Spin, Upload, message } from 'antd';
import {
  UploadOutlined,
  DashboardOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import api from '../config/api';
import FinancialCharts from '../charts/FinancialCharts';
import Recommendations from './Recommendations';

const SCORE_COLOR = (s) => (s >= 75 ? '#10B981' : s >= 50 ? '#F59E0B' : s >= 30 ? '#F97316' : '#EF4444');
const RISK_COLOR = { MINIMAL: '#10B981', LOW: '#3B82F6', MEDIUM: '#F59E0B', HIGH: '#EF4444' };

function ScoreCard({ title, value, benchmark, sub, format = 'score' }) {
  const color = SCORE_COLOR(value);
  return (
    <div
      style={{
        background: '#131929',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14,
        padding: '18px 20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}
    >
      <div>
        <div
          style={{
            fontSize: 11,
            color: '#64748B',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.07em',
            marginBottom: 8,
          }}
        >
          {title}
        </div>
        <div style={{ fontSize: 30, fontWeight: 800, color, letterSpacing: '-0.02em', lineHeight: 1 }}>
          {Math.round(value)}
          <span style={{ fontSize: 14, fontWeight: 500, color: '#475569' }}>/100</span>
        </div>
      </div>
      <div style={{ marginTop: 12 }}>
        <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2 }}>
          <div
            style={{
              height: '100%',
              width: `${Math.min(100, Math.max(0, value))}%`,
              background: color,
              borderRadius: 2,
              transition: 'width 0.8s ease',
            }}
          />
        </div>
        {sub && <div style={{ fontSize: 11, color: '#64748B', marginTop: 8, lineHeight: 1.4 }}>{sub}</div>}
      </div>
    </div>
  );
}

function ShapRiskDriversPanel({ explanations, riskCategory }) {
  if (!explanations || explanations.length === 0) return null;

  return (
    <div
      style={{
        background: '#131929',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14,
        padding: 22,
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700, color: '#F1F5F9', display: 'flex', alignItems: 'center', gap: 8 }}>
          <ThunderboltOutlined style={{ color: '#F59E0B' }} />
          SHAP Feature Attribution & Risk Drivers
        </div>
        <span
          style={{
            fontSize: 11,
            color: '#64748B',
            background: 'rgba(255,255,255,0.04)',
            padding: '3px 8px',
            borderRadius: 6,
          }}
        >
          Model-driven
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {explanations.map((item, idx) => {
          const isRisk = item.direction === 'increases_risk';
          const impactColor = isRisk ? '#EF4444' : '#10B981';
          const bgShade = isRisk ? 'rgba(239,68,68,0.06)' : 'rgba(16,185,129,0.06)';
          const borderShade = isRisk ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.15)';

          return (
            <div
              key={idx}
              style={{
                background: bgShade,
                border: `1px solid ${borderShade}`,
                borderRadius: 10,
                padding: '12px 14px',
                display: 'flex',
                flexDirection: 'column',
                gap: 6,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 13, fontWeight: 700, color: '#E2E8F0', textTransform: 'capitalize' }}>
                  {item.feature.replace(/_/g, ' ')}
                </span>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: 12,
                    background: `${impactColor}20`,
                    color: impactColor,
                    border: `1px solid ${impactColor}40`,
                  }}
                >
                  {isRisk ? '▲ INCREASES RISK' : '▼ RISK MITIGATOR'} ({item.impact})
                </span>
              </div>
              <p style={{ fontSize: 12, color: '#CBD5E1', margin: 0, lineHeight: 1.5 }}>
                {item.explanation}
              </p>
              {item.benchmark !== undefined && item.benchmark !== null && (
                <div style={{ fontSize: 11, color: '#64748B', display: 'flex', gap: 12, marginTop: 2 }}>
                  <span>Actual: <strong style={{ color: '#E2E8F0' }}>{item.value}</strong></span>
                  <span>Target: <strong style={{ color: '#818CF8' }}>{item.benchmark}</strong></span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

const Dashboard = ({ companyId }) => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setData] = useState(null);
  const [uploading, setUploading] = useState(false);

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

  useEffect(() => {
    if (companyId) fetchDashboardData();
  }, [companyId, fetchDashboardData]);

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      setUploading(true);
      await api.post(`/upload-financial-data/${companyId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      message.success('Financial data analyzed via ML pipeline!');
      fetchDashboardData();
    } catch (err) {
      message.error(err.response?.data?.detail || 'Failed to upload financial data');
    } finally {
      setUploading(false);
    }
    return false;
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 80, gap: 16 }}>
        <Spin size="large" />
        <span style={{ color: '#64748B', fontSize: 13 }}>Loading explainable financial risk assessment…</span>
      </div>
    );
  }

  if (!dashboardData || dashboardData.message === 'No assessments found' || dashboardData.status === 'error') {
    return (
      <div
        style={{
          background: '#131929',
          border: '1px dashed rgba(99,102,241,0.3)',
          borderRadius: 16,
          padding: '60px 24px',
          textAlign: 'center',
        }}
      >
        <div style={{ fontSize: 48, marginBottom: 16 }}>📊</div>
        <div style={{ fontSize: 18, fontWeight: 700, color: '#E2E8F0', marginBottom: 8 }}>No Assessment Generated Yet</div>
        <div style={{ fontSize: 13, color: '#64748B', marginBottom: 28, maxWidth: 450, margin: '0 auto 28px' }}>
          Upload a financial statement (CSV or Excel) to run feature engineering, calibrated ML risk scoring, multi-label recommendations, and SHAP explainability.
        </div>
        <Upload beforeUpload={handleFileUpload} accept=".csv,.xlsx,.xls" showUploadList={false}>
          <button className="btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
            <UploadOutlined /> {uploading ? 'Processing ML Pipeline…' : 'Upload Financial Data'}
          </button>
        </Upload>
      </div>
    );
  }

  const {
    company_info,
    health_scores,
    risk_assessment,
    recommendations,
    cost_optimization,
    shap_explanations,
    executive_summary,
    last_updated,
  } = dashboardData;

  const riskCat = risk_assessment.category || risk_assessment.level || 'MEDIUM';
  const riskColor = RISK_COLOR[riskCat] || '#F59E0B';
  const riskScore = risk_assessment.score !== undefined ? risk_assessment.score : (100 - health_scores.overall);
  const riskProb = risk_assessment.probability !== undefined ? (risk_assessment.probability * 100).toFixed(1) : `${riskScore}%`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* ── ML Risk Header Banner ── */}
      <div
        style={{
          background: 'linear-gradient(135deg, #131929 0%, #172036 100%)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 16,
          padding: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 20,
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
            <DashboardOutlined style={{ color: '#6366F1', fontSize: 22 }} />
            <span style={{ fontSize: 22, fontWeight: 800, color: '#F8FAFC', letterSpacing: '-0.02em' }}>
              {company_info.name}
            </span>
            <span
              style={{
                padding: '4px 12px',
                borderRadius: 20,
                fontSize: 11,
                fontWeight: 700,
                background: 'rgba(99,102,241,0.15)',
                color: '#818CF8',
                border: '1px solid rgba(99,102,241,0.3)',
                textTransform: 'capitalize',
              }}
            >
              {company_info.industry}
            </span>
          </div>

          <div style={{ fontSize: 12, color: '#64748B', marginBottom: 12 }}>
            Last assessed {new Date(last_updated).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
            {risk_assessment.model_version && ` · ${risk_assessment.model_version}`}
          </div>

          {/* Executive narrative if available */}
          {executive_summary?.narrative && (
            <div
              style={{
                fontSize: 13,
                color: '#CBD5E1',
                lineHeight: 1.6,
                maxWidth: 650,
                background: 'rgba(0,0,0,0.25)',
                padding: '10px 14px',
                borderRadius: 8,
                borderLeft: `3px solid ${riskColor}`,
              }}
            >
              {executive_summary.narrative}
            </div>
          )}
        </div>

        {/* Risk Probability Score Gauge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <div
            style={{
              background: '#0B0F19',
              border: `1px solid ${riskColor}50`,
              borderRadius: 14,
              padding: '16px 24px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 11, color: '#64748B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              ML Risk Score
            </div>
            <div style={{ fontSize: 32, fontWeight: 900, color: riskColor, letterSpacing: '-0.02em' }}>
              {riskScore}
              <span style={{ fontSize: 16, fontWeight: 500, color: '#475569' }}>/100</span>
            </div>
            <div
              style={{
                fontSize: 11,
                fontWeight: 700,
                color: riskColor,
                background: `${riskColor}15`,
                padding: '2px 8px',
                borderRadius: 10,
                marginTop: 4,
              }}
            >
              {riskCat} RISK ({riskProb}% Prob)
            </div>
          </div>

          <Upload beforeUpload={handleFileUpload} accept=".csv,.xlsx,.xls" showUploadList={false}>
            <button className="btn-ghost" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
              <UploadOutlined /> {uploading ? 'Processing…' : 'Upload New Data'}
            </button>
          </Upload>
        </div>
      </div>

      {/* ── Component Health Scores ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
        <ScoreCard title="Overall Health" value={health_scores.overall} sub="Combined creditworthiness" />
        <ScoreCard title="Liquidity" value={health_scores.liquidity} sub="Current & quick assets" />
        <ScoreCard title="Profitability" value={health_scores.profitability} sub="Operating & net margins" />
        <ScoreCard title="Leverage & Solvency" value={health_scores.leverage} sub="Debt-to-assets ratio" />
      </div>

      {/* ── SHAP Risk Drivers + Financial Charts ── */}
      <div style={{ display: 'grid', gridTemplateColumns: shap_explanations?.length ? '1fr 1fr' : '1fr', gap: 20 }}>
        {shap_explanations && shap_explanations.length > 0 && (
          <ShapRiskDriversPanel explanations={shap_explanations} riskCategory={riskCat} />
        )}
        <FinancialCharts companyId={companyId} />
      </div>

      {/* ── Ranked Multi-Label Recommendations ── */}
      <Recommendations
        recommendations={recommendations}
        title="ML-Ranked Financial Interventions"
        icon={<ThunderboltOutlined style={{ color: '#6366F1' }} />}
      />
    </div>
  );
};

export default Dashboard;
