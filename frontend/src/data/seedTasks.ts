export interface TaskLocation {
  task_id: string;
  title: string;
  description: string;
  category: 'academic' | 'social' | 'campus';
  difficulty: 'easy' | 'medium' | 'hard';
  status: 'available' | 'in_progress' | 'completed';
  location: {
    lat: number;
    lng: number;
    name: string;
  };
  rewards?: string[];
  estimatedTime?: number; // minutes
  course?: string; // Related course
  dueDate?: string; // ISO date string
  createdAt?: string; // ISO date string
  created_at?: string; // Alias for createdAt
  due_date?: string; // Alias for dueDate
}

// CityU Hong Kong campus coordinates (approximate)
export const CITYU_CENTER = { lat: 22.3364, lng: 114.2734 };

export const seedTasks: TaskLocation[] = [
  // Academic Building tasks
  {
    task_id: 'ac-001',
    title: '参观学术楼一',
    description: '探索学术楼一的各个教室和实验室，了解教学设施',
    category: 'academic',
    difficulty: 'easy',
    status: 'available',
    location: { lat: 22.3370, lng: 114.2740, name: '学术楼一' },
    rewards: ['探索徽章', '10积分'],
    estimatedTime: 30,
    course: '大学导论',
    dueDate: '2025-09-15T23:59:59.000Z',
    createdAt: '2025-09-09T04:00:00.000Z'
  },
  {
    task_id: 'ac-002',
    title: '计算机科学系实验室参观',
    description: '参观计算机科学系的先进实验室，了解最新科研设备',
    category: 'academic',
    difficulty: 'medium',
    status: 'available',
    location: { lat: 22.3375, lng: 114.2745, name: '计算机科学系' },
    rewards: ['科技徽章', '20积分'],
    estimatedTime: 45,
    course: '计算机科学导论',
    dueDate: '2025-09-12T23:59:59.000Z',
    createdAt: '2025-09-09T04:00:00.000Z'
  },
  {
    task_id: 'ac-003',
    title: '参加学术讲座',
    description: '参加在学术楼举办的学术讲座，拓展知识视野',
    category: 'academic',
    difficulty: 'hard',
    status: 'in_progress',
    location: { lat: 22.3368, lng: 114.2738, name: '学术楼二' },
    rewards: ['学者徽章', '50积分'],
    estimatedTime: 90,
    course: '学术研究方法',
    dueDate: '2025-09-10T18:00:00.000Z',
    createdAt: '2025-09-08T04:00:00.000Z'
  },

  // Library tasks
  {
    task_id: 'lib-001',
    title: '图书馆导览',
    description: '熟悉图书馆的各个区域和借阅流程',
    category: 'campus',
    difficulty: 'easy',
    status: 'completed',
    location: { lat: 22.3360, lng: 114.2730, name: '邵逸夫图书馆' },
    rewards: ['读者徽章', '15积分'],
    estimatedTime: 40,
    course: '信息素养',
    dueDate: '2025-09-08T23:59:59.000Z',
    createdAt: '2025-09-07T04:00:00.000Z'
  },
  {
    task_id: 'lib-002',
    title: '数字资源培训',
    description: '学习使用图书馆的数字资源和数据库',
    category: 'academic',
    difficulty: 'medium',
    status: 'available',
    location: { lat: 22.3362, lng: 114.2732, name: '图书馆培训室' },
    rewards: ['数字徽章', '25积分'],
    estimatedTime: 60,
    course: '信息检索',
    dueDate: '2025-09-16T23:59:59.000Z',
    createdAt: '2025-09-09T04:00:00.000Z'
  },

  // Student Center tasks
  {
    task_id: 'sc-001',
    title: '学生会注册',
    description: '在学生中心完成学生会注册，参与校园活动',
    category: 'social',
    difficulty: 'easy',
    status: 'available',
    location: { lat: 22.3355, lng: 114.2725, name: '学生中心' },
    rewards: ['社交徽章', '10积分'],
    estimatedTime: 20,
    course: '学生发展',
    dueDate: '2025-09-20T23:59:59.000Z',
    createdAt: '2025-09-09T04:00:00.000Z'
  },
  {
    task_id: 'sc-002',
    title: '加入学生社团',
    description: '选择并加入一个感兴趣的学生社团',
    category: 'social',
    difficulty: 'medium',
    status: 'available',
    location: { lat: 22.3357, lng: 114.2727, name: '社团活动室' },
    rewards: ['团队徽章', '30积分'],
    estimatedTime: 45
  },
  {
    task_id: 'sc-003',
    title: '组织社团活动',
    description: '策划并组织一次社团活动，锻炼领导能力',
    category: 'social',
    difficulty: 'hard',
    status: 'available',
    location: { lat: 22.3359, lng: 114.2729, name: '多功能厅' },
    rewards: ['领导徽章', '60积分'],
    estimatedTime: 120
  },

  // Sports Complex tasks
  {
    task_id: 'sp-001',
    title: '体育馆参观',
    description: '参观体育馆的各项运动设施',
    category: 'campus',
    difficulty: 'easy',
    status: 'available',
    location: { lat: 22.3350, lng: 114.2720, name: '体育馆' },
    rewards: ['运动徽章', '10积分'],
    estimatedTime: 30
  },
  {
    task_id: 'sp-002',
    title: '参加体育课程',
    description: '报名并参加一门体育课程',
    category: 'social',
    difficulty: 'medium',
    status: 'available',
    location: { lat: 22.3352, lng: 114.2722, name: '运动场' },
    rewards: ['健康徽章', '25积分'],
    estimatedTime: 90
  },

  // Dining Hall tasks
  {
    task_id: 'dh-001',
    title: '食堂美食探索',
    description: '尝试食堂的各种美食，体验校园饮食文化',
    category: 'campus',
    difficulty: 'easy',
    status: 'available',
    location: { lat: 22.3345, lng: 114.2715, name: '学生食堂' },
    rewards: ['美食徽章', '15积分'],
    estimatedTime: 45
  },

  // Residence Hall tasks
  {
    task_id: 'rh-001',
    title: '宿舍生活适应',
    description: '熟悉宿舍环境，建立良好的宿舍关系',
    category: 'social',
    difficulty: 'easy',
    status: 'available',
    location: { lat: 22.3340, lng: 114.2710, name: '学生宿舍' },
    rewards: ['居住徽章', '20积分'],
    estimatedTime: 60
  },
  {
    task_id: 'rh-002',
    title: '宿舍文化活动',
    description: '参与或组织宿舍的文化交流活动',
    category: 'social',
    difficulty: 'medium',
    status: 'available',
    location: { lat: 22.3342, lng: 114.2712, name: '宿舍公共区域' },
    rewards: ['文化徽章', '35积分'],
    estimatedTime: 75
  },

  // Campus Garden tasks
  {
    task_id: 'cg-001',
    title: '校园花园漫步',
    description: '在校园花园中漫步，欣赏自然美景',
    category: 'campus',
    difficulty: 'easy',
    status: 'available',
    location: { lat: 22.3365, lng: 114.2735, name: '校园花园' },
    rewards: ['自然徽章', '10积分'],
    estimatedTime: 25
  },

  // Innovation Hub tasks
  {
    task_id: 'ih-001',
    title: '创新中心参观',
    description: '参观创新中心，了解创业孵化项目',
    category: 'academic',
    difficulty: 'medium',
    status: 'available',
    location: { lat: 22.3380, lng: 114.2750, name: '创新中心' },
    rewards: ['创新徽章', '40积分'],
    estimatedTime: 50
  },
  {
    task_id: 'ih-002',
    title: '创业项目提案',
    description: '准备并提交一个创业项目提案',
    category: 'academic',
    difficulty: 'hard',
    status: 'available',
    location: { lat: 22.3382, lng: 114.2752, name: '创业孵化器' },
    rewards: ['企业家徽章', '80积分'],
    estimatedTime: 180
  },

  // Additional tasks with course and time information
  ...Array.from({ length: 35 }, (_, i) => {
    const courses = [
      '数据结构与算法', '高等数学', '大学英语', '物理学基础', '化学原理',
      '生物学概论', '心理学导论', '社会学基础', '经济学原理', '管理学概论',
      '艺术欣赏', '体育与健康', '哲学思辨', '历史文化', '文学鉴赏'
    ];
    
    const baseDate = new Date('2025-09-09T04:00:00.000Z');
    const createdAt = new Date(baseDate.getTime() + i * 24 * 60 * 60 * 1000 * (Math.random() * 7 - 3));
    const dueDate = new Date(createdAt.getTime() + (7 + Math.random() * 14) * 24 * 60 * 60 * 1000);
    
    return {
      task_id: `extra-${String(i + 1).padStart(3, '0')}`,
      title: `校园探索任务 ${i + 1}`,
      description: `探索校园的隐藏角落，发现更多有趣的地方`,
      category: ['academic', 'social', 'campus'][i % 3] as 'academic' | 'social' | 'campus',
      difficulty: ['easy', 'medium', 'hard'][i % 3] as 'easy' | 'medium' | 'hard',
      status: ['available', 'in_progress', 'completed'][i % 3] as 'available' | 'in_progress' | 'completed',
      location: {
        lat: CITYU_CENTER.lat + (Math.random() - 0.5) * 0.01,
        lng: CITYU_CENTER.lng + (Math.random() - 0.5) * 0.01,
        name: `校园位置 ${i + 1}`
      },
      rewards: ['探索徽章', `${(i + 1) * 5}积分`],
      estimatedTime: 30 + (i % 4) * 15,
      course: courses[i % courses.length],
      createdAt: createdAt.toISOString(),
      dueDate: dueDate.toISOString()
    };
  })
];

export const getCategoryColor = (category: string): string => {
  switch (category) {
    case 'academic': return '#1890ff'; // Blue
    case 'social': return '#722ed1';   // Purple  
    case 'campus': return '#13c2c2';   // Cyan
    default: return '#666666';         // Gray
  }
};

export const getDifficultyIcon = (difficulty: string): string => {
  switch (difficulty) {
    case 'easy': return '⭐';
    case 'medium': return '⭐⭐';
    case 'hard': return '⭐⭐⭐';
    default: return '⭐';
  }
};

export const getStatusIcon = (status: string): string => {
  switch (status) {
    case 'available': return '🎯';
    case 'in_progress': return '⏳';
    case 'completed': return '✅';
    default: return '🎯';
  }
};