import React, { useState, useEffect, useCallback } from 'react';
import { Spin } from 'antd';
import { Line, Doughnut, Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
} from 'chart.js';
import axios from 'axios';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, ArcElement, RadialLinearScale
);

const TOOLTIP_STYLE = {
  backgroundColor: '#1A2235',
  borderColor: 'rgba(99,102,241,0.25)',
  borderWidth: 1,
  titleColor: '#F1F5F9',
  bodyColor: '#94A3B8',
  padding: 10,
};

const DARK_LEGEND = {
  labels: { color: '#94A3B8', font: { size: 12 } },
};

const TABS = [
  { key: 'trends',   label: 'Revenue Trends' },
  { key: 'ratios',   label: 'Ratios' },
  { key: 'health',   label: 'Health Scores' },
  { key: 'forecast', label: 'Forecast' },
];

const FinancialCharts = ({ companyId }) => {
  const [loading, setLoading]         = useState(false);
  const [chartType, setChartType]     = useState('trends');
  const [forecastData, setForecastData] = useState(null);

  const fetchChartData = useCallback(async () => {
    if (chartType !== 'forecast') return;
    try {
      setLoading(true);
      const res = await axios.get(`/api/v1/companies/${companyId}/forecast?months=12`);
      setForecastData(res.data);
    } catch (e) {
      console.error('Forecast fetch error:', e);
    } finally {
      setLoading(false);
    }
  }, [companyId, chartType]);

  useEffect(() => { if (companyId) fetchChartData(); }, [companyId, fetchChartData]);

  const getTrendsChart = () => (
    <Line
      data={{
        labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
        datasets: [
          {
            label: 'Revenue',
            data: [1500,1650,1800,1750,1900,2100,2200,2000,2300,2500,2800,3000],
            borderColor: '#6366F1', backgroundColor: 'rgba(99,102,241,0.1)', tension: 0.4, pointRadius: 3,
          },
          {
            label: 'Expenses',
            data: [1200,1280,1350,1320,1400,1550,1600,1480,1650,1800,1950,2100],
            borderColor: '#EF4444', backgroundColor: 'rgba(239,68,68,0.1)', tension: 0.4, pointRadius: 3,
          },
        ],
      }}
      options={{
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: DARK_LEGEND, tooltip: { ...TOOLTIP_STYLE } },
        scales: {
          x: { ticks: { color: '#475569', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
          y: { ticks: { color: '#475569', font: { size: 11 }, callback: v => '₹' + v + 'K' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        },
      }}
    />
  );

  const getRatiosChart = () => (
    <Radar
      data={{
        labels: ['Current Ratio','Quick Ratio','Debt-to-Asset','Profit Margin','ROA'],
        datasets: [
          {
            label: 'Your Company',
            data: [1.8,1.4,0.35,0.12,0.08],
            backgroundColor: 'rgba(99,102,241,0.2)', borderColor: '#6366F1', borderWidth: 2, pointBackgroundColor: '#6366F1',
          },
          {
            label: 'Industry Average',
            data: [1.5,1.2,0.50,0.08,0.06],
            backgroundColor: 'rgba(245,158,11,0.15)', borderColor: '#F59E0B', borderWidth: 2, pointBackgroundColor: '#F59E0B',
          },
        ],
      }}
      options={{
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: DARK_LEGEND, tooltip: { ...TOOLTIP_STYLE } },
        scales: {
          r: {
            ticks: { color: '#475569', backdropColor: 'transparent', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.08)' },
            pointLabels: { color: '#94A3B8', font: { size: 11 } },
          },
        },
      }}
    />
  );

  const getHealthChart = () => (
    <Doughnut
      data={{
        labels: ['Liquidity','Profitability','Leverage','Efficiency','Growth'],
        datasets: [{
          data: [75,68,82,60,85],
          backgroundColor: ['#6366F1','#10B981','#F59E0B','#06B6D4','#8B5CF6'],
          borderColor: '#131929', borderWidth: 3,
        }],
      }}
      options={{
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { color: '#94A3B8', font: { size: 12 }, padding: 16 } },
          tooltip: { ...TOOLTIP_STYLE },
        },
        cutout: '65%',
      }}
    />
  );

  const getForecastChart = () => {
    if (!forecastData?.forecast_data) {
      return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#475569', fontSize: 13 }}>
          No forecast data — need at least 3 assessments
        </div>
      );
    }
    return (
      <Line
        data={{
          labels: forecastData.forecast_data.map(d => d.month),
          datasets: [
            {
              label: 'Projected Health Score',
              data: forecastData.forecast_data.map(d => d.projected_health_score),
              borderColor: '#10B981', backgroundColor: 'rgba(16,185,129,0.1)', tension: 0.4, pointRadius: 3,
            },
            {
              label: 'Confidence %',
              data: forecastData.forecast_data.map(d => d.confidence_level * 100),
              borderColor: '#F59E0B', backgroundColor: 'rgba(245,158,11,0.1)', tension: 0.4, pointRadius: 3, yAxisID: 'y1',
            },
          ],
        }}
        options={{
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: DARK_LEGEND, tooltip: { ...TOOLTIP_STYLE } },
          scales: {
            x: { ticks: { color: '#475569', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
            y:  { ticks: { color: '#475569', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
            y1: { position: 'right', ticks: { color: '#475569', font: { size: 11 } }, grid: { drawOnChartArea: false } },
          },
        }}
      />
    );
  };

  const renderChart = () => {
    if (loading) return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Spin size="large" />
      </div>
    );
    switch (chartType) {
      case 'trends':   return getTrendsChart();
      case 'ratios':   return getRatiosChart();
      case 'health':   return getHealthChart();
      case 'forecast': return getForecastChart();
      default:         return getTrendsChart();
    }
  };

  return (
    <div style={{ background: '#131929', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 22 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 10 }}>
        <span style={{ fontSize: 14, fontWeight: 700, color: '#E2E8F0' }}>Financial Analytics</span>
        <div style={{ display: 'flex', gap: 6 }}>
          {TABS.map(t => (
            <button key={t.key} onClick={() => setChartType(t.key)} style={{
              padding: '6px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
              border: '1px solid',
              borderColor: chartType === t.key ? '#6366F1' : 'rgba(255,255,255,0.06)',
              background: chartType === t.key ? 'rgba(99,102,241,0.15)' : 'transparent',
              color: chartType === t.key ? '#818CF8' : '#64748B',
              cursor: 'pointer', fontFamily: 'inherit',
            }}>{t.label}</button>
          ))}
        </div>
      </div>
      <div style={{ height: 300 }}>
        {renderChart()}
      </div>
    </div>
  );
};

export default FinancialCharts;
