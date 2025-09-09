import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { customTheme } from './theme';
import AppLayout from './components/Layout/AppLayout';
import HomePage from './pages/HomePage';
import TasksPage from './pages/TasksPage';
import SettingsPage from './pages/SettingsPage';
import './App.css';

function App() {
  return (
    <ConfigProvider theme={customTheme}>
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </AppLayout>
      </Router>
    </ConfigProvider>
  );
}

export default App;