import React from 'react';

const SEVERITY_STYLES = {
  HIGH: { bg: 'rgba(239,68,68,0.12)', color: '#EF4444', border: 'rgba(239,68,68,0.35)' },
  MEDIUM: { bg: 'rgba(245,158,11,0.12)', color: '#F59E0B', border: 'rgba(245,158,11,0.35)' },
  LOW: { bg: 'rgba(99,102,241,0.12)', color: '#818CF8', border: 'rgba(99,102,241,0.35)' },
};

const Recommendations = ({ recommendations, title, icon, type = 'general' }) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div
        style={{
          background: '#131929',
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: 14,
          padding: 24,
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700, color: '#E2E8F0', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          {icon} {title}
        </div>
        <div style={{ color: '#64748B', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>
          No recommendations needed — all ratios align with industry targets.
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        background: '#131929',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14,
        padding: 24,
      }}
    >
      <div
        style={{
          fontSize: 15,
          fontWeight: 700,
          color: '#F8FAFC',
          marginBottom: 18,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {icon} {title}
        </div>
        <span style={{ fontSize: 11, color: '#64748B', fontWeight: 500 }}>
          Deterministic rule-validated & prioritized
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {recommendations.map((item, i) => {
          // Backward compatibility for raw string recommendations
          if (typeof item === 'string') {
            const parts = item.split('—');
            const recTitle = parts[0] ? parts[0].trim() : item;
            const recReason = parts[1] ? parts[1].trim() : '';

            return (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 12,
                  padding: '14px 16px',
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  borderRadius: 10,
                }}
              >
                <span style={{ color: '#6366F1', fontSize: 16, marginTop: 1, flexShrink: 0 }}>✓</span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#E2E8F0' }}>{recTitle}</div>
                  {recReason && <div style={{ fontSize: 12, color: '#94A3B8', marginTop: 4 }}>{recReason}</div>}
                </div>
              </div>
            );
          }

          // Structured ML recommendation object
          const sev = SEVERITY_STYLES[item.severity || item.priority] || SEVERITY_STYLES.LOW;
          const confPercent = item.confidence ? Math.round(item.confidence * 100) : null;
          const rank = item.priority || i + 1;

          return (
            <div
              key={i}
              style={{
                padding: '16px 18px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid rgba(255,255,255,0.07)',
                borderRadius: 12,
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
                transition: 'border-color 0.2s',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(99,102,241,0.3)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)')}
            >
              {/* Header row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span
                    style={{
                      width: 24,
                      height: 24,
                      borderRadius: '50%',
                      background: 'rgba(99,102,241,0.2)',
                      color: '#818CF8',
                      fontSize: 12,
                      fontWeight: 800,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    #{rank}
                  </span>
                  <span style={{ fontSize: 14, fontWeight: 700, color: '#F1F5F9' }}>
                    {item.title || item.category || item.code}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {confPercent !== null && (
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: 12,
                        fontSize: 11,
                        fontWeight: 700,
                        background: 'rgba(16,185,129,0.15)',
                        color: '#10B981',
                        border: '1px solid rgba(16,185,129,0.3)',
                      }}
                    >
                      {confPercent}% ML Confidence
                    </span>
                  )}
                  {item.severity && (
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: 12,
                        fontSize: 11,
                        fontWeight: 700,
                        background: sev.bg,
                        color: sev.color,
                        border: `1px solid ${sev.border}`,
                      }}
                    >
                      Severity: {item.severity}
                    </span>
                  )}
                  {item.impact && (
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: 12,
                        fontSize: 11,
                        fontWeight: 700,
                        background: 'rgba(99,102,241,0.15)',
                        color: '#818CF8',
                        border: '1px solid rgba(99,102,241,0.3)',
                      }}
                    >
                      Impact: {item.impact}
                    </span>
                  )}
                </div>
              </div>

              {/* Business Description */}
              {item.description && (
                <p style={{ fontSize: 12.5, color: '#94A3B8', margin: '2px 0 0', lineHeight: 1.5 }}>
                  {item.description}
                </p>
              )}

              {/* Rationale / Metric attribution */}
              {(item.rationale || item.suggestion) && (
                <div
                  style={{
                    background: 'rgba(0,0,0,0.2)',
                    padding: '8px 12px',
                    borderRadius: 8,
                    fontSize: 12,
                    color: '#CBD5E1',
                    borderLeft: `2px solid ${sev.color}`,
                    marginTop: 4,
                  }}
                >
                  <strong style={{ color: '#818CF8' }}>Why was this recommended? </strong>
                  {item.rationale || item.suggestion}
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
