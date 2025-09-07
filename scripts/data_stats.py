#!/usr/bin/env python3
"""
数据统计分析脚本
分析 tasks.csv 和 task_kb.jsonl 的内容统计
"""

import csv
import json
import os
from collections import Counter, defaultdict
from typing import Dict, List, Any

def analyze_tasks_csv(file_path: str) -> Dict[str, Any]:
    """分析任务 CSV 文件"""
    stats = {
        'total_tasks': 0,
        'categories': Counter(),
        'difficulties': Counter(),
        'statuses': Counter(),
        'courses': Counter(),
        'avg_duration': 0,
        'duration_range': {'min': float('inf'), 'max': 0},
        'locations': set(),
        'npcs': set()
    }
    
    total_duration = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            stats['total_tasks'] += 1
            
            # 统计分类
            stats['categories'][row.get('category', 'Unknown')] += 1
            
            # 统计难度
            stats['difficulties'][row.get('difficulty', 'Unknown')] += 1
            
            # 统计状态
            stats['statuses'][row.get('status', 'Unknown')] += 1
            
            # 统计课程
            course = row.get('course_code', '').strip()
            if course:
                stats['courses'][course] += 1
            else:
                stats['courses']['无课程关联'] += 1
            
            # 统计时长
            try:
                duration = int(row.get('estimated_duration', 0))
                total_duration += duration
                stats['duration_range']['min'] = min(stats['duration_range']['min'], duration)
                stats['duration_range']['max'] = max(stats['duration_range']['max'], duration)
            except ValueError:
                pass
            
            # 统计地点和NPC
            stats['locations'].add(row.get('location_name', 'Unknown'))
            stats['npcs'].add(row.get('npc_id', 'Unknown'))
    
    if stats['total_tasks'] > 0:
        stats['avg_duration'] = total_duration / stats['total_tasks']
    
    # 转换集合为计数
    stats['unique_locations'] = len(stats['locations'])
    stats['unique_npcs'] = len(stats['npcs'])
    del stats['locations']
    del stats['npcs']
    
    return stats

def analyze_task_kb_jsonl(file_path: str) -> Dict[str, Any]:
    """分析任务知识库 JSONL 文件"""
    stats = {
        'total_records': 0,
        'knowledge_types': Counter(),
        'difficulties': Counter(),
        'avg_content_length': 0,
        'content_length_range': {'min': float('inf'), 'max': 0},
        'avg_tags_count': 0,
        'all_tags': Counter(),
        'courses': Counter(),
        'avg_estimated_time': 0
    }
    
    total_content_length = 0
    total_tags_count = 0
    total_estimated_time = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                stats['total_records'] += 1
                
                # 统计知识类型
                stats['knowledge_types'][data.get('knowledge_type', 'Unknown')] += 1
                
                # 统计难度
                stats['difficulties'][data.get('difficulty', 'Unknown')] += 1
                
                # 统计内容长度
                content = data.get('content', '')
                content_length = len(content)
                total_content_length += content_length
                stats['content_length_range']['min'] = min(stats['content_length_range']['min'], content_length)
                stats['content_length_range']['max'] = max(stats['content_length_range']['max'], content_length)
                
                # 统计标签
                tags = data.get('tags', [])
                if isinstance(tags, list):
                    total_tags_count += len(tags)
                    for tag in tags:
                        stats['all_tags'][tag] += 1
                
                # 统计课程
                course = data.get('course_code')
                if course:
                    stats['courses'][course] += 1
                else:
                    stats['courses']['无课程关联'] += 1
                
                # 统计预估时间
                estimated_time = data.get('estimated_time', 0)
                if isinstance(estimated_time, int):
                    total_estimated_time += estimated_time
                    
            except json.JSONDecodeError:
                continue
    
    if stats['total_records'] > 0:
        stats['avg_content_length'] = total_content_length / stats['total_records']
        stats['avg_tags_count'] = total_tags_count / stats['total_records']
        stats['avg_estimated_time'] = total_estimated_time / stats['total_records']
    
    return stats

