import React from 'react';
import { Card, Select, Checkbox, DatePicker, Row, Col, Button, Space, Form } from 'antd';
import { FilterOutlined, ReloadOutlined, CalendarOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;

export interface FilterState {
  categories: string[];
  difficulties: string[];
  statuses: string[];
  courses: string[];
  timeRange: 'all' | 'today' | 'this-week' | 'custom';
  customDateRange?: [dayjs.Dayjs, dayjs.Dayjs] | null;
  searchText: string;
}

interface TaskFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  availableCategories: string[];
  availableDifficulties: string[];
  availableStatuses: string[];
  availableCourses: string[];
  loading?: boolean;
}

const TaskFilters: React.FC<TaskFiltersProps> = ({
  filters,
  onFiltersChange,
  availableCategories,
  availableDifficulties,
  availableStatuses,
  availableCourses,
  loading = false
}) => {
  const [form] = Form.useForm();

  const handleFilterChange = (key: keyof FilterState, value: any) => {
    const newFilters = { ...filters, [key]: value };
    onFiltersChange(newFilters);
  };

  const handleReset = () => {
    const resetFilters: FilterState = {
      categories: [],
      difficulties: [],
      statuses: [],
      courses: [],
      timeRange: 'all',
      customDateRange: null,
      searchText: ''
    };
    onFiltersChange(resetFilters);
    form.resetFields();
  };

  const getTimeRangeOptions = () => [
    { label: '全部时间', value: 'all' },
    { label: '今天', value: 'today' },
    { label: '本周', value: 'this-week' },
    { label: '自定义', value: 'custom' }
  ];

  const getCategoryColor = (category: string) => {
    // This can be simplified if you have a centralized color mapping
    const colors: { [key: string]: string } = {
      academic: 'blue',
      social: 'purple',
      campus: 'teal',
    };
    return colors[category] || 'gray';
  };

  return (
    <Card 
      title={
        <Space className="text-text-primary">
          <FilterOutlined />
          <span>任务筛选</span>
        </Space>
      }
      extra={
        <Button 
          icon={<ReloadOutlined />} 
          onClick={handleReset}
          size="small"
          loading={loading}
        >
          重置
        </Button>
      }
      className="mb-6 bg-bg-secondary border-border"
    >
      <Form form={form} layout="vertical">
        <Row gutter={[16, 16]}>
          {/* Time Range Filter */}
          <Col xs={24} sm={12} md={6}>
            <Form.Item label={<span className="text-text-secondary">时间范围</span>} className="mb-4">
              <Select
                value={filters.timeRange}
                onChange={(value) => handleFilterChange('timeRange', value)}
                placeholder="选择时间范围"
                suffixIcon={<CalendarOutlined />}
              >
                {getTimeRangeOptions().map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
              
              {filters.timeRange === 'custom' && (
                <RangePicker
                  className="mt-2 w-full"
                  value={filters.customDateRange}
                  onChange={(dates) => handleFilterChange('customDateRange', dates)}
                  placeholder={['开始日期', '结束日期']}
                />
              )}
            </Form.Item>
          </Col>

          {/* Category Filter */}
          <Col xs={24} sm={12} md={6}>
            <Form.Item label={<span className="text-text-secondary">任务类别</span>} className="mb-4">
              <Checkbox.Group
                value={filters.categories}
                onChange={(values) => handleFilterChange('categories', values)}
                className="w-full"
              >
                <div className="space-y-2 text-text-primary">
                  {availableCategories.map(category => (
                    <div key={category} className="flex items-center">
                      <Checkbox value={category} className="mr-2">
                        <div className="flex items-center gap-2">
                          <div 
                            className={`w-3 h-3 rounded-full bg-${getCategoryColor(category)}-500`}
                          />
                          <span className="capitalize">{category}</span>
                        </div>
                      </Checkbox>
                    </div>
                  ))}
                </div>
              </Checkbox.Group>
            </Form.Item>
          </Col>

          {/* Difficulty Filter */}
          <Col xs={24} sm={12} md={6}>
            <Form.Item label={<span className="text-text-secondary">难度等级</span>} className="mb-4">
              <Checkbox.Group
                value={filters.difficulties}
                onChange={(values) => handleFilterChange('difficulties', values)}
                className="w-full"
              >
                <div className="space-y-2 text-text-primary">
                  {availableDifficulties.map(difficulty => (
                    <div key={difficulty} className="flex items-center">
                      <Checkbox value={difficulty}>
                        <span>
                          {difficulty === 'easy' && '⭐ 简单'}
                          {difficulty === 'medium' && '⭐⭐ 中等'}
                          {difficulty === 'hard' && '⭐⭐⭐ 困难'}
                        </span>
                      </Checkbox>
                    </div>
                  ))}
                </div>
              </Checkbox.Group>
            </Form.Item>
          </Col>

          {/* Status Filter */}
          <Col xs={24} sm={12} md={6}>
            <Form.Item label={<span className="text-text-secondary">任务状态</span>} className="mb-4">
              <Checkbox.Group
                value={filters.statuses}
                onChange={(values) => handleFilterChange('statuses', values)}
                className="w-full"
              >
                <div className="space-y-2 text-text-primary">
                  {availableStatuses.map(status => (
                    <div key={status} className="flex items-center">
                      <Checkbox value={status}>
                        <span>
                          {status === 'available' && '🎯 可接取'}
                          {status === 'in_progress' && '⏳ 进行中'}
                          {status === 'completed' && '✅ 已完成'}
                        </span>
                      </Checkbox>
                    </div>
                  ))}
                </div>
              </Checkbox.Group>
            </Form.Item>
          </Col>
        </Row>

        {/* Course Filter - Full Width */}
        <Row>
          <Col span={24}>
            <Form.Item label={<span className="text-text-secondary">相关课程</span>} className="mb-0">
              <Select
                mode="multiple"
                value={filters.courses}
                onChange={(values) => handleFilterChange('courses', values)}
                placeholder="选择相关课程"
                className="w-full"
                maxTagCount="responsive"
              >
                {availableCourses.map(course => (
                  <Option key={course} value={course}>
                    {course}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Card>
  );
};

export default TaskFilters;