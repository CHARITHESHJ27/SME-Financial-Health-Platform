import React, { useState, useEffect, useCallback } from 'react';
import { Card, Select, Spin } from 'antd';
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
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale
);

const { Option } = Select;

const FinancialCharts = ({ companyId }) => {
  const [loading, setLoading] = useState(false);
  const [chartType, setChartType] = useState('trends');
  const [forecastData, setForecastData] = useState(null);

  const fetchChartData = useCallback(async () => {
    try {
      setLoading(true);
      
      if (chartType === 'forecast') {
        const response = await axios.get(`/api/v1/companies/${companyId}/forecast?months=12`);
        setForecastData(response.data);
      }
    } catch (error) {
      console.error('Error fetching chart data:', error);
    } finally {
      setLoading(false);
    }
  }, [companyId, chartType]);

  useEffect(() => {
    if (companyId) {
      fetchChartData();
    }
  }, [companyId, fetchChartData]);

  const getTrendsChart = () => {
    const data = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      datasets: [
        {
          label: 'Revenue',
          data: [1500, 1650, 1800, 1750, 1900, 2100, 2200, 2000, 2300, 2500, 2800, 3000],
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
        },
        {
          label: 'Expenses',
          data: [1200, 1280, 1350, 1320, 1400, 1550, 1600, 1480, 1650, 1800, 1950, 2100],
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.1,
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Revenue vs Expenses Trend (₹ in thousands)',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '₹' + value + 'K';
            }
          }
        }
      }
    };

    return <Line data={data} options={options} />;
  };

  const getRatiosChart = () => {
    const data = {
      labels: ['Current Ratio', 'Quick Ratio', 'Debt-to-Asset', 'Profit Margin', 'ROA'],
      datasets: [
        {
          label: 'Your Company',
          data: [1.8, 1.4, 0.35, 0.12, 0.08],
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
        },
        {
          label: 'Industry Average',
          data: [1.5, 1.2, 0.50, 0.08, 0.06],
          backgroundColor: 'rgba(255, 206, 86, 0.6)',
          borderColor: 'rgba(255, 206, 86, 1)',
          borderWidth: 2,
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Financial Ratios Comparison',
        },
      },
      scales: {
        r: {
          beginAtZero: true,
          max: 2,
        },
      },
    };

    return <Radar data={data} options={options} />;
  };

  const getHealthScoreChart = () => {
    const data = {
      labels: ['Liquidity', 'Profitability', 'Leverage', 'Efficiency', 'Growth'],
      datasets: [
        {
          data: [75, 68, 82, 60, 85],
          backgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#9966FF',
          ],
          hoverBackgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#9966FF',
          ],
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
        },
        title: {
          display: true,
          text: 'Health Score Breakdown',
        },
      },
    };

    return <Doughnut data={data} options={options} />;
  };

  const getForecastChart = () => {
    if (!forecastData || !forecastData.forecast_data) {
      return <div>No forecast data available</div>;
    }

    const data = {
      labels: forecastData.forecast_data.map(item => item.month),
      datasets: [
        {
          label: 'Projected Health Score',
          data: forecastData.forecast_data.map(item => item.projected_health_score),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
        },
        {
          label: 'Confidence Level',
          data: forecastData.forecast_data.map(item => item.confidence_level * 100),
          borderColor: 'rgb(255, 159, 64)',
          backgroundColor: 'rgba(255, 159, 64, 0.2)',
          tension: 0.1,
          yAxisID: 'y1',
        },
      ],
    };

    const options = {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        title: {
          display: true,
          text: `Financial Health Forecast - ${forecastData.forecast_period}`,
        },
      },
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Health Score',
          },
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Confidence %',
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    };

    return <Line data={data} options={options} />;
  };

  const renderChart = () => {
    if (loading) {
      return (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
        </div>
      );
    }

    switch (chartType) {
      case 'trends':
        return getTrendsChart();
      case 'ratios':
        return getRatiosChart();
      case 'health':
        return getHealthScoreChart();
      case 'forecast':
        return getForecastChart();
      default:
        return getTrendsChart();
    }
  };

  return (
    <Card
      title="Financial Analytics"
      extra={
        <Select
          value={chartType}
          onChange={setChartType}
          style={{ width: 150 }}
        >
          <Option value="trends">Revenue Trends</Option>
          <Option value="ratios">Financial Ratios</Option>
          <Option value="health">Health Scores</Option>
          <Option value="forecast">Forecast</Option>
        </Select>
      }
    >
      <div style={{ height: '400px' }}>
        {renderChart()}
      </div>
    </Card>
  );
};

export default FinancialCharts;