import React from 'react';
import { NavLink } from 'react-router-dom';
import { Menu } from 'antd';
import {
  HomeOutlined,
  EnvironmentOutlined,
  UnorderedListOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import ThemeToggle from '../common/ThemeToggle';
import { useTheme } from '../../contexts/ThemeContext';

const AppHeader: React.FC = () => {
  const { theme } = useTheme();

  const menuItems = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: <NavLink to="/">首页</NavLink>,
    },
    {
      key: 'map',
      icon: <EnvironmentOutlined />,
      label: <NavLink to="/map">任务地图</NavLink>,
    },
    {
      key: 'tasks',
      icon: <UnorderedListOutlined />,
      label: <NavLink to="/tasks">任务中心</NavLink>,
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: <NavLink to="/settings">设置</NavLink>,
    },
  ];

  return (
    <header
      className="sticky top-0 bg-bg-secondary/80 backdrop-blur-lg shadow-sm"
      style={{
        zIndex: 'var(--z-nav)',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <div className="container mx-auto flex items-center justify-between p-2">
        <div className="flex items-center gap-2">
          <img src="/logo.svg" alt="CityU Campus Tasks" className="h-8 w-8" />
          <span className="font-bold text-lg text-text-primary hidden md:inline">
            CityU Tasks
          </span>
        </div>
        <nav className="flex-grow flex justify-center">
          <Menu
            mode="horizontal"
            items={menuItems}
            theme={theme}
            className="bg-transparent border-none"
            style={{ flex: '1', justifyContent: 'center' }}
          />
        </nav>
        <div>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};

export default AppHeader;