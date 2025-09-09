import React, { useState, useMemo, useCallback } from 'react';
import { Row, Col, Statistic, Button, Space, message } from 'antd';
import NeonCard from '../components/common/NeonCard';
import { 
  EnvironmentOutlined, 
  UnorderedListOutlined,
  FullscreenOutlined,
  CloseOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import LeafletMap from '../components/Map/LeafletMap';
import MapLegend from '../components/Map/MapLegend';
import TaskFilters, { FilterState } from '../components/Filters/TaskFilters';
import TaskListView from '../components/TaskList/TaskListView';
import { seedTasks, TaskLocation } from '../data/seedTasks';
import { filterTasks, getUniqueValues, getAvailableCourses, debounceFilter } from '../utils/filterUtils';
import TaskDrawer from '../components/Task/TaskDrawer';

const MapPage: React.FC = () => {
  const [filters, setFilters] = useState<FilterState>({
    categories: [],
    difficulties: [],
    statuses: [],
    courses: [],
    timeRange: 'all',
    customDateRange: null,
    searchText: ''
  });
  
  const [selectedTask, setSelectedTask] = useState<TaskLocation | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [viewMode, setViewMode] = useState<'map' | 'list' | 'split'>('split');
  const [isFiltering, setIsFiltering] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);

  // Get unique values for filters
  const categories = useMemo(() => getUniqueValues(seedTasks, 'category'), []);
  const difficulties = useMemo(() => getUniqueValues(seedTasks, 'difficulty'), []);
  const statuses = useMemo(() => getUniqueValues(seedTasks, 'status'), []);
  const courses = useMemo(() => getAvailableCourses(seedTasks), []);

  // Debounced filter function for performance
  const debouncedFilter = useMemo(
    () => debounceFilter((newFilters: FilterState) => {
      setFilters(newFilters);
      setIsFiltering(false);
    }, 300),
    []
  );

  // Handle filter changes with debounce
  const handleFiltersChange = useCallback((newFilters: FilterState) => {
    setIsFiltering(true);
    debouncedFilter(newFilters);
  }, [debouncedFilter]);

  // Filter tasks based on current filters
  const filteredTasks = useMemo(() => {
    const startTime = performance.now();
    const result = filterTasks(seedTasks, filters);
    const endTime = performance.now();
    
    // Log performance for debugging
    if (endTime - startTime > 300) {
      console.warn(`Filter performance warning: ${(endTime - startTime).toFixed(2)}ms`);
    }
    
    return result;
  }, [filters]);

  // Statistics
  const stats = useMemo(() => {
    const total = filteredTasks.length;
    const available = filteredTasks.filter(t => t.status === 'available').length;
    const inProgress = filteredTasks.filter(t => t.status === 'in_progress').length;
    const completed = filteredTasks.filter(t => t.status === 'completed').length;
    
    return { total, available, inProgress, completed };
  }, [filteredTasks]);

  const handleTaskSelect = useCallback((task: TaskLocation) => {
    setSelectedTask(task);
    setDrawerOpen(true);
    setDrawerVisible(true);
  }, []);

  const handleDrawerClose = useCallback(() => {
    setDrawerOpen(false);
    setDrawerVisible(false);
  }, []);

  const toggleDrawer = useCallback(() => {
    if (selectedTask) {
      setDrawerVisible(!drawerVisible);
      setDrawerOpen(!drawerOpen);
    }
  }, [selectedTask, drawerVisible, drawerOpen]);

  const handleTaskAction = useCallback((task: TaskLocation, action: 'view' | 'start') => {
    if (action === 'view') {
      setSelectedTask(task);
      message.info(`查看任务: ${task.title}`);
    } else if (action === 'start') {
      message.success(`开始任务: ${task.title}`);
    }
  }, []);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const mapHeight = isFullscreen ? '80vh' : '500px';

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4 flex items-center justify-center gap-2 text-primary">
          <EnvironmentOutlined className="text-secondary" />
          校园任务地图
        </h1>
        <p className="text-text-secondary">探索 CityU 校园，发现精彩任务</p>
      </div>

      {/* Statistics */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={12} sm={6}>
          <NeonCard>
            <Statistic
              title={<span className="text-text-secondary">总任务</span>}
              value={stats.total}
              prefix={<EnvironmentOutlined className="text-primary" />}
              valueStyle={{ color: 'rgb(var(--color-primary))', fontWeight: 600 }}
              loading={isFiltering}
            />
          </NeonCard>
        </Col>
        <Col xs={12} sm={6}>
          <NeonCard>
            <Statistic
              title={<span className="text-text-secondary">可接取</span>}
              value={stats.available}
              valueStyle={{ color: 'rgb(var(--color-success))', fontWeight: 600 }}
              loading={isFiltering}
            />
          </NeonCard>
        </Col>
        <Col xs={12} sm={6}>
          <NeonCard>
            <Statistic
              title={<span className="text-text-secondary">进行中</span>}
              value={stats.inProgress}
              valueStyle={{ color: 'rgb(var(--color-warning))', fontWeight: 600 }}
              loading={isFiltering}
            />
          </NeonCard>
        </Col>
        <Col xs={12} sm={6}>
          <NeonCard>
            <Statistic
              title={<span className="text-text-secondary">已完成</span>}
              value={stats.completed}
              valueStyle={{ color: 'rgb(var(--color-info))', fontWeight: 600 }}
              loading={isFiltering}
            />
          </NeonCard>
        </Col>
      </Row>

      {/* Filters */}
      <TaskFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        availableCategories={categories}
        availableDifficulties={difficulties}
        availableStatuses={statuses}
        availableCourses={courses}
        loading={isFiltering}
      />

      {/* View Mode Controls */}
      <div className="mb-6 flex justify-between items-center">
        <Space>
          <Button
            className={`view-toggle-btn ${viewMode === 'map' ? 'view-toggle-selected' : ''}`}
            icon={<EnvironmentOutlined />}
            onClick={() => setViewMode('map')}
          >
            地图视图
          </Button>
          <Button
            className={`view-toggle-btn ${viewMode === 'list' ? 'view-toggle-selected' : ''}`}
            icon={<UnorderedListOutlined />}
            onClick={() => setViewMode('list')}
          >
            列表视图
          </Button>
          <Button
            className={`view-toggle-btn ${viewMode === 'split' ? 'view-toggle-selected' : ''}`}
            onClick={() => setViewMode('split')}
          >
            分屏视图
          </Button>
        </Space>
        
        <Space>
          {selectedTask && (
            <Button
              type={drawerVisible ? 'primary' : 'default'}
              icon={drawerVisible ? <CloseOutlined /> : <InfoCircleOutlined />}
              onClick={toggleDrawer}
              className="drawer-toggle-btn"
            >
              {drawerVisible ? '关闭详情' : '任务详情'}
            </Button>
          )}
          <Button 
            icon={<FullscreenOutlined />} 
            onClick={toggleFullscreen}
          >
            {isFullscreen ? '退出全屏' : '全屏显示'}
          </Button>
        </Space>
      </div>

      {/* Content Area */}
      <Row gutter={[16, 16]}>
        {(viewMode === 'map' || viewMode === 'split') && (
          <Col xs={24} lg={viewMode === 'split' ? 12 : 24} className="relative">
            <LeafletMap
              tasks={filteredTasks}
              onTaskSelect={handleTaskSelect}
              height={mapHeight}
              enableClustering={filteredTasks.length > 50}
            />
            <MapLegend className="hidden md:block" />
          </Col>
        )}
        
        {(viewMode === 'list' || viewMode === 'split') && (
          <Col xs={24} lg={viewMode === 'split' ? 12 : 24}>
            <NeonCard className="p-2">
              <TaskListView
                tasks={filteredTasks}
                loading={isFiltering}
                onTaskSelect={handleTaskSelect}
                onTaskAction={handleTaskAction}
                selectedTaskId={selectedTask?.task_id}
              />
            </NeonCard>
          </Col>
        )}
      </Row>

      {/* Enhanced Task Drawer with Split View Support */}
      <TaskDrawer
        task={selectedTask}
        open={drawerOpen}
        onClose={handleDrawerClose}
        onOpenOnMap={(task) => {
          setSelectedTask(task);
          setViewMode('map');
          setDrawerVisible(false);
          setDrawerOpen(false);
          // Focus map on the task location
        }}
        mask={viewMode !== 'split'}
        maskClosable={viewMode !== 'split'}
        keyboard={true}
        destroyOnClose={false}
        forceRender={true}
        getContainer={false}
        style={{
          position: viewMode === 'split' ? 'absolute' : 'fixed',
          zIndex: viewMode === 'split' ? 'var(--z-drawer)' : 'var(--z-drawer-mask)'
        }}
      />
    </div>
  );
};

export default MapPage;