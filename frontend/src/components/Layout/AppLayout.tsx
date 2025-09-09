import React from 'react';
import { Layout, Menu, Drawer, Button } from 'antd';
import { MenuOutlined, HomeOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';

const { Header, Content, Footer } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [mobileMenuVisible, setMobileMenuVisible] = useState(false);
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/tasks',
      icon: <AppstoreOutlined />,
      label: <Link to="/tasks">任务中心</Link>,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">设置</Link>,
    },
  ];

  const toggleMobileMenu = () => {
    setMobileMenuVisible(!mobileMenuVisible);
  };

  return (
    <Layout className="min-h-screen">
      <Header className="bg-white shadow-sm px-4 flex items-center justify-between">
        <div className="flex items-center">
          <h1 className="text-xl font-bold text-gray-800 mr-8">
            CityU Campus Tasks
          </h1>
          
          {/* Desktop Menu */}
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            className="hidden md:flex border-none bg-transparent flex-1"
          />
        </div>

        {/* Mobile Menu Button */}
        <Button
          type="text"
          icon={<MenuOutlined />}
          onClick={toggleMobileMenu}
          className="md:hidden"
        />

        {/* Mobile Menu Drawer */}
        <Drawer
          title="菜单"
          placement="right"
          onClose={() => setMobileMenuVisible(false)}
          open={mobileMenuVisible}
          width={280}
        >
          <Menu
            mode="vertical"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={() => setMobileMenuVisible(false)}
          />
        </Drawer>
      </Header>

      <Content className="flex-1">
        <div className="container mx-auto px-4 py-6 max-w-7xl">
          {children}
        </div>
      </Content>

      <Footer className="text-center bg-gray-50 border-t">
        <div className="text-sm text-gray-600">
          CityU Campus Tasks © 2024 - 开放世界地图 × NPC 智能体校园任务系统
        </div>
      </Footer>
    </Layout>
  );
};

export default AppLayout;