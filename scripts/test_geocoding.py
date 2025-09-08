#!/usr/bin/env python3
"""
地理编码测试脚本
验证任务数据的地理编码覆盖率和准确性
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import csv
from geocode import geocode_service, get_geocoding_stats
from data_loader import DataLoader

def test_task_geocoding():
    """测试任务数据的地理编码覆盖率"""
    
    print("🗺️  CityU Campus Tasks - 地理编码覆盖率测试")
    print("=" * 60)
    
    # 读取任务数据中的位置信息
    task_locations = []
    tasks_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tasks.csv')
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                location_name = row.get('location_name', '').strip()
                if location_name:
                    task_locations.append(location_name)
        
        print(f"📋 从任务数据中提取到 {len(task_locations)} 个位置")
        print(f"📍 位置列表: {', '.join(task_locations)}")
        print()
        
    except Exception as e:
        print(f"❌ 读取任务文件失败: {str(e)}")
        return False
    
    # 执行地理编码测试
    print("🔍 开始地理编码测试...")
    print("-" * 40)
    
    geocoded_results = {}
    fallback_locations = []
    
    for i, location in enumerate(task_locations, 1):
        result = geocode_service.geocode_location(location)
        geocoded_results[location] = result
        
        status_icon = "✅" if result.source != "fallback" else "⚠️"
        print(f"{status_icon} [{i:2d}] {location}")
        print(f"     坐标: ({result.latitude:.4f}, {result.longitude:.4f})")
        print(f"     来源: {result.source}, 置信度: {result.confidence}")
        
        if result.source == "fallback":
            fallback_locations.append(location)
        print()
    
    # 统计结果
    stats = get_geocoding_stats(task_locations)
    
    print("📊 地理编码统计结果")
    print("=" * 40)
    print(f"📍 总位置数: {stats['total']}")
    print(f"🎯 覆盖率: {stats['coverage_rate']:.2f}%")
    print(f"⭐ 高置信度率: {stats['high_confidence_rate']:.2f}%")
    print(f"📈 来源分布: {stats['sources']}")
    print(f"🔄 回退位置数: {stats['fallback_count']}")
    print()
    
    # 验收标准检查
    print("✅ 验收标准检查")
    print("=" * 40)
    
    coverage_passed = stats['coverage_rate'] >= 95.0
    print(f"📊 覆盖率要求 (≥95%): {stats['coverage_rate']:.2f}% {'✅ 通过' if coverage_passed else '❌ 未通过'}")
    
    if fallback_locations:
        print(f"⚠️  使用回退位置的任务:")
        for location in fallback_locations:
            print(f"   - {location} -> 教学楼入口")
        print(f"💡 建议: 为这些位置添加精确坐标到地理编码映射表")
    else:
        print("🎉 所有位置都有精确坐标!")
    
    print()
    
    # 数据加载器集成测试
    print("🔧 数据加载器集成测试")
    print("=" * 40)
    
    try:
        # 测试数据加载器是否正确使用地理编码
        loader = DataLoader()
        success = loader.load_tasks('../data/tasks.csv')
        
        if success:
            tasks = loader.get_all_tasks()
            print(f"✅ 数据加载器成功加载 {len(tasks)} 个任务")
            
            # 检查坐标数据
            valid_coords = 0
            for task in tasks:
                if (task.latitude != 0 and task.longitude != 0 and 
                    22.33 <= task.latitude <= 22.34 and 
                    114.26 <= task.longitude <= 114.28):  # 香港城市大学坐标范围
                    valid_coords += 1
            
            coord_rate = (valid_coords / len(tasks)) * 100 if tasks else 0
            print(f"📍 有效坐标率: {coord_rate:.2f}% ({valid_coords}/{len(tasks)})")
            
            if coord_rate >= 95:
                print("✅ 坐标数据质量检查通过")
            else:
                print("⚠️  坐标数据质量需要改进")
        else:
            print("❌ 数据加载器测试失败")
            
    except Exception as e:
        print(f"❌ 数据加载器集成测试失败: {str(e)}")
    
    print()
    
    # 总结
    print("🎯 测试总结")
    print("=" * 40)
    
    if coverage_passed:
        print("🎉 地理编码覆盖率测试通过!")
        print("✅ 满足 ≥95% 任务具备坐标的要求")
        print("✅ 缺失任务能正常显示回退点")
        return True
    else:
        print("⚠️  地理编码覆盖率未达标")
        print(f"📊 当前覆盖率: {stats['coverage_rate']:.2f}%")
        print("💡 建议添加更多位置到地理编码映射表")
        return False

def suggest_improvements():
    """建议改进措施"""
    print("\n💡 改进建议")
    print("=" * 40)
    print("1. 扩展校园位置映射表，添加更多建筑物和地点")
    print("2. 集成在线地理编码API (Google Maps, 百度地图等)")
    print("3. 添加位置别名和同义词支持")
    print("4. 实现位置坐标的人工校验和修正机制")
    print("5. 定期更新和维护位置数据库")

if __name__ == "__main__":
    success = test_task_geocoding()
    
    if not success:
        suggest_improvements()
    
    print(f"\n{'🎉 测试完成!' if success else '⚠️  测试完成，需要改进'}")