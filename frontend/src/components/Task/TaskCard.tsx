import React from 'react';
import { List, Tag } from 'antd';
import { CheckCircleOutlined, UserOutlined, FireOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';

interface Task {
  task_id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
}

interface TaskCardProps {
  task: Task;
}

const getDifficultyTagClass = (difficulty: string) => {
  switch (difficulty.toLowerCase()) {
    case 'easy': return 'bg-success/10 text-success border-success/20';
    case 'medium': return 'bg-warning/10 text-warning border-warning/20';
    case 'hard': return 'bg-danger/10 text-danger border-danger/20';
    default: return 'bg-info/10 text-info border-info/20';
  }
};

const getCategoryIcon = (category: string) => {
  switch (category.toLowerCase()) {
    case 'academic': return <CheckCircleOutlined />;
    case 'social': return <UserOutlined />;
    case 'campus': return <FireOutlined />;
    default: return <ClockCircleOutlined />;
  }
};

const TaskCard: React.FC<TaskCardProps> = ({ task }) => {
  return (
    <List.Item className="task-card-item">
      <div className="task-card-inner group">
        <div className="flex-grow">
          <List.Item.Meta
            avatar={<div className="text-lg text-text-secondary pt-1">{getCategoryIcon(task.category)}</div>}
            title={<span className="font-medium text-text-primary group-hover:text-primary transition-colors">{task.title}</span>}
            description={
              <div className="text-sm text-text-secondary">
                <p className="mb-2">{task.description}</p>
                <Tag className="bg-bg-tertiary text-text-secondary border-border">{task.category}</Tag>
              </div>
            }
          />
        </div>
        <div className="flex flex-col items-end justify-center gap-2 pl-4">
          <Tag key="difficulty" className={`font-medium border ${getDifficultyTagClass(task.difficulty)}`}>
            {task.difficulty}
          </Tag>
          <Link to={`/task/${task.task_id}`} className="text-sm text-primary hover:text-primary/80">
            查看详情
          </Link>
        </div>
      </div>
    </List.Item>
  );
};

export default TaskCard;