import React, { useState, useEffect } from 'react';
import { CaretLeftOutlined, CaretRightOutlined } from '@ant-design/icons';
import NeonCard from '../common/NeonCard';
import { getCategoryColor } from '../../data/seedTasks';

interface MapLegendProps {
  className?: string;
}

const LEGEND_COLLAPSED_KEY = 'map-legend-collapsed';

const MapLegend: React.FC<MapLegendProps> = ({ className = '' }) => {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    try {
      return localStorage.getItem(LEGEND_COLLAPSED_KEY) === 'true';
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(LEGEND_COLLAPSED_KEY, String(isCollapsed));
    } catch (e) {
      console.warn('Failed to save legend state to localStorage', e);
    }
  }, [isCollapsed]);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const categories = [
    { key: 'academic', label: '学术任务', color: getCategoryColor('academic') },
    { key: 'social', label: '社交任务', color: getCategoryColor('social') },
    { key: 'campus', label: '校园任务', color: getCategoryColor('campus') }
  ];
  const difficulties = [
    { key: 'easy', label: '简单', icon: '⭐' },
    { key: 'medium', label: '中等', icon: '⭐⭐' },
    { key: 'hard', label: '困难', icon: '⭐⭐⭐' }
  ];
  const statuses = [
    { key: 'available', label: '可接取', icon: '🎯' },
    { key: 'in_progress', label: '进行中', icon: '⏳' },
    { key: 'completed', label: '已完成', icon: '✅' }
  ];

  return (
    <div className={`absolute top-4 right-4 ${className}`} style={{ zIndex: 'var(--z-map-overlay)' }}>
      {/* Expanded Card */}
      <div
        className={`transition-all duration-200 ease-in-out ${
          isCollapsed ? 'opacity-0 translate-x-8 pointer-events-none' : 'opacity-100 translate-x-0'
        }`}
        aria-hidden={isCollapsed}
      >
        <NeonCard className="w-64">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-text-primary font-bold text-base">图例说明</h3>
            <button
              onClick={toggleCollapse}
              className="text-text-secondary hover:text-primary transition-colors"
              aria-label="折叠图例"
            >
              <CaretRightOutlined />
            </button>
          </div>
          <div className="space-y-3 text-xs text-text-secondary">
            <div>
              <div className="font-medium mb-1 text-text-primary">任务类别</div>
              {categories.map(c => (
                <div key={c.key} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full border border-bg-secondary" style={{ backgroundColor: c.color }} />
                  <span>{c.label}</span>
                </div>
              ))}
            </div>
            <div>
              <div className="font-medium mb-1 text-text-primary">难度等级</div>
              {difficulties.map(d => (
                <div key={d.key} className="flex items-center gap-2">
                  <span className="w-4 text-center">{d.icon.charAt(0)}</span>
                  <span>{d.label}</span>
                </div>
              ))}
            </div>
            <div>
              <div className="font-medium mb-1 text-text-primary">任务状态</div>
              {statuses.map(s => (
                <div key={s.key} className="flex items-center gap-2">
                  <span className="w-4 text-center">{s.icon}</span>
                  <span>{s.label}</span>
                </div>
              ))}
            </div>
          </div>
        </NeonCard>
      </div>

      {/* Collapsed Strip */}
      <div
        className={`absolute top-1/2 -translate-y-1/2 -right-4 w-8 h-24 flex items-center justify-center transition-opacity duration-200 ease-in-out ${
          isCollapsed ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        aria-hidden={!isCollapsed}
      >
        <button
          onClick={toggleCollapse}
          aria-label="展开图例"
          className="relative w-full h-full group"
        >
          <div
            className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-[5px] rounded-full opacity-90 transition-all duration-200 ease-in-out group-hover:opacity-100"
            style={{
              backgroundColor: 'var(--legend-strip-color)',
              boxShadow: '0 0 12px var(--legend-strip-glow)',
            }}
          />
          <div className="absolute inset-0 flex items-center justify-center text-bg-primary opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <CaretLeftOutlined />
          </div>
        </button>
      </div>
    </div>
  );
};

export default MapLegend;