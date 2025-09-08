#!/usr/bin/env python3
"""
数据加载器模块
负责解析、去重、字段校验和日志记录
提供内存数据管理和调试接口
"""

import csv
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum

# 导入地理编码服务
from geocode import geocode_service, LocationInfo

# 配置日志
import os
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'data_loader.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """校验级别"""
    ERROR = "error"      # 错误：数据无法使用
    WARNING = "warning"  # 警告：数据可用但有问题
    INFO = "info"        # 信息：数据正常

@dataclass
class ValidationResult:
    """校验结果"""
    level: ValidationLevel
    field: str
    message: str
    value: Any = None
    record_id: str = ""

@dataclass
class Task:
    """任务数据模型"""
    task_id: str
    title: str
    description: str
    category: str
    location_name: str
    latitude: float
    longitude: float
    difficulty: str
    estimated_duration: int
    prerequisites: str
    rewards: str
    status: str
    created_at: str
    updated_at: str
    npc_id: str
    course_code: str
    
    def __post_init__(self):
        """数据后处理"""
        # 确保数值类型正确
        if isinstance(self.latitude, str):
            try:
                self.latitude = float(self.latitude)
            except ValueError:
                self.latitude = 0.0
                
        if isinstance(self.longitude, str):
            try:
                self.longitude = float(self.longitude)
            except ValueError:
                self.longitude = 0.0
                
        if isinstance(self.estimated_duration, str):
            try:
                self.estimated_duration = int(self.estimated_duration)
            except ValueError:
                self.estimated_duration = 0
    
    @property
    def location_lat(self) -> float:
        """兼容性属性"""
        return self.latitude
    
    @property
    def location_lng(self) -> float:
        """兼容性属性"""
        return self.longitude
    
    @property
    def points(self) -> int:
        """从奖励字符串中提取积分"""
        if not self.rewards:
            return 0
        # 简单解析积分，如 "学分+2" -> 2
        import re
        match = re.search(r'(\d+)', self.rewards)
        return int(match.group(1)) if match else 0

@dataclass
class TaskKnowledge:
    """任务知识库数据模型"""
    task_id: str
    knowledge_type: str
    content: str
    tags: List[str]
    difficulty: str
    estimated_time: int
    course_code: str
    
    def __post_init__(self):
        """数据后处理"""
        # 确保列表类型正确
        if isinstance(self.tags, str):
            try:
                self.tags = json.loads(self.tags) if self.tags.startswith('[') else [self.tags]
            except json.JSONDecodeError:
                self.tags = [self.tags] if self.tags else []
        elif not isinstance(self.tags, list):
            self.tags = []
                
        if isinstance(self.estimated_time, str):
            try:
                self.estimated_time = int(self.estimated_time)
            except ValueError:
                self.estimated_time = 0
    
    @property
    def title(self) -> str:
        """兼容性属性 - 从知识类型生成标题"""
        type_map = {
            'procedure': '操作流程',
            'safety_guide': '安全指南',
            'interview_tips': '面试技巧',
            'guide_script': '导览脚本',
            'project_requirements': '项目要求',
            'photography_guide': '摄影指南',
            'business_plan': '商业计划',
            'fitness_plan': '健身计划',
            'performance_guide': '表演指南',
            'lab_procedure': '实验流程',
            'food_review': '美食评价',
            'academic_notes': '学术笔记'
        }
        return type_map.get(self.knowledge_type, self.knowledge_type)
    
    @property
    def difficulty_level(self) -> str:
        """兼容性属性"""
        return self.difficulty
    
    @property
    def estimated_read_time(self) -> int:
        """兼容性属性"""
        return self.estimated_time
    
    @property
    def prerequisites(self) -> List[str]:
        """兼容性属性"""
        return []
    
    @property
    def related_tasks(self) -> List[str]:
        """兼容性属性"""
        return []
    
    @property
    def created_at(self) -> str:
        """兼容性属性"""
        return "2024-01-15T09:00:00Z"
    
    @property
    def updated_at(self) -> str:
        """兼容性属性"""
        return "2024-01-15T09:00:00Z"

