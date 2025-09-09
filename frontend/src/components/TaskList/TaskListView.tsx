import React from 'react';
import { List, Tag, Button, Empty, Spin, Avatar } from 'antd';
import { 
  EnvironmentOutlined, 
  ClockCircleOutlined, 
  GiftOutlined,
  EyeOutlined,
  PlayCircleOutlined 
} from '@ant-design/icons';
import { TaskLocation, getCategoryColor } from '../../data/seedTasks';

interface TaskListViewProps {
  tasks: TaskLocation[];
  loading?: boolean;
  onTaskSelect?: (task: TaskLocation) => void;
  onTaskAction?: (task: TaskLocation, action: 'view' | 'start') => void;
  selectedTaskId?: string;
}

const TaskListView: React.FC<TaskListViewProps> = ({
  tasks,
  loading = false,
  onTaskSelect,
  onTaskAction,
  selectedTaskId
}) => {
  const getDifficultyTag = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return <Tag color="green">⭐ 简单</Tag>;
      case 'medium': return <Tag color="gold">⭐⭐ 中等</Tag>;
      case 'hard': return <Tag color="red">⭐⭐⭐ 困难</Tag>;
      default: return <Tag>{difficulty}</Tag>;
    }
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'available': return <Tag color="success">🎯 可接取</Tag>;
      case 'in_progress': return <Tag color="processing">⏳ 进行中</Tag>;
      case 'completed': return <Tag color="default">✅ 已完成</Tag>;
      default: return <Tag>{status}</Tag>;
    }
  };

  const handleTaskClick = (task: TaskLocation) => {
    if (onTaskSelect) {
      onTaskSelect(task);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-text-secondary bg-bg-secondary p-4 rounded-lg">
        <Spin size="large" />
        <span className="ml-3">加载任务列表中...</span>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="bg-bg-secondary p-4 rounded-lg">
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <div className="text-center">
              <div className="text-text-secondary mb-2">没有找到匹配的任务</div>
              <div className="text-sm text-text-muted">
                尝试调整筛选条件或重置所有筛选器
              </div>
            </div>
          }
        />
      </div>
    );
  }

  return (
    <div className="bg-bg-secondary rounded-lg h-full">
      <List
        itemLayout="vertical"
        size="small"
        dataSource={tasks}
        header={<div className="text-text-primary px-4 pt-2 font-semibold">{`任务列表 (${tasks.length})`}</div>}
        pagination={{
          pageSize: 5,
          size: 'small',
          showSizeChanger: false,
          showQuickJumper: true,
          showTotal: (total, range) => 
            <span className="text-text-muted">{`第 ${range[0]}-${range[1]} 项，共 ${total} 个任务`}</span>
        }}
        renderItem={(task) => {
          const isSelected = selectedTaskId === task.task_id;

          return (
            <List.Item
              key={task.task_id}
              className={`cursor-pointer transition-all duration-300 rounded-lg p-3 m-2 border ${
                isSelected 
                  ? 'bg-bg-tertiary border-primary' 
                  : 'border-border hover:bg-bg-tertiary'
              }`}
              onClick={() => handleTaskClick(task)}
              actions={[
                <Button
                  key="view"
                  type="text"
                  size="small"
                  className="text-text-secondary hover:text-primary"
                  icon={<EyeOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    onTaskAction?.(task, 'view');
                  }}
                >
                  查看
                </Button>,
                <Button
                  key="start"
                  type={task.status === 'available' ? 'primary' : 'default'}
                  size="small"
                  icon={<PlayCircleOutlined />}
                  disabled={task.status === 'completed'}
                  onClick={(e) => {
                    e.stopPropagation();
                    onTaskAction?.(task, 'start');
                  }}
                >
                  {task.status === 'available' && '开始'}
                  {task.status === 'in_progress' && '继续'}
                  {task.status === 'completed' && '已完成'}
                </Button>
              ]}
            >
              <List.Item.Meta
                avatar={
                  <Avatar
                    style={{ backgroundColor: getCategoryColor(task.category) }}
                    size="large"
                    className="text-white"
                  >
                    {task.category === 'academic' && '📚'}
                    {task.category === 'social' && '👥'}
                    {task.category === 'campus' && '🏫'}
                  </Avatar>
                }
                title={
                  <div className="flex items-center justify-between">
                    <span className={`font-medium ${isSelected ? 'text-primary' : 'text-text-primary'}`}>
                      {task.title}
                    </span>
                    <div className="flex gap-1">
                      <Tag color={getCategoryColor(task.category)}>
                        {task.category}
                      </Tag>
                      {getDifficultyTag(task.difficulty)}
                      {getStatusTag(task.status)}
                    </div>
                  </div>
                }
                description={
                  <div className="space-y-2">
                    <p className="text-text-secondary text-sm line-clamp-2">
                      {task.description}
                    </p>
                    
                    <div className="flex items-center gap-4 text-xs text-text-muted">
                      <div className="flex items-center gap-1">
                        <EnvironmentOutlined />
                        <span>{task.location.name}</span>
                      </div>
                      
                      {task.estimatedTime && (
                        <div className="flex items-center gap-1">
                          <ClockCircleOutlined />
                          <span>{task.estimatedTime} 分钟</span>
                        </div>
                      )}
                      
                      {task.rewards && task.rewards.length > 0 && (
                        <div className="flex items-center gap-1">
                          <GiftOutlined />
                          <span>{task.rewards.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                }
              />
            </List.Item>
          );
        }}
      />
    </div>
  );
};

export default TaskListView;