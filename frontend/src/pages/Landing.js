import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const STATS = [
  { value: '10,000+', label: 'SMEs Analyzed' },
  { value: '₹2.4B+', label: 'Financing Facilitated' },
  { value: '98.2%', label: 'Assessment Accuracy' },
  { value: '6', label: 'Industries Covered' },
];

const FEATURES = [
  {
    icon: '⚡',
    title: 'AI-Powered Analysis',
    desc: 'GPT-4 driven insights that analyze 20+ financial ratios and surface actionable recommendations in seconds.',
  },
  {
    icon: '🏦',
    title: 'Credit Scoring Engine',
    desc: 'Advanced 0–100 credit scoring algorithm with industry-specific benchmarking for precise creditworthiness.',
  },
  {
    icon: '📊',
    title: 'Real-Time Dashboard',
    desc: 'Live financial health tracking with forecasting, risk heatmaps, and drill-down analytics across your portfolio.',
  },
  {
    icon: '🛡️',
    title: 'Risk Intelligence',
    desc: 'Multi-dimensional risk assessment with early warning signals and mitigation strategy playbooks.',
  },
  {
    icon: '🏢',
    title: 'Multi-Tenant Workspaces',
    desc: 'Org-level tenancy with role-based access — onboard your team and manage all companies in one workspace.',
  },
  {
    icon: '🇮🇳',
    title: 'GST & AA Integration',
    desc: 'Built for India — GST compliance checking, Account Aggregator framework ready, Hindi language support.',
  },
];

export default function Landing() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const canvasRef = useRef(null);

  useEffect(() => {
    if (user) navigate('/app');
  }, [user, navigate]);

  // Particle canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = Array.from({ length: 60 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      r: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.4 + 0.1,
    }));

    let raf;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p) => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(99,102,241,${p.alpha})`;
        ctx.fill();
      });
      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(99,102,241,${0.08 * (1 - dist / 120)})`;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: '#0A0F1E', position: 'relative', overflow: 'hidden' }}>
      <canvas ref={canvasRef} style={{ position: 'fixed', top: 0, left: 0, pointerEvents: 'none', zIndex: 0 }} />

      {/* Navbar */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 48px', height: 64,
        background: 'rgba(10,15,30,0.85)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(99,102,241,0.1)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 16, fontWeight: 800, color: 'white',
          }}>F</div>
          <span style={{ fontSize: 20, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>
            finexri
          </span>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn-ghost" style={{ padding: '8px 20px' }} onClick={() => navigate('/login')}>
            Sign In
          </button>
          <button className="btn-primary" style={{ padding: '8px 20px' }} onClick={() => navigate('/signup')}>
            Get Started Free
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section style={{
        position: 'relative', zIndex: 1,
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', textAlign: 'center',
        minHeight: '100vh', padding: '120px 24px 80px',
      }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '6px 16px', borderRadius: 20,
          background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.3)',
          fontSize: 12, fontWeight: 600, color: '#818CF8', marginBottom: 32,
          letterSpacing: '0.05em', textTransform: 'uppercase',
        }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
          AI-Powered SME Financial Intelligence Platform
        </div>

        <h1 style={{
          fontSize: 'clamp(40px, 6vw, 72px)', fontWeight: 800,
          lineHeight: 1.1, letterSpacing: '-0.03em',
          color: '#F1F5F9', maxWidth: 900, marginBottom: 24,
        }}>
          Financial Health{' '}
          <span style={{
            background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #06B6D4 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>Intelligence</span>
          {' '}for Every SME
        </h1>

        <p style={{
          fontSize: 18, color: '#94A3B8', maxWidth: 600,
          lineHeight: 1.7, marginBottom: 48,
        }}>
          Assess creditworthiness, benchmark against your industry, and get AI-driven recommendations —
          all in one enterprise workspace built for your team.
        </p>

        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', justifyContent: 'center' }}>
          <button className="btn-primary" style={{ padding: '14px 32px', fontSize: 15 }}
            onClick={() => navigate('/signup')}>
            Start for Free →
          </button>
          <button className="btn-ghost" style={{ padding: '14px 32px', fontSize: 15 }}
            onClick={() => navigate('/login')}>
            View Demo
          </button>
        </div>

        {/* Stats bar */}
        <div style={{
          display: 'flex', gap: 0, marginTop: 80,
          background: 'rgba(19,25,41,0.8)', backdropFilter: 'blur(20px)',
          border: '1px solid rgba(99,102,241,0.15)', borderRadius: 16,
          overflow: 'hidden', flexWrap: 'wrap',
        }}>
          {STATS.map((s, i) => (
            <div key={i} style={{
              padding: '24px 48px', textAlign: 'center',
              borderRight: i < STATS.length - 1 ? '1px solid rgba(99,102,241,0.1)' : 'none',
            }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>
                {s.value}
              </div>
              <div style={{ fontSize: 12, color: '#64748B', marginTop: 4, fontWeight: 500 }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section style={{ position: 'relative', zIndex: 1, padding: '80px 48px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <h2 style={{ fontSize: 40, fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em', marginBottom: 16 }}>
            Everything your team needs
          </h2>
          <p style={{ fontSize: 16, color: '#64748B', maxWidth: 500, margin: '0 auto' }}>
            Enterprise-grade financial intelligence, designed for the speed and scale of modern SME lending.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
          {FEATURES.map((f, i) => (
            <div key={i} className="glass-card" style={{
              padding: 28,
              transition: 'border-color 0.2s, transform 0.2s',
              cursor: 'default',
            }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(99,102,241,0.4)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(99,102,241,0.15)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{ fontSize: 28, marginBottom: 14 }}>{f.icon}</div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#F1F5F9', marginBottom: 8 }}>{f.title}</h3>
              <p style={{ fontSize: 14, color: '#64748B', lineHeight: 1.65 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{
        position: 'relative', zIndex: 1, padding: '80px 24px',
        textAlign: 'center',
      }}>
        <div style={{
          maxWidth: 680, margin: '0 auto',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(139,92,246,0.08) 100%)',
          border: '1px solid rgba(99,102,241,0.25)', borderRadius: 24, padding: '60px 48px',
        }}>
          <h2 style={{ fontSize: 36, fontWeight: 800, color: '#F1F5F9', marginBottom: 16, letterSpacing: '-0.02em' }}>
            Ready to transform your SME analysis?
          </h2>
          <p style={{ fontSize: 16, color: '#64748B', marginBottom: 36 }}>
            Join thousands of financial professionals using Finexri to make smarter credit decisions.
          </p>
          <button className="btn-primary" style={{ padding: '14px 40px', fontSize: 15 }}
            onClick={() => navigate('/signup')}>
            Create Your Workspace →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        position: 'relative', zIndex: 1,
        borderTop: '1px solid rgba(255,255,255,0.05)',
        padding: '32px 48px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        flexWrap: 'wrap', gap: 16,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 24, height: 24, borderRadius: 6,
            background: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 12, fontWeight: 800, color: 'white',
          }}>F</div>
          <span style={{ fontSize: 14, fontWeight: 700, color: '#475569' }}>finexri</span>
        </div>
        <span style={{ fontSize: 13, color: '#334155' }}>© 2024 Finexri. Built for SME financial empowerment.</span>
      </footer>
    </div>
  );
}