class DataValidator:
    """数据校验器"""
    
    @staticmethod
    def validate_task(task_data: Dict[str, Any]) -> List[ValidationResult]:
        """校验任务数据"""
        results = []
        
        # 必需字段检查
        required_fields = ['task_id', 'title', 'description', 'category']
        for field in required_fields:
            if not task_data.get(field) or str(task_data[field]).strip() == '':
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=field,
                    message=f"必需字段 '{field}' 为空或缺失",
                    value=task_data.get(field),
                    record_id=task_data.get('task_id', 'unknown')
                ))
        
        # 数值字段检查
        numeric_fields = {
            'latitude': (-90, 90),
            'longitude': (-180, 180),
            'estimated_duration': (1, 10080),  # 1分钟到1周
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            value = task_data.get(field)
            if value is not None:
                try:
                    num_value = float(value)
                    if not (min_val <= num_value <= max_val):
                        results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            field=field,
                            message=f"字段 '{field}' 值 {num_value} 超出合理范围 [{min_val}, {max_val}]",
                            value=value,
                            record_id=task_data.get('task_id', 'unknown')
                        ))
                except (ValueError, TypeError):
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        field=field,
                        message=f"字段 '{field}' 不是有效的数值",
                        value=value,
                        record_id=task_data.get('task_id', 'unknown')
                    ))
        
        # 枚举字段检查
        enum_fields = {
            'difficulty': ['初级', '中级', '高级'],
            'status': ['active', 'inactive', 'draft', 'archived']
        }
        
        for field, valid_values in enum_fields.items():
            value = task_data.get(field)
            if value and value not in valid_values:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field=field,
                    message=f"字段 '{field}' 值 '{value}' 不在有效选项中: {valid_values}",
                    value=value,
                    record_id=task_data.get('task_id', 'unknown')
                ))
        
        return results
    
    @staticmethod
    def validate_task_knowledge(kb_data: Dict[str, Any]) -> List[ValidationResult]:
        """校验知识库数据"""
        results = []
        
        # 必需字段检查
        required_fields = ['task_id', 'knowledge_type', 'content']
        for field in required_fields:
            if not kb_data.get(field) or str(kb_data[field]).strip() == '':
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=field,
                    message=f"必需字段 '{field}' 为空或缺失",
                    value=kb_data.get(field),
                    record_id=kb_data.get('task_id', 'unknown')
                ))
        
        # 内容长度检查
        content = kb_data.get('content', '')
        if len(content) < 10:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                field='content',
                message=f"内容长度过短 ({len(content)} 字符)，建议至少10字符",
                value=len(content),
                record_id=kb_data.get('task_id', 'unknown')
            ))
        elif len(content) > 10000:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                field='content',
                message=f"内容长度过长 ({len(content)} 字符)，建议不超过10000字符",
                value=len(content),
                record_id=kb_data.get('task_id', 'unknown')
            ))
        
        # 标签检查
        tags = kb_data.get('tags', [])
        if isinstance(tags, list) and len(tags) > 10:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                field='tags',
                message=f"标签数量过多 ({len(tags)} 个)，建议不超过10个",
                value=len(tags),
                record_id=kb_data.get('task_id', 'unknown')
            ))
        
        return results

