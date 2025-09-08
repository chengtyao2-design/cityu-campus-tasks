"""
简化的搜索功能测试（不依赖 pytest）
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from search_engine import BM25SearchEngine


def test_search_engine():
    """测试搜索引擎基本功能"""
    print("🔍 开始测试搜索引擎...")
    
    # 创建搜索引擎
    engine = BM25SearchEngine()
    
    # 测试文档
    test_documents = [
        {
            'task_id': 'T001',
            'title': '图书馆文献检索',
            'description': '在图书馆完成指定主题的文献检索任务，学习如何使用数据库和检索工具',
            'location_lat': 22.3364,
            'location_lng': 114.2654
        },
        {
            'task_id': 'T002',
            'title': '实验室安全培训',
            'description': '参加实验室安全培训课程，了解实验室操作规范和安全注意事项',
            'location_lat': 22.3370,
            'location_lng': 114.2660
        },
        {
            'task_id': 'T003',
            'title': '学生会招新面试',
            'description': '参加学生会各部门的招新面试，展示个人能力和团队合作精神',
            'location_lat': 22.3358,
            'location_lng': 114.2648
        }
    ]
    
    # 构建索引
    print("📚 构建搜索索引...")
    engine.build_index(test_documents)
    print(f"   索引构建完成，文档数量: {engine.corpus_size}")
    print(f"   词汇数量: {len(engine.idf)}")
    print(f"   平均文档长度: {engine.avgdl:.2f}")
    
    # 测试分词
    print("\n🔤 测试分词功能...")
    test_cases = [
        ("图书馆文献检索", ['图', '书', '馆', '文', '献', '检', '索']),
        ("Library Research", ['library', 'research']),
        ("图书馆 Library", ['图', '书', '馆', 'library'])
    ]
    
    for text, expected in test_cases:
        tokens = engine.tokenize(text)
        print(f"   '{text}' -> {tokens}")
        if tokens == expected:
            print("   ✅ 分词正确")
        else:
            print(f"   ❌ 分词错误，期望: {expected}")
    
    # 测试搜索
    print("\n🔍 测试搜索功能...")
    search_queries = [
        ("图书馆", "应该匹配图书馆文献检索"),
        ("安全", "应该匹配实验室安全培训"),
        ("学生", "应该匹配学生会招新面试"),
        ("文献", "应该匹配图书馆文献检索"),
        ("不存在的词", "应该无匹配结果")
    ]
    
    for query, description in search_queries:
        print(f"\n   查询: '{query}' ({description})")
        results = engine.search(query, top_n=3)
        
        if results:
            print(f"   找到 {len(results)} 个结果:")
            for i, result in enumerate(results, 1):
                print(f"     {i}. {result['task_id']}: {result['title']}")
                print(f"        分数: {result['score']:.4f}, 坐标: ({result['lat']}, {result['lng']})")
        else:
            print("   无匹配结果")
    
    # 测试边界情况
    print("\n🧪 测试边界情况...")
    
    # 空查询
    empty_results = engine.search("", top_n=5)
    print(f"   空查询结果数量: {len(empty_results)} (应该为0)")
    
    # 限制结果数量
    limited_results = engine.search("学", top_n=1)
    print(f"   限制结果数量测试: {len(limited_results)} (应该 <= 1)")
    
    print("\n✅ 搜索引擎测试完成!")
    return True


def test_api_integration():
    """测试 API 集成"""
    print("\n🌐 测试 API 集成...")
    
    import requests
    import json
    
    base_url = "http://localhost:8000"
    
    # 测试搜索端点
    search_data = {
        "query": "图书馆",
        "top_n": 5
    }
    
    try:
        response = requests.post(
            f"{base_url}/tasks/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   返回结果数量: {len(data.get('data', []))}")
            print(f"   元数据: {data.get('meta', {})}")
            
            # 显示搜索结果
            for result in data.get('data', []):
                print(f"     - {result.get('task_id')}: {result.get('title')} (分数: {result.get('score', 0):.4f})")
            
            print("   ✅ API 集成测试通过")
        else:
            print(f"   ❌ API 请求失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ API 测试失败: {e}")
        print("   (请确保服务器正在运行)")


if __name__ == "__main__":
    print("🚀 开始搜索功能测试\n")
    
    # 测试搜索引擎
    test_search_engine()
    
    # 测试 API 集成
    test_api_integration()
    
    print("\n🎉 所有测试完成!")