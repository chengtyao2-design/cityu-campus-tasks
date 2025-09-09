"""
搜索功能测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from search_engine import BM25SearchEngine


class TestBM25SearchEngine:
    """BM25 搜索引擎测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = BM25SearchEngine()
        
        # 测试文档
        self.test_documents = [
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
            },
            {
                'task_id': 'T004',
                'title': '校园导览志愿服务',
                'description': '为新生和访客提供校园导览服务，介绍校园历史和各个建筑',
                'location_lat': 22.3355,
                'location_lng': 114.2645
            },
            {
                'task_id': 'T005',
                'title': '学术讲座参与',
                'description': '参加学术讲座，了解最新研究成果和学术动态',
                'location_lat': 22.3362,
                'location_lng': 114.2652
            }
        ]
        
        # 构建索引
        self.engine.build_index(self.test_documents)
    
    def test_tokenize_chinese(self):
        """测试中文分词"""
        text = "图书馆文献检索"
        tokens = self.engine.tokenize(text)
        expected = ['图', '书', '馆', '文', '献', '检', '索']
        assert tokens == expected
    
    def test_tokenize_english(self):
        """测试英文分词"""
        text = "Library Research Task"
        tokens = self.engine.tokenize(text)
        expected = ['library', 'research', 'task']
        assert tokens == expected
    
    def test_tokenize_mixed(self):
        """测试中英文混合分词"""
        text = "图书馆 Library 检索"
        tokens = self.engine.tokenize(text)
        expected = ['图', '书', '馆', 'library', '检', '索']
        assert tokens == expected
    
    def test_tokenize_empty(self):
        """测试空文本分词"""
        tokens = self.engine.tokenize("")
        assert tokens == []
        
        tokens = self.engine.tokenize(None)
        assert tokens == []
    
    def test_build_index(self):
        """测试索引构建"""
        assert self.engine.indexed == True
        assert self.engine.corpus_size == 5
        assert len(self.engine.documents) == 5
        assert len(self.engine.doc_len) == 5
        assert self.engine.avgdl > 0
        assert len(self.engine.idf) > 0
    
    def test_search_exact_match(self):
        """测试精确匹配搜索"""
        results = self.engine.search("图书馆", top_n=5)
        
        # 应该返回包含"图书馆"的结果
        assert len(results) > 0
        assert results[0]['task_id'] == 'T001'  # 图书馆文献检索应该排第一
        assert results[0]['score'] > 0
        
        # 验证返回格式
        for result in results:
            assert 'task_id' in result
            assert 'title' in result
            assert 'score' in result
            assert 'lat' in result
            assert 'lng' in result
            assert isinstance(result['score'], float)
            assert result['score'] > 0
    
    def test_search_partial_match(self):
        """测试部分匹配搜索"""
        results = self.engine.search("安全", top_n=5)
        
        # 应该返回包含"安全"的结果
        assert len(results) > 0
        assert results[0]['task_id'] == 'T002'  # 实验室安全培训
        assert results[0]['score'] > 0
    
    def test_search_multiple_keywords(self):
        """测试多关键词搜索"""
        results = self.engine.search("学生 面试", top_n=5)
        
        # 应该返回相关结果
        assert len(results) > 0
        # 学生会招新面试应该有较高分数
        task_ids = [r['task_id'] for r in results]
        assert 'T003' in task_ids
    
    def test_search_ranking(self):
        """测试搜索结果排序"""
        results = self.engine.search("学术", top_n=5)
        
        if len(results) > 1:
            # 验证结果按分数降序排列
            for i in range(len(results) - 1):
                assert results[i]['score'] >= results[i + 1]['score']
    
    def test_search_empty_query(self):
        """测试空查询"""
        results = self.engine.search("", top_n=5)
        assert len(results) == 0
        
        results = self.engine.search("   ", top_n=5)
        assert len(results) == 0
    
    def test_search_no_match(self):
        """测试无匹配结果"""
        results = self.engine.search("不存在的关键词xyz", top_n=5)
        assert len(results) == 0
    
    def test_search_top_n_limit(self):
        """测试返回结果数量限制"""
        results = self.engine.search("学", top_n=2)
        assert len(results) <= 2
        
        results = self.engine.search("学", top_n=10)
        assert len(results) <= 10
    
    def test_search_score_positive(self):
        """测试搜索分数为正数"""
        results = self.engine.search("图书馆", top_n=5)
        
        for result in results:
            assert result['score'] > 0
            assert isinstance(result['score'], float)
    
    def test_search_coordinates(self):
        """测试搜索结果包含坐标"""
        results = self.engine.search("图书馆", top_n=1)
        
        assert len(results) > 0
        result = results[0]
        assert 'lat' in result
        assert 'lng' in result
        assert isinstance(result['lat'], float)
        assert isinstance(result['lng'], float)
        assert -90 <= result['lat'] <= 90
        assert -180 <= result['lng'] <= 180