def print_stats():
    """打印统计信息"""
    print("📊 CityU Campus Tasks - 数据统计分析")
    print("=" * 60)
    
    # 获取文件路径
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    csv_file = os.path.join(data_dir, 'tasks.csv')
    jsonl_file = os.path.join(data_dir, 'task_kb.jsonl')
    
    # 分析任务数据
    print("\n🎯 任务数据统计 (tasks.csv)")
    print("-" * 40)
    
    if os.path.exists(csv_file):
        task_stats = analyze_tasks_csv(csv_file)
        
        print(f"📋 总任务数: {task_stats['total_tasks']}")
        print(f"⏱️  平均时长: {task_stats['avg_duration']:.1f} 分钟")
        print(f"📍 独特地点: {task_stats['unique_locations']} 个")
        print(f"🤖 关联NPC: {task_stats['unique_npcs']} 个")
        
        print(f"\n📂 任务分类分布:")
        for category, count in task_stats['categories'].most_common():
            percentage = (count / task_stats['total_tasks']) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")
        
        print(f"\n⭐ 难度分布:")
        for difficulty, count in task_stats['difficulties'].most_common():
            percentage = (count / task_stats['total_tasks']) * 100
            print(f"  {difficulty}: {count} ({percentage:.1f}%)")
        
        print(f"\n📚 课程关联:")
        for course, count in task_stats['courses'].most_common():
            percentage = (count / task_stats['total_tasks']) * 100
            print(f"  {course}: {count} ({percentage:.1f}%)")
            
        print(f"\n⏰ 时长范围: {task_stats['duration_range']['min']}-{task_stats['duration_range']['max']} 分钟")
    else:
        print("❌ tasks.csv 文件不存在")
    
    # 分析知识库数据
    print("\n📚 知识库数据统计 (task_kb.jsonl)")
    print("-" * 40)
    
    if os.path.exists(jsonl_file):
        kb_stats = analyze_task_kb_jsonl(jsonl_file)
        
        print(f"📖 总知识条目: {kb_stats['total_records']}")
        print(f"📝 平均内容长度: {kb_stats['avg_content_length']:.1f} 字符")
        print(f"🏷️  平均标签数: {kb_stats['avg_tags_count']:.1f} 个")
        print(f"⏱️  平均学习时间: {kb_stats['avg_estimated_time']:.1f} 分钟")
        
        print(f"\n📋 知识类型分布:")
        for knowledge_type, count in kb_stats['knowledge_types'].most_common():
            percentage = (count / kb_stats['total_records']) * 100
            print(f"  {knowledge_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n🏷️  热门标签 (Top 10):")
        for tag, count in kb_stats['all_tags'].most_common(10):
            percentage = (count / kb_stats['total_records']) * 100
            print(f"  {tag}: {count} ({percentage:.1f}%)")
        
        print(f"\n📚 课程关联:")
        for course, count in kb_stats['courses'].most_common():
            percentage = (count / kb_stats['total_records']) * 100
            print(f"  {course}: {count} ({percentage:.1f}%)")
            
        print(f"\n📏 内容长度范围: {kb_stats['content_length_range']['min']}-{kb_stats['content_length_range']['max']} 字符")
    else:
        print("❌ task_kb.jsonl 文件不存在")
    
    # 数据质量评估
    print("\n🔍 数据质量评估")
    print("-" * 40)
    
    if os.path.exists(csv_file) and os.path.exists(jsonl_file):
        task_stats = analyze_tasks_csv(csv_file)
        kb_stats = analyze_task_kb_jsonl(jsonl_file)
        
        # 检查数据一致性
        if task_stats['total_tasks'] == kb_stats['total_records']:
            print("✅ 任务数据与知识库数据数量一致")
        else:
            print(f"⚠️  数据数量不一致: 任务({task_stats['total_tasks']}) vs 知识库({kb_stats['total_records']})")
        
        # 检查课程覆盖
        course_tasks = sum(1 for course in task_stats['courses'] if course != '无课程关联')
        course_percentage = (course_tasks / task_stats['total_tasks']) * 100
        print(f"📚 课程关联覆盖率: {course_percentage:.1f}%")
        
        # 检查难度分布
        difficulty_balance = max(task_stats['difficulties'].values()) / min(task_stats['difficulties'].values())
        if difficulty_balance <= 2:
            print("✅ 难度分布相对均衡")
        else:
            print("⚠️  难度分布不均衡，建议调整")
    
    print("\n🎯 数据概览完成!")

if __name__ == "__main__":
    print_stats()