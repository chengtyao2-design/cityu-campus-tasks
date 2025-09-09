import React, { useState, useEffect } from 'react';
import { Card, List, Tag, Input, Select, Row, Col, Spin, Empty } from 'antd';
import { SearchOutlined, FilterOutlined } from '@ant-design/icons';

const { Search } = Input;
const { Option } = Select;

interface Task {
  task_id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  status?: string;
}

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [difficultyFilter, setDifficultyFilter] = useState<string>('all');

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await fetch('http://localhost:8000/tasks', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (response.ok) {
          const data = await response.json();
          setTasks(data.data || []);
          setFilteredTasks(data.data || []);
        } else {
          // 使用模拟数据
          const mockTasks = getMockTasks();
          setTasks(mockTasks);
          setFilteredTasks(mockTasks);
        }
      } catch (error) {
        // 静默处理错误，使用模拟数据
        const mockTasks = getMockTasks();
        setTasks(mockTasks);
        setFilteredTasks(mockTasks);
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(fetchTasks, 300);
    return () => clearTimeout(timer);
  }, []);

  // 模拟任务数据
  const getMockTasks = (): Task[] => [
    {
      task_id: 'demo-001',
      title: '参观图书馆',
      description: '熟悉图书馆的各个区域和借阅流程，了解学习资源的分布',
      category: 'campus',
      difficulty: 'easy',
      status: 'available'
    },
    {
      task_id: 'demo-002', 
      title: '加入学生社团',
      description: '选择一个感兴趣的社团并参加活动，扩展社交圈子',
      category: 'social',
      difficulty: 'medium',
      status: 'available'
    },
    {
      task_id: 'demo-003',
      title: '完成第一次作业',
      description: '按时提交高质量的课程作业，展示学习成果',
      category: 'academic',
      difficulty: 'medium',
      status: 'in_progress'
    },
    {
      task_id: 'demo-004',
      title: '参加学术讲座',
      description: '参加至少3场学术讲座并撰写心得体会',
      category: 'academic', 
      difficulty: 'hard',
      status: 'available'
    },
    {
      task_id: 'demo-005',
      title: '校园导览',
      description: '探索校园的每个角落，了解各个建筑的功能和历史',
      category: 'campus',
      difficulty: 'easy',
      status: 'completed'
    },
    {
      task_id: 'demo-006',
      title: '组织学习小组',
      description: '与同学组建学习小组，共同提高学习效率',
      category: 'social',
      difficulty: 'medium',
      status: 'available'
    },
    {
      task_id: 'demo-007',
      title: '参与志愿服务',
      description: '参加校内外的志愿服务活动，培养社会责任感',
      category: 'social',
      difficulty: 'hard',
      status: 'available'
    },
    {
      task_id: 'demo-008',
      title: '探索实验室',
      description: '参观各个学院的实验室，了解科研设备和项目',
      category: 'academic',
      difficulty: 'medium',
      status: 'available'
    }
  ];

  useEffect(() => {
    let filtered = tasks;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(task =>
        task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(task => task.category === categoryFilter);
    }

    // Difficulty filter
    if (difficultyFilter !== 'all') {
      filtered = filtered.filter(task => task.difficulty === difficultyFilter);
    }

    setFilteredTasks(filtered);
  }, [tasks, searchTerm, categoryFilter, difficultyFilter]);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'green';
      case 'medium': return 'orange';
      case 'hard': return 'red';
      default: return 'blue';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'academic': return 'blue';
      case 'social': return 'purple';
      case 'campus': return 'cyan';
      default: return 'default';
    }
  };

  const categories = [...new Set(tasks.map(task => task.category))];
  const difficulties = [...new Set(tasks.map(task => task.difficulty))];

  if (loading) {
    return (
      <div className="text-center py-12">
        <Spin size="large" />
        <p className="mt-4 text-gray-500">加载任务中...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">任务中心</h1>
        <p className="text-gray-600">探索校园任务，完成挑战，获得成长</p>
      </div>

      <Card className="mb-6">
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} md={12}>
            <Search
              placeholder="搜索任务标题或描述..."
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              onSearch={setSearchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Col>
          <Col xs={12} md={6}>
            <Select
              placeholder="选择类别"
              size="large"
              style={{ width: '100%' }}
              value={categoryFilter}
              onChange={setCategoryFilter}
              suffixIcon={<FilterOutlined />}
            >
              <Option value="all">全部类别</Option>
              {categories.map(category => (
                <Option key={category} value={category}>{category}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={12} md={6}>
            <Select
              placeholder="选择难度"
              size="large"
              style={{ width: '100%' }}
              value={difficultyFilter}
              onChange={setDifficultyFilter}
              suffixIcon={<FilterOutlined />}
            >
              <Option value="all">全部难度</Option>
              {difficulties.map(difficulty => (
                <Option key={difficulty} value={difficulty}>{difficulty}</Option>
              ))}
            </Select>
          </Col>
        </Row>
      </Card>

      <div className="mb-4 text-sm text-gray-600">
        找到 {filteredTasks.length} 个任务
      </div>

      {filteredTasks.length === 0 ? (
        <Card>
          <Empty
            description="没有找到匹配的任务"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </Card>
      ) : (
        <List
          grid={{
            gutter: 16,
            xs: 1,
            sm: 1,
            md: 2,
            lg: 2,
            xl: 3,
            xxl: 3,
          }}
          dataSource={filteredTasks}
          renderItem={(task) => (
            <List.Item>
              <Card
                hoverable
                className="h-full"
                actions={[
                  <span key="start">开始任务</span>,
                  <span key="details">查看详情</span>,
                ]}
              >
                <Card.Meta
                  title={
                    <div className="flex items-start justify-between">
                      <span className="font-medium text-gray-800 flex-1 mr-2">
                        {task.title}
                      </span>
                      <Tag color={getDifficultyColor(task.difficulty)} className="ml-auto">
                        {task.difficulty}
                      </Tag>
                    </div>
                  }
                  description={
                    <div className="space-y-3">
                      <p className="text-gray-600 text-sm line-clamp-3">
                        {task.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <Tag color={getCategoryColor(task.category)}>
                          {task.category}
                        </Tag>
                        <span className="text-xs text-gray-400">
                          ID: {task.task_id}
                        </span>
                      </div>
                    </div>
                  }
                />
              </Card>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default TasksPage;