import React, { useState, useEffect } from 'react';
import { Drawer, Tag, Button, Space, Progress } from 'antd';
import {
  CloseOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined,
  MessageOutlined,
  ShareAltOutlined,
  CheckCircleOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { TaskLocation } from '../../data/seedTasks';
import ChatPanel from './ChatPanel.tsx';
import { getCategoryIcon, getDifficultyTag, getStatusTag } from '../../utils/taskUtils.tsx';

interface TaskDrawerProps {
  task: TaskLocation | null;
  open: boolean;
  onClose: () => void;
  onOpenOnMap: (task: TaskLocation) => void;
  mask?: boolean;
  maskClosable?: boolean;
  keyboard?: boolean;
  destroyOnClose?: boolean;
  forceRender?: boolean;
  getContainer?: string | HTMLElement | (() => HTMLElement) | false;
  style?: React.CSSProperties;
}

const TaskDrawer: React.FC<TaskDrawerProps> = ({
  task,
  open,
  onClose,
  onOpenOnMap,
  mask = true,
  maskClosable = true,
  keyboard = true,
  destroyOnClose = false,
  forceRender = false,
  getContainer,
  style = {}
}) => {
  const [activeTab, setActiveTab] = useState<'details' | 'chat'>('details');
  const [taskProgress, setTaskProgress] = useState(0);

  useEffect(() => {
    if (task) {
      const progress =
        task.status === 'completed' ? 100 :
        task.status === 'in_progress' ? 65 : 0;
      setTaskProgress(progress);
    }
  }, [task]);

  if (!task) return null;

  const handleOpenOnMap = () => {
    onOpenOnMap(task);
    onClose();
  };

  const CategoryIcon = getCategoryIcon(task.category);

  return (
    <Drawer
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CategoryIcon className="text-2xl text-primary" />
            <span className="font-semibold text-text text-lg">{task.title}</span>
          </div>
        </div>
      }
      placement="right"
      width={480}
      open={open}
      onClose={onClose}
      closable={true}
      closeIcon={<CloseOutlined className="text-text-secondary hover:text-primary transition-colors" />}
      mask={mask}
      maskClosable={maskClosable}
      keyboard={keyboard}
      destroyOnClose={destroyOnClose}
      forceRender={forceRender}
      getContainer={getContainer}
      style={style}
      styles={{
        body: { 
          padding: 0, 
          backgroundColor: 'rgb(var(--color-bg-secondary))',
          minHeight: '100%'
        },
        header: {
          padding: '16px 24px',
          backgroundColor: 'rgb(var(--color-bg-elevated))',
          borderBottom: '1px solid rgb(var(--color-border))',
          minHeight: '56px'
        },
        content: {
          backgroundColor: 'rgb(var(--color-bg-secondary))',
          display: 'flex',
          flexDirection: 'column'
        },
        wrapper: {
          zIndex: 'var(--z-drawer)'
        }
      }}
      extra={
        <Space>
          <Button
            type="text"
            icon={<EnvironmentOutlined />}
            onClick={handleOpenOnMap}
            className="!text-text-secondary hover:!text-primary transition-colors"
            tabIndex={0}
          >
            地图
          </Button>
        </Space>
      }
    >
      {/* Tab Navigation */}
      <div className="mb-4 border-b border-border/50">
        <div className="flex -mb-px px-6">
          <button
            className={`px-4 py-3 border-b-2 font-medium text-sm transition-all ${
              activeTab === 'details'
                ? 'border-primary text-primary'
                : 'border-transparent text-text-secondary hover:text-text hover:border-border'
            }`}
            onClick={() => setActiveTab('details')}
          >
            任务详情
          </button>
          <button
            className={`px-4 py-3 border-b-2 font-medium text-sm transition-all ${
              activeTab === 'chat'
                ? 'border-primary text-primary'
                : 'border-transparent text-text-secondary hover:text-text hover:border-border'
            }`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageOutlined className="mr-2" />
            任务助手
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        {activeTab === 'details' && (
          <div className="space-y-5">
            {/* Task Description */}
            <p className="text-text-secondary leading-relaxed">{task.description}</p>

            {/* Task Status & Progress */}
            <div className="p-4 rounded-lg bg-bg-elevated">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-text-secondary">任务状态</span>
                {getStatusTag(task.status)}
              </div>
              {task.status === 'in_progress' && (
                <div>
                  <div className="flex justify-between text-sm mb-1 text-text-secondary">
                    <span>完成进度</span>
                    <span className="font-mono text-text">{taskProgress}%</span>
                  </div>
                  <Progress percent={taskProgress} size="small" showInfo={false} />
                </div>
              )}
            </div>

            {/* Task Info Grid */}
            <div className="p-4 rounded-lg bg-bg-elevated">
              <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-3 text-sm items-center">
                <span className="text-text-secondary font-medium">类别:</span>
                <div className="flex items-center gap-2">
                  <CategoryIcon className="text-primary" />
                  <span className="text-text">{task.category}</span>
                </div>

                <span className="text-text-secondary font-medium">难度:</span>
                <div>{getDifficultyTag(task.difficulty)}</div>

                {task.course && (
                  <>
                    <span className="text-text-secondary font-medium">课程:</span>
                    <div className="flex items-center gap-2 text-text">
                      <BookOutlined className="text-text" />
                      <span>{task.course}</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Location & Time */}
            <div className="p-4 rounded-lg bg-bg-elevated">
                <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-3 text-sm items-center">
                    <span className="text-text-secondary font-medium">位置:</span>
                    <div className="flex items-center gap-2 text-text">
                        <EnvironmentOutlined className="text-text" />
                        <span>{task.location.name}</span>
                    </div>

                    {task.estimatedTime && (
                        <>
                            <span className="text-text-secondary font-medium">用时:</span>
                            <div className="flex items-center gap-2 text-text">
                                <ClockCircleOutlined className="text-text" />
                                <span>{task.estimatedTime} 分钟</span>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* Rewards */}
            {task.rewards && task.rewards.length > 0 && (
              <div className="p-4 rounded-lg bg-bg-elevated">
                <div className="text-sm font-medium text-text-secondary mb-2">任务奖励:</div>
                <div className="flex flex-wrap gap-2">
                  {task.rewards.map((reward, index) => (
                    <Tag key={index} className="!bg-bg-base !border-border !text-text-secondary">
                      🎁 {reward}
                    </Tag>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 pt-2">
              {task.status === 'available' && (
                <Button type="primary" size="large" className="flex-1" icon={<CheckCircleOutlined />}>
                  接取任务
                </Button>
              )}
              {task.status === 'in_progress' && (
                <Button type="primary" ghost size="large" className="flex-1">
                  继续任务
                </Button>
              )}
              {task.status === 'completed' && (
                <Button size="large" className="flex-1" disabled icon={<CheckCircleOutlined />}>
                  已完成
                </Button>
              )}
              <Button
                icon={<ShareAltOutlined />}
                size="large"
                title="分享任务"
                className="!text-text-secondary hover:!text-primary hover:!border-primary"
              />
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <ChatPanel taskId={task.task_id} task={task} onOpenOnMap={handleOpenOnMap} />
        )}
      </div>
    </Drawer>
  );
};

export default TaskDrawer;