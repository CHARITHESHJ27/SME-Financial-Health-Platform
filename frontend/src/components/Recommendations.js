import React from 'react';
import { Card, List, Tag } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

const Recommendations = ({ recommendations, title, icon, type = 'general' }) => {
  const getRecommendationColor = (priority) => {
    const colors = {
      'HIGH': 'red',
      'MEDIUM': 'orange', 
      'LOW': 'blue'
    };
    return colors[priority] || 'default';
  };

  const renderRecommendation = (item, index) => {
    if (typeof item === 'string') {
      return (
        <List.Item key={index}>
          <List.Item.Meta
            avatar={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            description={item}
          />
        </List.Item>
      );
    }

    // For cost optimization objects
    return (
      <List.Item key={index}>
        <List.Item.Meta
          avatar={<ExclamationCircleOutlined style={{ color: '#fa8c16' }} />}
          title={item.category || item.suggestion}
          description={
            <div>
              {item.suggestion && <p>{item.suggestion}</p>}
              {item.potential_savings && (
                <Tag color="green">Savings: {item.potential_savings}</Tag>
              )}
              {item.priority && (
                <Tag color={getRecommendationColor(item.priority)}>
                  {item.priority} Priority
                </Tag>
              )}
            </div>
          }
        />
      </List.Item>
    );
  };

  return (
    <Card title={<>{icon} {title}</>}>
      {recommendations && recommendations.length > 0 ? (
        <List
          dataSource={recommendations}
          renderItem={renderRecommendation}
          size="small"
        />
      ) : (
        <p style={{ color: '#999', textAlign: 'center', padding: '20px' }}>
          No recommendations available
        </p>
      )}
    </Card>
  );
};

export default Recommendations;