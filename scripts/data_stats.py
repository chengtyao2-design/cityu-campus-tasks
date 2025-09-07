#!/usr/bin/env python3
"""
数据统计分析脚本
分析 tasks.csv 和 task_kb.jsonl 的内容和质量
"""

import csv
import json
from collections import Counter
from typing import Dict, List, Any, Set
import os

def analyze_tasks_csv(file_path: str) -> Dict[str, Any]:
    """分析 tasks.csv 文件"""
    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}"}
    
    stats = {
        "total_tasks": 0,
        "categories": Counter(),
        "difficulties": Counter(),
        "locations": set(),
        "npcs": set(),
        "courses": set(),
        "durations": [],
        "points": [],
        "field_stats": {}
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                stats["total_tasks"] += 1
                
                # 统计分类
                if row.get("category"):
                    stats["categories"][row["category"]] += 1
                
                # 统计难度
                if row.get("difficulty"):
                    stats["difficulties"][row["difficulty"]] += 1
                
                # 统计时长
                if row.get("estimated_duration"):
                    try:
                        duration = int(row["estimated_duration"])
                        stats["durations"].append(duration)
                    except ValueError:
                        pass
                
                # 统计积分
                if row.get("points"):
                    try:
                        points = int(row["points"])
                        stats["points"].append(points)
                    except ValueError:
                        pass
                
                # 收集唯一值
                if row.get("location_name"):
                    stats["locations"].add(row["location_name"])
                if row.get("npc_id"):
                    stats["npcs"].add(row["npc_id"])
                if row.get("course_code"):
                    stats["courses"].add(row["course_code"])
                
                # 字段完整性统计
                for field, value in row.items():
                    if field not in stats["field_stats"]:
                        stats["field_stats"][field] = {"filled": 0, "empty": 0}
                    
                    if value and value.strip():
                        stats["field_stats"][field]["filled"] += 1
                    else:
                        stats["field_stats"][field]["empty"] += 1
        
        # 计算平均值
        if stats["durations"]:
            stats["avg_duration"] = sum(stats["durations"]) / len(stats["durations"])
            stats["min_duration"] = min(stats["durations"])
            stats["max_duration"] = max(stats["durations"])
        
        if stats["points"]:
            stats["avg_points"] = sum(stats["points"]) / len(stats["points"])
            stats["min_points"] = min(stats["points"])
            stats["max_points"] = max(stats["points"])
        
        # 计算字段完整率
        for field_name, field_data in stats["field_stats"].items():
            total = field_data["filled"] + field_data["empty"]
            if total > 0:
                field_data["completion_rate"] = field_data["filled"] / total
        
        # 转换集合为列表以便JSON序列化
        stats["locations"] = len(stats["locations"])
        stats["npcs"] = len(stats["npcs"])
        stats["courses"] = len(stats["courses"])
        
    except Exception as e:
        return {"error": f"读取文件时出错: {str(e)}"}
    
    return stats

def analyze_task_kb_jsonl(file_path: str) -> Dict[str, Any]:
    """分析 task_kb.jsonl 文件"""
    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}"}
    
    stats = {
        "total_records": 0,
        "knowledge_types": Counter(),
        "task_ids": set(),
        "tags": Counter(),
        "field_stats": {}
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    stats["total_records"] += 1
                    
                    # 统计知识类型
                    if record.get("knowledge_type"):
                        stats["knowledge_types"][record["knowledge_type"]] += 1
                    
                    # 收集任务ID
                    if record.get("task_id"):
                        stats["task_ids"].add(record["task_id"])
                    
                    # 统计标签
                    if record.get("tags") and isinstance(record["tags"], list):
                        for tag in record["tags"]:
                            stats["tags"][tag] += 1
                    
                    # 字段完整性统计
                    for field, value in record.items():
                        if field not in stats["field_stats"]:
                            stats["field_stats"][field] = {"filled": 0, "empty": 0}
                        
                        if value is not None and str(value).strip():
                            stats["field_stats"][field]["filled"] += 1
                        else:
                            stats["field_stats"][field]["empty"] += 1
                
                except json.JSONDecodeError as e:
                    print(f"第 {line_num} 行JSON解析错误: {e}")
                    continue
        
        # 计算字段完整率
        for field_name, field_data in stats["field_stats"].items():
            total = field_data["filled"] + field_data["empty"]
            if total > 0:
                field_data["completion_rate"] = field_data["filled"] / total
        
        # 转换集合为数量
        stats["unique_task_ids"] = len(stats["task_ids"])
        stats["task_ids"] = list(stats["task_ids"])  # 保留列表用于验证
        
    except Exception as e:
        return {"error": f"读取文件时出错: {str(e)}"}
    
    return stats

def print_analysis_report(tasks_stats: Dict[str, Any], kb_stats: Dict[str, Any]):
    """打印分析报告"""
    print("=" * 60)
    print("🎯 CityU Campus Tasks 数据分析报告")
    print("=" * 60)
    
    # Tasks CSV 分析
    if "error" not in tasks_stats:
        print("\n📊 任务数据 (tasks.csv) 分析:")
        print(f"  总任务数: {tasks_stats['total_tasks']} 个")
        
        if tasks_stats.get("avg_duration"):
            print(f"  平均时长: {tasks_stats['avg_duration']:.1f} 分钟")
            print(f"  时长范围: {tasks_stats['min_duration']}-{tasks_stats['max_duration']} 分钟")
        
        if tasks_stats.get("avg_points"):
            print(f"  平均积分: {tasks_stats['avg_points']:.1f} 分")
            print(f"  积分范围: {tasks_stats['min_points']}-{tasks_stats['max_points']} 分")
        
        print(f"  独特地点: {tasks_stats['locations']} 个")
        print(f"  关联NPC: {tasks_stats['npcs']} 个")
        print(f"  涉及课程: {tasks_stats['courses']} 门")
        
        print("\n  📈 分类分布:")
        for category, count in tasks_stats["categories"].most_common():
            percentage = (count / tasks_stats["total_tasks"]) * 100
            print(f"    {category}: {count} 个 ({percentage:.1f}%)")
        
        print("\n  🎚️ 难度分布:")
        for difficulty, count in tasks_stats["difficulties"].most_common():
            percentage = (count / tasks_stats["total_tasks"]) * 100
            print(f"    {difficulty}: {count} 个 ({percentage:.1f}%)")
    else:
        print(f"\n❌ 任务数据分析失败: {tasks_stats['error']}")
    
    # Task KB JSONL 分析
    if "error" not in kb_stats:
        print(f"\n📚 知识库数据 (task_kb.jsonl) 分析:")
        print(f"  总记录数: {kb_stats['total_records']} 条")
        print(f"  关联任务: {kb_stats['unique_task_ids']} 个")
        
        print("\n  🧠 知识类型分布:")
        for knowledge_type, count in kb_stats["knowledge_types"].most_common():
            percentage = (count / kb_stats["total_records"]) * 100
            print(f"    {knowledge_type}: {count} 条 ({percentage:.1f}%)")
        
        print(f"\n  🏷️ 标签统计:")
        print(f"    总标签数: {len(kb_stats['tags'])} 个")
        print("    热门标签:")
        for tag, count in kb_stats["tags"].most_common(10):
            print(f"      {tag}: {count} 次")
    else:
        print(f"\n❌ 知识库数据分析失败: {kb_stats['error']}")
    
    # 数据一致性检查
    if "error" not in tasks_stats and "error" not in kb_stats:
        print(f"\n🔗 数据一致性检查:")
        task_kb_coverage = (kb_stats['unique_task_ids'] / tasks_stats['total_tasks']) * 100
        print(f"  知识库覆盖率: {task_kb_coverage:.1f}%")
        
        if task_kb_coverage >= 100:
            print("  ✅ 所有任务都有对应的知识库条目")
        else:
            print("  ⚠️ 部分任务缺少知识库条目")
    
    print("\n" + "=" * 60)
    print("📋 数据质量评估完成")
    print("=" * 60)

def main():
    """主函数"""
    # 分析数据文件
    tasks_stats = analyze_tasks_csv("data/tasks.csv")
    kb_stats = analyze_task_kb_jsonl("data/task_kb.jsonl")
    
    # 打印报告
    print_analysis_report(tasks_stats, kb_stats)
    
    # 保存详细统计到文件
    detailed_stats = {
        "tasks_analysis": tasks_stats,
        "knowledge_base_analysis": kb_stats,
        "generated_at": "2025-09-08T02:00:00+08:00"
    }
    
    try:
        with open("data/analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(detailed_stats, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n💾 详细分析报告已保存到: data/analysis_report.json")
    except Exception as e:
        print(f"\n❌ 保存分析报告失败: {e}")

if __name__ == "__main__":
    main()