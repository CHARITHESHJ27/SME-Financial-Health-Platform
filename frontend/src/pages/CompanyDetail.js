import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Dashboard from '../components/Dashboard';
import api from '../config/api';

export default function CompanyDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [company, setCompany] = useState(null);

  useEffect(() => {
    // Try to get from local cache first
    const stored = JSON.parse(localStorage.getItem('finexri_companies') || '[]');
    const found = stored.find(c => String(c.id) === String(id));
    if (found) setCompany(found);
    // Also fetch dashboard for name fallback
    api.get(`/companies/${id}/dashboard`)
      .then(r => { if (r.data?.company_info) setCompany(r.data.company_info); })
      .catch(() => {});
  }, [id]);

  return (
    <div>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 24, fontSize: 13 }}>
        <button onClick={() => navigate('/app')} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: '#475569', padding: 0, fontFamily: 'inherit',
        }}>Overview</button>
        <span style={{ color: '#334155' }}>›</span>
        <button onClick={() => navigate('/app/companies')} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: '#475569', padding: 0, fontFamily: 'inherit',
        }}>Companies</button>
        <span style={{ color: '#334155' }}>›</span>
        <span style={{ color: '#818CF8', fontWeight: 600 }}>
          {company?.name || `Company #${id}`}
        </span>
      </div>

      <Dashboard companyId={parseInt(id)} />
    </div>
  );
}
