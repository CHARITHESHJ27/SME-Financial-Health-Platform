import React, { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Statistic, Progress, Alert, Spin, Button, Upload, message } from 'antd';
import { UploadOutlined, DashboardOutlined, RiseOutlined, WarningOutlined } from '@ant-design/icons';
import api from '../config/api';
import FinancialCharts from '../charts/FinancialCharts';
import Recommendations from './Recommendations';

const Dashboard = ({ companyId }) => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [uploading, setUploading] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get(`/companies/${companyId}/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      message.error('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => {
    if (companyId) {
      fetchDashboardData();
    }
  }, [companyId, fetchDashboardData]);

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      await api.post(`/upload-financial-data/${companyId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      message.success('Financial data uploaded successfully');
      message.success('Financial assessment completed');
      fetchDashboardData();
      
    } catch (error) {
      message.error('Failed to upload financial data');
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
    
    return false;
  };

  const getIndustryBenchmark = (industry, profitScore) => {
    const benchmarks = {
      retail: { avg: 65, message: profitScore > 65 ? 'above' : 'below' },
      services: { avg: 70, message: profitScore > 70 ? 'above' : 'below' },
      manufacturing: { avg: 60, message: profitScore > 60 ? 'above' : 'below' },
      logistics: { avg: 55, message: profitScore > 55 ? 'above' : 'below' },
      agriculture: { avg: 50, message: profitScore > 50 ? 'above' : 'below' },
      'e-commerce': { avg: 75, message: profitScore > 75 ? 'above' : 'below' }
    };
    const benchmark = benchmarks[industry] || benchmarks.services;
    return `Your profitability is ${Math.abs(profitScore - benchmark.avg).toFixed(0)}% ${benchmark.message} ${industry} industry average`;
  };

  const getCreditReadiness = (healthScore, riskLevel) => {
    if (healthScore >= 80 && riskLevel === 'MINIMAL') return { status: 'Excellent', color: '#52c41a' };
    if (healthScore >= 70 && ['MINIMAL', 'LOW'].includes(riskLevel)) return { status: 'Good', color: '#faad14' };
    if (healthScore >= 50) return { status: 'Moderate', color: '#fa8c16' };
    return { status: 'Weak', color: '#f5222d' };
  };

  const getHealthScoreColor = (score) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    if (score >= 40) return '#fa8c16';
    return '#f5222d';
  };

  const getRiskLevelColor = (level) => {
    const colors = {
      'MINIMAL': '#52c41a',
      'LOW': '#faad14',
      'MEDIUM': '#fa8c16',
      'HIGH': '#f5222d'
    };
    return colors[level] || '#d9d9d9';
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>Loading financial dashboard...</p>
      </div>
    );
  }

  if (!dashboardData || dashboardData.message === "No assessments found" || dashboardData.status === 'error') {
    return (
      <div style={{ padding: '20px' }}>
        <Alert
          message="No Assessment Data"
          description="Please upload financial data or create a new assessment to view the dashboard."
          type="info"
          showIcon
          action={
            <Upload
              beforeUpload={handleFileUpload}
              accept=".csv,.xlsx,.xls"
              showUploadList={false}
            >
              <Button type="primary" icon={<UploadOutlined />} loading={uploading}>
                Upload Financial Data
              </Button>
            </Upload>
          }
        />
      </div>
    );
  }

  const { company_info, health_scores, risk_assessment, recommendations, cost_optimization, last_updated } = dashboardData;
  const creditReadiness = getCreditReadiness(health_scores.overall, risk_assessment.level);
  const industryBenchmark = getIndustryBenchmark(company_info.industry, health_scores.profitability);

  return (
    <div style={{ padding: '20px' }}>
      <Row gutter={[16, 16]} style={{ marginBottom: '20px' }}>
        <Col span={24}>
          <Card>
            <Row justify="space-between" align="middle">
              <Col>
                <h1 style={{ margin: 0 }}>
                  <DashboardOutlined /> {company_info.name}
                </h1>
                <p style={{ margin: 0, color: '#666' }}>
                  {company_info.industry} • Last Updated: {new Date(last_updated).toLocaleDateString()}
                </p>
                <div style={{ marginTop: '8px' }}>
                  <span style={{ 
                    padding: '4px 12px', 
                    borderRadius: '12px', 
                    backgroundColor: creditReadiness.color, 
                    color: 'white', 
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}>
                    Credit Readiness: {creditReadiness.status}
                  </span>
                </div>
              </Col>
              <Col>
                <Upload
                  beforeUpload={handleFileUpload}
                  accept=".csv,.xlsx,.xls"
                  showUploadList={false}
                >
                  <Button type="primary" icon={<UploadOutlined />} loading={uploading}>
                    Upload New Data
                  </Button>
                </Upload>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: '20px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Overall Health Score"
              value={health_scores.overall}
              suffix="/100"
              valueStyle={{ color: getHealthScoreColor(health_scores.overall) }}
            />
            <Progress
              percent={health_scores.overall}
              strokeColor={getHealthScoreColor(health_scores.overall)}
              showInfo={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Liquidity Score"
              value={health_scores.liquidity}
              suffix="/100"
              valueStyle={{ color: getHealthScoreColor(health_scores.liquidity) }}
            />
            <Progress
              percent={health_scores.liquidity}
              strokeColor={getHealthScoreColor(health_scores.liquidity)}
              showInfo={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Profitability Score"
              value={health_scores.profitability}
              suffix="/100"
              valueStyle={{ color: getHealthScoreColor(health_scores.profitability) }}
            />
            <Progress
              percent={health_scores.profitability}
              strokeColor={getHealthScoreColor(health_scores.profitability)}
              showInfo={false}
              size="small"
            />
            <div style={{ fontSize: '11px', color: '#666', marginTop: '4px' }}>
              {industryBenchmark}
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Leverage Score"
              value={health_scores.leverage}
              suffix="/100"
              valueStyle={{ color: getHealthScoreColor(health_scores.leverage) }}
            />
            <Progress
              percent={health_scores.leverage}
              strokeColor={getHealthScoreColor(health_scores.leverage)}
              showInfo={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: '20px' }}>
        <Col span={24}>
          <Card title="Why This Score?" size="small">
            <p style={{ margin: 0, fontSize: '13px', color: '#666' }}>
              Score is based on <strong>liquidity</strong> ({health_scores.liquidity}/100), 
              <strong> profitability</strong> ({health_scores.profitability}/100), 
              <strong> leverage control</strong> ({health_scores.leverage}/100), and 
              <strong> cash flow stability</strong>. Higher scores indicate better financial health and creditworthiness.
            </p>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: '20px' }}>
        <Col xs={24} lg={8}>
          <Card title={<><WarningOutlined /> Risk Assessment</>}>
            <div style={{ textAlign: 'center', marginBottom: '16px' }}>
              <div
                style={{
                  display: 'inline-block',
                  padding: '8px 16px',
                  borderRadius: '20px',
                  backgroundColor: getRiskLevelColor(risk_assessment.level),
                  color: 'white',
                  fontWeight: 'bold'
                }}
              >
                {risk_assessment.level} RISK
              </div>
            </div>
            
            {risk_assessment.risks && risk_assessment.risks.length > 0 ? (
              <div>
                <h4>Identified Risks:</h4>
                <ul>
                  {risk_assessment.risks.map((risk, index) => (
                    <li key={index} style={{ marginBottom: '8px' }}>
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <p style={{ color: '#52c41a' }}>No significant risks identified</p>
            )}
          </Card>
        </Col>
        
        <Col xs={24} lg={16}>
          <FinancialCharts companyId={companyId} />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Recommendations 
            recommendations={recommendations} 
            title="AI Recommendations"
            icon={<RiseOutlined />}
          />
        </Col>
        <Col xs={24} lg={12}>
          <Recommendations 
            recommendations={cost_optimization} 
            title="Cost Optimization"
            icon={<RiseOutlined />}
            type="cost"
          />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;