def test_search_engine_integration():
    """集成测试"""
    engine = BM25SearchEngine()
    
    # 测试文档
    documents = [
        {
            'task_id': 'TEST001',
            'title': '测试任务',
            'description': '这是一个测试任务',
            'location_lat': 22.0,
            'location_lng': 114.0
        }
    ]
    
    # 构建索引
    engine.build_index(documents)
    
    # 搜索测试
    results = engine.search("测试", top_n=1)
    assert len(results) == 1
    assert results[0]['task_id'] == 'TEST001'
    assert results[0]['score'] > 0


def test_bm25_parameters():
    """测试 BM25 参数"""
    # 测试不同参数设置
    engine1 = BM25SearchEngine(k1=1.2, b=0.75)
    engine2 = BM25SearchEngine(k1=2.0, b=0.5)
    
    documents = [
        {
            'task_id': 'T001',
            'title': '短标题',
            'description': '短描述',
            'location_lat': 22.0,
            'location_lng': 114.0
        },
        {
            'task_id': 'T002',
            'title': '这是一个很长很长的标题包含很多词汇',
            'description': '这是一个很长很长的描述包含很多词汇和详细信息',
            'location_lat': 22.1,
            'location_lng': 114.1
        }
    ]
    
    engine1.build_index(documents)
    engine2.build_index(documents)
    
    # 搜索相同关键词
    results1 = engine1.search("标题", top_n=2)
    results2 = engine2.search("标题", top_n=2)
    
    # 两个引擎都应该返回结果
    assert len(results1) > 0
    assert len(results2) > 0


if __name__ == "__main__":
    # 运行测试
    test_engine = TestBM25SearchEngine()
    test_engine.setup_method()
    
    print("运行搜索引擎测试...")
    
    # 基础功能测试
    print("1. 测试分词功能...")
    test_engine.test_tokenize_chinese()
    test_engine.test_tokenize_english()
    test_engine.test_tokenize_mixed()
    test_engine.test_tokenize_empty()
    print("   ✅ 分词功能测试通过")
    
    # 索引构建测试
    print("2. 测试索引构建...")
    test_engine.test_build_index()
    print("   ✅ 索引构建测试通过")
    
    # 搜索功能测试
    print("3. 测试搜索功能...")
    test_engine.test_search_exact_match()
    test_engine.test_search_partial_match()
    test_engine.test_search_multiple_keywords()
    test_engine.test_search_ranking()
    print("   ✅ 搜索功能测试通过")
    
    # 边界情况测试
    print("4. 测试边界情况...")
    test_engine.test_search_empty_query()
    test_engine.test_search_no_match()
    test_engine.test_search_top_n_limit()
    print("   ✅ 边界情况测试通过")
    
    # 数据格式测试
    print("5. 测试数据格式...")
    test_engine.test_search_score_positive()
    test_engine.test_search_coordinates()
    print("   ✅ 数据格式测试通过")
    
    # 集成测试
    print("6. 运行集成测试...")
    test_search_engine_integration()
    test_bm25_parameters()
    print("   ✅ 集成测试通过")
    
    print("\n🎉 所有测试通过！搜索引擎功能正常。")
    
    # 演示搜索功能
    print("\n📋 搜索功能演示:")
    engine = test_engine.engine
    
    test_queries = ["图书馆", "安全", "学生", "校园", "不存在的词"]
    
    for query in test_queries:
        results = engine.search(query, top_n=3)
        print(f"\n查询: '{query}'")
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']} (分数: {result['score']:.4f})")
        else:
            print("  无匹配结果")