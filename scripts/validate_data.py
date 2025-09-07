#!/usr/bin/env python3
"""
数据模板和样例校验脚本
验证 tasks.csv 和 task_kb.jsonl 的格式和内容
"""

import csv
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class DataValidator:
    """数据校验器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def log_error(self, message: str):
        """记录错误"""
        self.errors.append(f"❌ ERROR: {message}")
        
    def log_warning(self, message: str):
        """记录警告"""
        self.warnings.append(f"⚠️  WARNING: {message}")
        
    def log_success(self, message: str):
        """记录成功"""
        print(f"✅ {message}")

class TaskCSVValidator(DataValidator):
    """任务 CSV 文件校验器"""
    
    REQUIRED_FIELDS = [
        'task_id', 'title', 'description', 'category', 'location_name',
        'latitude', 'longitude', 'difficulty', 'estimated_duration',
        'prerequisites', 'rewards', 'status', 'created_at', 'updated_at',
        'npc_id', 'course_code'
    ]
    
    VALID_CATEGORIES = [
        '学术研究', '安全培训', '社团活动', '志愿服务', '文艺活动',
        '创业实践', '体育运动', '生活体验'
    ]
    
    VALID_DIFFICULTIES = ['初级', '中级', '高级']
    VALID_STATUSES = ['active', 'inactive', 'completed', 'pending']
    
    def validate_csv_file(self, file_path: str) -> bool:
        """验证 CSV 文件"""
        print(f"🔍 验证任务 CSV 文件: {file_path}")
        
        if not os.path.exists(file_path):
            self.log_error(f"文件不存在: {file_path}")
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # 验证字段名
                if not self._validate_headers(reader.fieldnames):
                    return False
                
                # 验证数据行
                row_count = 0
                for row_num, row in enumerate(reader, start=2):
                    row_count += 1
                    self._validate_row(row, row_num)
                
                if row_count == 0:
                    self.log_error("CSV 文件为空")
                    return False
                    
                self.log_success(f"CSV 文件包含 {row_count} 条任务记录")
                
        except Exception as e:
            self.log_error(f"读取 CSV 文件失败: {str(e)}")
            return False
            
        return len(self.errors) == 0
    
    def _validate_headers(self, headers: Optional[List[str]]) -> bool:
        """验证 CSV 头部字段"""
        if not headers:
            self.log_error("CSV 文件缺少头部字段")
            return False
            
        missing_fields = set(self.REQUIRED_FIELDS) - set(headers)
        if missing_fields:
            self.log_error(f"缺少必需字段: {', '.join(missing_fields)}")
            return False
            
        extra_fields = set(headers) - set(self.REQUIRED_FIELDS)
        if extra_fields:
            self.log_warning(f"包含额外字段: {', '.join(extra_fields)}")
            
        self.log_success("CSV 头部字段验证通过")
        return True
    
    def _validate_row(self, row: Dict[str, str], row_num: int):
        """验证单行数据"""
        # 验证任务 ID
        if not row.get('task_id') or not re.match(r'^T\d{3}$', row['task_id']):
            self.log_error(f"第 {row_num} 行: 任务 ID 格式错误 (应为 T001 格式)")
            
        # 验证标题和描述
        if not row.get('title') or len(row['title'].strip()) < 2:
            self.log_error(f"第 {row_num} 行: 任务标题不能为空且长度至少2个字符")
            
        if not row.get('description') or len(row['description'].strip()) < 10:
            self.log_error(f"第 {row_num} 行: 任务描述不能为空且长度至少10个字符")
            
        # 验证分类
        if row.get('category') not in self.VALID_CATEGORIES:
            self.log_error(f"第 {row_num} 行: 无效的任务分类 '{row.get('category')}'")
            
        # 验证坐标
        try:
            lat = float(row.get('latitude', 0))
            lng = float(row.get('longitude', 0))
            if not (22.0 <= lat <= 23.0) or not (114.0 <= lng <= 115.0):
                self.log_warning(f"第 {row_num} 行: 坐标可能不在香港范围内")
        except ValueError:
            self.log_error(f"第 {row_num} 行: 坐标格式错误")
            
        # 验证难度
        if row.get('difficulty') not in self.VALID_DIFFICULTIES:
            self.log_error(f"第 {row_num} 行: 无效的难度等级 '{row.get('difficulty')}'")
            
        # 验证预估时长
        try:
            duration = int(row.get('estimated_duration', 0))
            if duration <= 0 or duration > 480:  # 最多8小时
                self.log_error(f"第 {row_num} 行: 预估时长应在 1-480 分钟之间")
        except ValueError:
            self.log_error(f"第 {row_num} 行: 预估时长必须是数字")
            
        # 验证状态
        if row.get('status') not in self.VALID_STATUSES:
            self.log_error(f"第 {row_num} 行: 无效的任务状态 '{row.get('status')}'")
            
        # 验证时间格式
        for time_field in ['created_at', 'updated_at']:
            if row.get(time_field):
                try:
                    datetime.fromisoformat(row[time_field].replace('Z', '+00:00'))
                except ValueError:
                    self.log_error(f"第 {row_num} 行: {time_field} 时间格式错误")

class TaskKBValidator(DataValidator):
    """任务知识库 JSONL 文件校验器"""
    
    REQUIRED_FIELDS = [
        'task_id', 'knowledge_type', 'content', 'tags', 
        'difficulty', 'estimated_time', 'course_code'
    ]
    
    VALID_KNOWLEDGE_TYPES = [
        'procedure', 'safety_guide', 'interview_tips', 'guide_script',
        'project_requirements', 'photography_guide', 'business_plan',
        'fitness_plan', 'performance_guide', 'lab_procedure',
        'food_review', 'academic_notes'
    ]
    
    VALID_DIFFICULTIES = ['初级', '中级', '高级']
    
    def validate_jsonl_file(self, file_path: str) -> bool:
        """验证 JSONL 文件"""
        print(f"🔍 验证任务知识库 JSONL 文件: {file_path}")
        
        if not os.path.exists(file_path):
            self.log_error(f"文件不存在: {file_path}")
            return False
            
        try:
            line_count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                        
                    line_count += 1
                    try:
                        data = json.loads(line)
                        self._validate_json_record(data, line_num)
                    except json.JSONDecodeError as e:
                        self.log_error(f"第 {line_num} 行: JSON 格式错误 - {str(e)}")
                        
            if line_count == 0:
                self.log_error("JSONL 文件为空")
                return False
                
            self.log_success(f"JSONL 文件包含 {line_count} 条知识记录")
            
        except Exception as e:
            self.log_error(f"读取 JSONL 文件失败: {str(e)}")
            return False
            
        return len(self.errors) == 0
    
    def _validate_json_record(self, data: Dict[str, Any], line_num: int):
        """验证单条 JSON 记录"""
        # 验证必需字段
        missing_fields = set(self.REQUIRED_FIELDS) - set(data.keys())
        if missing_fields:
            self.log_error(f"第 {line_num} 行: 缺少必需字段 {', '.join(missing_fields)}")
            
        # 验证任务 ID
        if not data.get('task_id') or not re.match(r'^T\d{3}$', data['task_id']):
            self.log_error(f"第 {line_num} 行: 任务 ID 格式错误")
            
        # 验证知识类型
        if data.get('knowledge_type') not in self.VALID_KNOWLEDGE_TYPES:
            self.log_error(f"第 {line_num} 行: 无效的知识类型 '{data.get('knowledge_type')}'")
            
        # 验证内容
        if not data.get('content') or len(data['content'].strip()) < 20:
            self.log_error(f"第 {line_num} 行: 知识内容不能为空且长度至少20个字符")
            
        # 验证标签
        if not isinstance(data.get('tags'), list) or len(data.get('tags', [])) == 0:
            self.log_error(f"第 {line_num} 行: 标签必须是非空数组")
            
        # 验证难度
        if data.get('difficulty') not in self.VALID_DIFFICULTIES:
            self.log_error(f"第 {line_num} 行: 无效的难度等级 '{data.get('difficulty')}'")
            
        # 验证预估时间
        if not isinstance(data.get('estimated_time'), int) or data.get('estimated_time', 0) <= 0:
            self.log_error(f"第 {line_num} 行: 预估时间必须是正整数")
            
        # 验证课程代码（可选）
        course_code = data.get('course_code')
        if course_code is not None and course_code != "" and not re.match(r'^[A-Z]{2}\d{4}$', course_code):
            self.log_error(f"第 {line_num} 行: 课程代码格式错误 (应为 CS2402 格式)")

def main():
    """主函数"""
    print("🚀 CityU Campus Tasks - 数据校验工具")
    print("=" * 50)
    
    # 获取数据文件路径
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    csv_file = os.path.join(data_dir, 'tasks.csv')
    jsonl_file = os.path.join(data_dir, 'task_kb.jsonl')
    
    # 验证 CSV 文件
    csv_validator = TaskCSVValidator()
    csv_valid = csv_validator.validate_csv_file(csv_file)
    
    print()
    
    # 验证 JSONL 文件
    jsonl_validator = TaskKBValidator()
    jsonl_valid = jsonl_validator.validate_jsonl_file(jsonl_file)
    
    print()
    print("📊 校验结果汇总")
    print("-" * 30)
    
    # 输出所有错误和警告
    all_errors = csv_validator.errors + jsonl_validator.errors
    all_warnings = csv_validator.warnings + jsonl_validator.warnings
    
    if all_errors:
        print("❌ 发现错误:")
        for error in all_errors:
            print(f"  {error}")
    
    if all_warnings:
        print("⚠️  发现警告:")
        for warning in all_warnings:
            print(f"  {warning}")
    
    # 最终结果
    if csv_valid and jsonl_valid:
        print("\n🎉 所有数据文件校验通过!")
        print("✅ tasks.csv - 格式正确")
        print("✅ task_kb.jsonl - 格式正确")
        return 0
    else:
        print("\n💥 数据校验失败!")
        if not csv_valid:
            print("❌ tasks.csv - 存在错误")
        if not jsonl_valid:
            print("❌ task_kb.jsonl - 存在错误")
        return 1

if __name__ == "__main__":
    sys.exit(main())