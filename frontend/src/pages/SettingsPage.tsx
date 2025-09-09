import React from 'react';
import { Card, Switch, Select, Divider, Button, message } from 'antd';
import { SettingOutlined, BellOutlined, EyeOutlined } from '@ant-design/icons';

const { Option } = Select;

const SettingsPage: React.FC = () => {
  const handleSave = () => {
    message.success('设置已保存');
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">系统设置</h1>
        <p className="text-gray-600">个性化你的校园任务体验</p>
      </div>

      <Card title={<><SettingOutlined className="mr-2" />基础设置</>}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">语言设置</div>
              <div className="text-sm text-gray-500">选择界面显示语言</div>
            </div>
            <Select defaultValue="zh-CN" style={{ width: 120 }}>
              <Option value="zh-CN">简体中文</Option>
              <Option value="en-US">English</Option>
            </Select>
          </div>

          <Divider />

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">主题模式</div>
              <div className="text-sm text-gray-500">选择浅色或深色主题</div>
            </div>
            <Select defaultValue="light" style={{ width: 120 }}>
              <Option value="light">浅色模式</Option>
              <Option value="dark">深色模式</Option>
              <Option value="auto">跟随系统</Option>
            </Select>
          </div>

          <Divider />

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">自动保存</div>
              <div className="text-sm text-gray-500">自动保存任务进度</div>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </Card>

      <Card title={<><BellOutlined className="mr-2" />通知设置</>}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">桌面通知</div>
              <div className="text-sm text-gray-500">接收任务更新的桌面通知</div>
            </div>
            <Switch defaultChecked />
          </div>

          <Divider />

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">邮件通知</div>
              <div className="text-sm text-gray-500">接收重要任务的邮件提醒</div>
            </div>
            <Switch />
          </div>

          <Divider />

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">声音提醒</div>
              <div className="text-sm text-gray-500">任务完成时播放提示音</div>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </Card>

      <Card title={<><EyeOutlined className="mr-2" />显示设置</>}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">紧凑模式</div>
              <div className="text-sm text-gray-500">使用更紧凑的界面布局</div>
            </div>
            <Switch />
          </div>

          <Divider />

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">显示任务ID</div>
              <div className="text-sm text-gray-500">在任务列表中显示任务ID</div>
            </div>
            <Switch defaultChecked />
          </div>

          <Divider />

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">动画效果</div>
              <div className="text-sm text-gray-500">启用界面过渡动画</div>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </Card>

      <Card title="系统信息">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="text-sm text-gray-500 mb-1">前端版本</div>
            <div className="font-medium">v1.0.0</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">构建时间</div>
            <div className="font-medium">{new Date().toLocaleDateString()}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">技术栈</div>
            <div className="font-medium">React + TypeScript + Vite</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">UI框架</div>
            <div className="font-medium">Ant Design + Tailwind CSS</div>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <Button type="primary" size="large" onClick={handleSave}>
          保存设置
        </Button>
      </div>
    </div>
  );
};

export default SettingsPage;