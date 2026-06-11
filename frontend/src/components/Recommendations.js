import React from 'react';

const PRIORITY_STYLES = {
  HIGH:   { bg: 'rgba(239,68,68,0.12)',   color: '#EF4444', border: 'rgba(239,68,68,0.3)' },
  MEDIUM: { bg: 'rgba(245,158,11,0.12)',  color: '#F59E0B', border: 'rgba(245,158,11,0.3)' },
  LOW:    { bg: 'rgba(99,102,241,0.12)',  color: '#818CF8', border: 'rgba(99,102,241,0.3)' },
};

const Recommendations = ({ recommendations, title, icon, type = 'general' }) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div style={{
        background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14, padding: 24,
      }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: '#E2E8F0', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          {icon} {title}
        </div>
        <div style={{ color: '#475569', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>
          No recommendations available
        </div>
      </div>
    );
  }

  return (
    <div style={{
      background: '#131929', border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 14, padding: 24,
    }}>
      <div style={{ fontSize: 14, fontWeight: 700, color: '#E2E8F0', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
        {icon} {title}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {recommendations.map((item, i) => {
          if (typeof item === 'string') {
            return (
              <div key={i} style={{
                display: 'flex', alignItems: 'flex-start', gap: 12,
                padding: '12px 14px',
                background: 'rgba(16,185,129,0.06)',
                border: '1px solid rgba(16,185,129,0.15)',
                borderRadius: 10,
              }}>
                <span style={{ color: '#10B981', fontSize: 14, marginTop: 1, flexShrink: 0 }}>✓</span>
                <span style={{ fontSize: 13, color: '#CBD5E1', lineHeight: 1.6 }}>{item}</span>
              </div>
            );
          }

          const p = PRIORITY_STYLES[item.priority] || PRIORITY_STYLES.LOW;
          return (
            <div key={i} style={{
              padding: '14px',
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 10,
            }}>
              {/* Header row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: item.suggestion ? 8 : 0 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: '#E2E8F0' }}>
                  {item.category || item.suggestion}
                </span>
                {item.priority && (
                  <span style={{
                    padding: '2px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700,
                    background: p.bg, color: p.color, border: `1px solid ${p.border}`,
                    flexShrink: 0, marginLeft: 8,
                  }}>
                    {item.priority}
                  </span>
                )}
              </div>

              {/* Suggestion text */}
              {item.suggestion && item.category && (
                <p style={{ fontSize: 12, color: '#94A3B8', margin: '0 0 10px', lineHeight: 1.6 }}>
                  {item.suggestion}
                </p>
              )}

              {/* Savings badge */}
              {item.potential_savings && (
                <div style={{
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                  padding: '4px 12px', borderRadius: 8,
                  background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)',
                }}>
                  <span style={{ fontSize: 11, color: '#6EE7B7', fontWeight: 500 }}>💰 Potential Savings</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: '#10B981' }}>
                    ₹{Number(item.potential_savings).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Recommendations;
