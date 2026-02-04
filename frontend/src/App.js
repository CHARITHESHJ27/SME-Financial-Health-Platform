import React, { useState } from 'react';
import { Layout, Menu, Button, Modal, Form, Input, Select } from 'antd';
import { DashboardOutlined, PlusOutlined } from '@ant-design/icons';
import api from './config/api';
import Dashboard from './components/Dashboard';
import 'antd/dist/reset.css';

const { Header, Content, Sider } = Layout;
const { Option } = Select;

function App() {
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  const handleCreateCompany = async (values) => {
    try {
      const response = await api.post('/companies/', values);
      setCompanies([...companies, response.data]);
      setSelectedCompany(response.data.id);
      setIsModalVisible(false);
      form.resetFields();
    } catch (error) {
      console.error('Error creating company:', error);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 20px' }}>
        <div style={{ color: 'white', fontSize: '18px', fontWeight: 'bold' }}>
          SME Financial Health Platform
        </div>
      </Header>
      
      <Layout>
        <Sider width={250} style={{ background: '#fff' }}>
          <div style={{ padding: '16px' }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setIsModalVisible(true)}
              style={{ width: '100%', marginBottom: '16px' }}
            >
              Add Company
            </Button>
            
            <Menu mode="inline" selectedKeys={[selectedCompany?.toString()]}>
              {companies.map(company => (
                <Menu.Item 
                  key={company.id} 
                  icon={<DashboardOutlined />}
                  onClick={() => setSelectedCompany(company.id)}
                >
                  {company.name}
                </Menu.Item>
              ))}
            </Menu>
          </div>
        </Sider>
        
        <Content style={{ padding: '0', background: '#f0f2f5' }}>
          {selectedCompany ? (
            <Dashboard companyId={selectedCompany} />
          ) : (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '100%',
              flexDirection: 'column'
            }}>
              <h2>Welcome to SME Financial Health Platform</h2>
              <p>Create or select a company to view financial dashboard</p>
              <Button 
                type="primary" 
                size="large"
                icon={<PlusOutlined />}
                onClick={() => setIsModalVisible(true)}
              >
                Create Your First Company
              </Button>
            </div>
          )}
        </Content>
      </Layout>

      <Modal
        title="Create New Company"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleCreateCompany} layout="vertical">
          <Form.Item
            name="name"
            label="Company Name"
            rules={[{ required: true, message: 'Please enter company name' }]}
          >
            <Input placeholder="Enter company name" />
          </Form.Item>
          
          <Form.Item
            name="industry"
            label="Industry"
            rules={[{ required: true, message: 'Please select industry' }]}
          >
            <Select placeholder="Select industry">
              <Option value="manufacturing">Manufacturing</Option>
              <Option value="retail">Retail</Option>
              <Option value="services">Services</Option>
              <Option value="agriculture">Agriculture</Option>
              <Option value="logistics">Logistics</Option>
              <Option value="e-commerce">E-commerce</Option>
            </Select>
          </Form.Item>
          
          <Form.Item name="gst_number" label="GST Number">
            <Input placeholder="Enter GST number (optional)" />
          </Form.Item>
          
          <Form.Item name="language_preference" label="Language Preference">
            <Select defaultValue="english">
              <Option value="english">English</Option>
              <Option value="hindi">Hindi</Option>
            </Select>
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
              Create Company
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
}

export default App;