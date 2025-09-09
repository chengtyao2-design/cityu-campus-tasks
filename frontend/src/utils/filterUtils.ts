import dayjs from 'dayjs';
import isBetween from 'dayjs/plugin/isBetween';
import { TaskLocation } from '../data/seedTasks';
import { FilterState } from '../components/Filters/TaskFilters';

dayjs.extend(isBetween);

export const filterTasks = (tasks: TaskLocation[], filters: FilterState): TaskLocation[] => {
  return tasks.filter(task => {
    // Category filter
    if (filters.categories.length > 0 && !filters.categories.includes(task.category)) {
      return false;
    }

    // Difficulty filter
    if (filters.difficulties.length > 0 && !filters.difficulties.includes(task.difficulty)) {
      return false;
    }

    // Status filter
    if (filters.statuses.length > 0 && !filters.statuses.includes(task.status)) {
      return false;
    }

    // Course filter
    if (filters.courses.length > 0 && task.course && !filters.courses.includes(task.course)) {
      return false;
    }

    // Search text filter
    if (filters.searchText) {
      const searchLower = filters.searchText.toLowerCase();
      const matchesTitle = task.title.toLowerCase().includes(searchLower);
      const matchesDescription = task.description.toLowerCase().includes(searchLower);
      const matchesLocation = task.location.name.toLowerCase().includes(searchLower);
      const matchesCourse = task.course?.toLowerCase().includes(searchLower) || false;
      
      if (!matchesTitle && !matchesDescription && !matchesLocation && !matchesCourse) {
        return false;
      }
    }

    // Time range filter
    if (filters.timeRange !== 'all' && task.createdAt) {
      const taskDate = dayjs(task.createdAt);
      const now = dayjs();

      switch (filters.timeRange) {
        case 'today':
          if (!taskDate.isSame(now, 'day')) {
            return false;
          }
          break;
        case 'this-week':
          if (!taskDate.isSame(now, 'week')) {
            return false;
          }
          break;
        case 'custom':
          if (filters.customDateRange) {
            const [start, end] = filters.customDateRange;
            if (!taskDate.isBetween(start, end, 'day', '[]')) {
              return false;
            }
          }
          break;
      }
    }

    return true;
  });
};

export const getUniqueValues = (
  tasks: TaskLocation[], 
  field: 'category' | 'difficulty' | 'status'
): string[] => {
  const values = tasks
    .map(task => task[field])
    .filter(value => typeof value === 'string' && value.length > 0) as string[];
  
  return [...new Set(values)].sort();
};

export const getAvailableCourses = (tasks: TaskLocation[]): string[] => {
  const courses = tasks
    .map(task => task.course)
    .filter((course): course is string => typeof course === 'string' && course.length > 0);
  
  return [...new Set(courses)].sort();
};

export const debounceFilter = <T extends any[]>(
  fn: (...args: T) => void,
  delay: number = 300
): ((...args: T) => void) => {
  let timeoutId: number;
  
  return (...args: T) => {
    clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => fn(...args), delay);
  };
};