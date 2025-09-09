
import { Tag } from 'antd';
import {
  BankOutlined,
  BookOutlined,
  SmileOutlined,
  AppstoreOutlined,
  CheckCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';

/**
 * 根据任务分类获取对应的图标组件。
 * @param category - 任务分类字符串
 * @returns 返回一个 Ant Design 图标组件
 */
export const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'campus':
      return BankOutlined;
    case 'academic':
      return BookOutlined;
    case 'social':
      return SmileOutlined;
    default:
      return AppstoreOutlined;
  }
};

/**
 * 根据任务难度返回一个带有样式的 Ant Design 标签。
 * @param difficulty - 任务难度字符串 ('easy', 'medium', 'hard')
 * @returns 返回一个 React 元素 (Tag)
 */
export const getDifficultyTag = (difficulty: string) => {
  switch (difficulty) {
    case 'easy':
      return (
        <Tag 
          style={{ 
            backgroundColor: 'rgba(var(--color-success-rgb), 0.1)',
            borderColor: 'rgb(var(--color-success))',
            color: 'rgb(var(--color-success))'
          }}
        >
          简单
        </Tag>
      );
    case 'medium':
      return (
        <Tag 
          style={{ 
            backgroundColor: 'rgba(var(--color-warning-rgb), 0.1)',
            borderColor: 'rgb(var(--color-warning))',
            color: 'rgb(var(--color-warning))'
          }}
        >
          中等
        </Tag>
      );
    case 'hard':
      return (
        <Tag 
          style={{ 
            backgroundColor: 'rgba(var(--color-danger-rgb), 0.1)',
            borderColor: 'rgb(var(--color-danger))',
            color: 'rgb(var(--color-danger))'
          }}
        >
          困难
        </Tag>
      );
    default:
      return (
        <Tag 
          style={{ 
            backgroundColor: 'rgba(var(--color-text-secondary-rgb), 0.1)',
            borderColor: 'rgb(var(--color-border))',
            color: 'rgb(var(--color-text-secondary))'
          }}
        >
          {difficulty}
        </Tag>
      );
  }
};

/**
 * 根据任务状态返回一个带有图标和样式的 Ant Design 标签。
 * @param status - 任务状态字符串 ('available', 'in_progress', 'completed')
 * @returns 返回一个 React 元素 (Tag)
 */
export const getStatusTag = (status?: string) => {
  switch (status) {
    case 'available':
      return (
        <Tag icon={<CheckCircleOutlined />} color="success">
          可接取
        </Tag>
      );
    case 'in_progress':
      return (
        <Tag icon={<SyncOutlined spin />} color="processing">
          进行中
        </Tag>
      );
    case 'completed':
      return (
        <Tag icon={<CheckCircleOutlined />} color="default">
          已完成
        </Tag>
      );
    default:
      return <Tag>{status}</Tag>;
  }
};