class DataLoader:
    """数据加载器主类"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_knowledge: Dict[str, TaskKnowledge] = {}
        self.validation_results: List[ValidationResult] = []
        self.load_stats = {
            'tasks_loaded': 0,
            'tasks_skipped': 0,
            'knowledge_loaded': 0,
            'knowledge_skipped': 0,
            'duplicates_removed': 0,
            'validation_errors': 0,
            'validation_warnings': 0,
            'last_load_time': None
        }
        self.validator = DataValidator()
        
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """生成数据哈希用于去重"""
        # 排除时间戳字段，只对核心内容计算哈希
        core_data = {k: v for k, v in data.items() 
                    if k not in ['created_at', 'updated_at']}
        data_str = json.dumps(core_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def load_tasks_csv(self, file_path: str) -> bool:
        """加载任务CSV文件"""
        logger.info(f"开始加载任务文件: {file_path}")
        
        if not Path(file_path).exists():
            logger.error(f"文件不存在: {file_path}")
            return False
        
        seen_hashes: Set[str] = set()
        loaded_count = 0
        skipped_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # 数据清理
                        cleaned_row = {k: v.strip() if isinstance(v, str) else v 
                                     for k, v in row.items()}
                        
                        # 校验数据
                        validation_results = self.validator.validate_task(cleaned_row)
                        self.validation_results.extend(validation_results)
                        
                        # 检查是否有错误级别的校验失败
                        has_errors = any(r.level == ValidationLevel.ERROR for r in validation_results)
                        if has_errors:
                            logger.error(f"第 {row_num} 行数据校验失败，跳过")
                            skipped_count += 1
                            self.load_stats['validation_errors'] += len([r for r in validation_results if r.level == ValidationLevel.ERROR])
                            continue
                        
                        # 记录警告
                        warnings = [r for r in validation_results if r.level == ValidationLevel.WARNING]
                        if warnings:
                            for warning in warnings:
                                logger.warning(f"第 {row_num} 行: {warning.message}")
                            self.load_stats['validation_warnings'] += len(warnings)
                        
                        # 去重检查
                        data_hash = self._generate_hash(cleaned_row)
                        if data_hash in seen_hashes:
                            logger.warning(f"第 {row_num} 行: 发现重复数据，跳过")
                            skipped_count += 1
                            self.load_stats['duplicates_removed'] += 1
                            continue
                        seen_hashes.add(data_hash)
                        
                        # 地理编码处理
                        location_name = cleaned_row.get('location_name', '')
                        if location_name:
                            location_info = geocode_service.geocode_location(location_name)
                            # 更新坐标信息 (使用正确的字段名)
                            cleaned_row['latitude'] = location_info.latitude
                            cleaned_row['longitude'] = location_info.longitude
                            
                            # 记录地理编码结果
                            if location_info.source == 'fallback':
                                logger.warning(f"任务 {cleaned_row.get('task_id', 'unknown')} 使用回退位置: {location_name}")
                            else:
                                logger.debug(f"任务 {cleaned_row.get('task_id', 'unknown')} 地理编码成功: {location_name} -> ({location_info.latitude}, {location_info.longitude})")
                        
                        # 创建任务对象
                        task = Task(**cleaned_row)
                        self.tasks[task.task_id] = task
                        loaded_count += 1
                        
                        logger.debug(f"成功加载任务: {task.task_id}")
                        
                    except Exception as e:
                        logger.error(f"第 {row_num} 行处理失败: {str(e)}")
                        skipped_count += 1
                        continue
        
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            return False
        
        self.load_stats['tasks_loaded'] = loaded_count
        self.load_stats['tasks_skipped'] = skipped_count
        logger.info(f"任务加载完成: 成功 {loaded_count} 个, 跳过 {skipped_count} 个")
        return True
    
    def load_knowledge_jsonl(self, file_path: str) -> bool:
        """加载知识库JSONL文件"""
        logger.info(f"开始加载知识库文件: {file_path}")
        
        if not Path(file_path).exists():
            logger.error(f"文件不存在: {file_path}")
            return False
        
        seen_hashes: Set[str] = set()
        loaded_count = 0
        skipped_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # 解析JSON
                        kb_data = json.loads(line)
                        
                        # 校验数据
                        validation_results = self.validator.validate_task_knowledge(kb_data)
                        self.validation_results.extend(validation_results)
                        
                        # 检查是否有错误级别的校验失败
                        has_errors = any(r.level == ValidationLevel.ERROR for r in validation_results)
                        if has_errors:
                            logger.error(f"第 {line_num} 行数据校验失败，跳过")
                            skipped_count += 1
                            self.load_stats['validation_errors'] += len([r for r in validation_results if r.level == ValidationLevel.ERROR])
                            continue
                        
                        # 记录警告
                        warnings = [r for r in validation_results if r.level == ValidationLevel.WARNING]
                        if warnings:
                            for warning in warnings:
                                logger.warning(f"第 {line_num} 行: {warning.message}")
                            self.load_stats['validation_warnings'] += len(warnings)
                        
                        # 去重检查
                        data_hash = self._generate_hash(kb_data)
                        if data_hash in seen_hashes:
                            logger.warning(f"第 {line_num} 行: 发现重复数据，跳过")
                            skipped_count += 1
                            self.load_stats['duplicates_removed'] += 1
                            continue
                        seen_hashes.add(data_hash)
                        
                        # 创建知识库对象
                        knowledge = TaskKnowledge(**kb_data)
                        self.task_knowledge[knowledge.task_id] = knowledge
                        loaded_count += 1
                        
                        logger.debug(f"成功加载知识库: {knowledge.task_id}")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"第 {line_num} 行JSON解析失败: {str(e)}")
                        skipped_count += 1
                        continue
                    except Exception as e:
                        logger.error(f"第 {line_num} 行处理失败: {str(e)}")
                        skipped_count += 1
                        continue
        
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            return False
        
        self.load_stats['knowledge_loaded'] = loaded_count
        self.load_stats['knowledge_skipped'] = skipped_count
        logger.info(f"知识库加载完成: 成功 {loaded_count} 个, 跳过 {skipped_count} 个")
        return True
    
    def load_all_data(self, tasks_file: str = "../data/tasks.csv", 
                     knowledge_file: str = "../data/task_kb.jsonl") -> bool:
        """加载所有数据"""
        logger.info("开始加载所有数据")
        
        # 重置统计信息
        self.load_stats['last_load_time'] = datetime.now().isoformat()
        
        # 加载任务数据
        tasks_success = self.load_tasks_csv(tasks_file)
        
        # 加载知识库数据
        knowledge_success = self.load_knowledge_jsonl(knowledge_file)
        
        # 数据一致性检查
        self._check_data_consistency()
        
        success = tasks_success and knowledge_success
        if success:
            logger.info("所有数据加载完成")
        else:
            logger.error("数据加载过程中出现错误")
        
        return success
    
    def _check_data_consistency(self):
        """检查数据一致性"""
        logger.info("开始数据一致性检查")
        
        # 检查任务和知识库的对应关系
        task_ids = set(self.tasks.keys())
        knowledge_task_ids = set(self.task_knowledge.keys())
        
        # 找出缺少知识库的任务
        missing_knowledge = task_ids - knowledge_task_ids
        if missing_knowledge:
            logger.warning(f"以下任务缺少知识库条目: {missing_knowledge}")
        
        # 找出没有对应任务的知识库
        orphaned_knowledge = knowledge_task_ids - task_ids
        if orphaned_knowledge:
            logger.warning(f"以下知识库条目没有对应任务: {orphaned_knowledge}")
        
        logger.info(f"一致性检查完成: 任务 {len(task_ids)} 个, 知识库 {len(knowledge_task_ids)} 个")
    
    def get_memory_snapshot(self) -> Dict[str, Any]:
        """获取内存数据快照"""
        return {
            "timestamp": datetime.now().isoformat(),
            "stats": self.load_stats.copy(),
            "validation_summary": {
                "total_issues": len(self.validation_results),
                "errors": len([r for r in self.validation_results if r.level == ValidationLevel.ERROR]),
                "warnings": len([r for r in self.validation_results if r.level == ValidationLevel.WARNING]),
                "info": len([r for r in self.validation_results if r.level == ValidationLevel.INFO])
            },
            "data_summary": {
                "tasks_count": len(self.tasks),
                "knowledge_count": len(self.task_knowledge),
                "task_ids": list(self.tasks.keys()),
                "knowledge_task_ids": list(self.task_knowledge.keys())
            },
            "tasks": {task_id: asdict(task) for task_id, task in self.tasks.items()},
            "knowledge": {task_id: asdict(kb) for task_id, kb in self.task_knowledge.items()},
            "validation_results": [
                {
                    "level": result.level.value,
                    "field": result.field,
                    "message": result.message,
                    "value": result.value,
                    "record_id": result.record_id
                }
                for result in self.validation_results
            ]
        }
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取指定任务"""
        return self.tasks.get(task_id)
    
    def get_task_knowledge(self, task_id: str) -> Optional[TaskKnowledge]:
        """获取指定任务的知识库"""
        return self.task_knowledge.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def get_all_knowledge(self) -> List[TaskKnowledge]:
        """获取所有知识库"""
        return list(self.task_knowledge.values())
    
    def get_load_stats(self) -> Dict[str, Any]:
        """获取加载统计信息"""
        return self.load_stats.copy()
    
    def get_validation_results(self) -> List[ValidationResult]:
        """获取校验结果"""
        return self.validation_results.copy()

# 全局数据加载器实例
data_loader = DataLoader()

def initialize_data_loader():
    """初始化数据加载器"""
    logger.info("初始化数据加载器")
    success = data_loader.load_all_data()
    if success:
        logger.info("数据加载器初始化成功")
    else:
        logger.error("数据加载器初始化失败")
    return success

if __name__ == "__main__":
    # 测试数据加载器
    initialize_data_loader()
    
    # 打印统计信息
    stats = data_loader.get_load_stats()
    print(f"加载统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 打印校验结果摘要
    validation_results = data_loader.get_validation_results()
    errors = [r for r in validation_results if r.level == ValidationLevel.ERROR]
    warnings = [r for r in validation_results if r.level == ValidationLevel.WARNING]
    
    print(f"\n校验结果摘要:")
    print(f"  错误: {len(errors)} 个")
    print(f"  警告: {len(warnings)} 个")
    
    if errors:
        print("\n错误详情:")
        for error in errors[:5]:  # 只显示前5个错误
            print(f"  - {error.record_id}: {error.field} - {error.message}")
    
    if warnings:
        print("\n警告详情:")
        for warning in warnings[:5]:  # 只显示前5个警告
            print(f"  - {warning.record_id}: {warning.field} - {warning.message}")