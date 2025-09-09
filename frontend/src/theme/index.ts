import { theme } from 'antd';

export const customTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',
    borderRadius: 8,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      headerHeight: 64,
    },
    Button: {
      borderRadius: 8,
    },
    Card: {
      borderRadius: 12,
    },
  },
};

export const mobileBreakpoints = {
  xs: '480px',
  sm: '576px', 
  md: '768px',
  lg: '992px',
  xl: '1200px',
  xxl: '1600px',
};