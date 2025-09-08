"""
NPC 聊天功能测试（pytest 版本）
"""
import sys
import os
import pytest

# 允许从项目根目录运行 pytest 时找到 backend 模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag import (
    KnowledgeRetriever, PromptTemplate, MockLLMService, RAGService,
    initialize_rag_service, process_npc_chat, RAGResult
)


def test_knowledge_retriever():
    """测试知识检索器"""
    retriever = KnowledgeRetriever()
    
    # 测试知识库数据
    test_knowledge = {
        'T001': {
            'knowledge_type': 'guide',
            'title': '图书馆文献检索指南',
            'content': '文献检索步骤：1. 确定检索主题和关键词 2. 选择合适的数据库 3. 构建检索策略 4. 执行检索并筛选结果 5. 评估和整理文献',
            'tags': ['research', 'library', 'database'],
            'difficulty_level': 'beginner',
            'estimated_read_time': 10,
            'prerequisites': None,
            'related_tasks': ['T005', 'T009']
        }
    }
    
    # 加载知识库
    retriever.load_knowledge_base(test_knowledge)
    assert len(retriever.knowledge_base) == 1
    
    # 测试检索单个任务知识
    knowledge = retriever.retrieve_task_knowledge('T001')
    assert knowledge is not None
    assert knowledge['title'] == '图书馆文献检索指南'
    
    # 测试检索不存在的任务
    no_knowledge = retriever.retrieve_task_knowledge('T999')
    assert no_knowledge is None
    
    # 测试相关片段搜索
    chunks = retriever.search_relevant_chunks('T001', '检索步骤', top_k=2)
    assert len(chunks) > 0
    assert chunks[0]['score'] > 0
    
    # 测试空查询
    empty_chunks = retriever.search_relevant_chunks('T001', '', top_k=2)
    assert len(empty_chunks) == 0


def test_prompt_template():
    """测试提示词模板"""
    template = PromptTemplate()
    
    # 测试任务信息
    task_info = {
        'task_id': 'T001',
        'title': '图书馆文献检索',
        'description': '在图书馆完成指定主题的文献检索任务',
        'location_name': '邵逸夫图书馆'
    }
    
    # 测试知识片段
    knowledge_chunks = [
        {
            'source': '图书馆文献检索指南',
            'content': '文献检索步骤：1. 确定检索主题和关键词',
            'score': 0.85
        }
    ]
    
    # 格式化提示词
    user_prompt = template.format_user_prompt(
        task_info, knowledge_chunks, "如何进行文献检索？"
    )
    
    assert 'T001' in user_prompt
    assert '图书馆文献检索' in user_prompt
    assert '邵逸夫图书馆' in user_prompt
    assert '如何进行文献检索？' in user_prompt
    
    # 测试空知识片段
    empty_prompt = template.format_user_prompt(
        task_info, [], "测试问题"
    )
    assert '暂无相关知识库信息' in empty_prompt


def test_mock_llm_service():
    """测试模拟 LLM 服务"""
    llm = MockLLMService()
    
    # 测试默认响应
    response = llm.generate_response("系统提示", "用户问题")
    assert 'answer' in response
    assert 'confidence' in response
    assert 'key_points' in response
    assert 'actionable_steps' in response
    
    # 测试关键词匹配响应
    library_response = llm.generate_response("系统提示", "图书馆相关问题")
    assert library_response['confidence'] == 'high'
    assert '图书馆' in library_response['answer'] or '数据库' in library_response['answer']
    
    # 测试安全相关响应
    safety_response = llm.generate_response("系统提示", "实验室安全问题")
    assert safety_response['confidence'] == 'high'
    assert '安全' in safety_response['answer']


def test_rag_service():
    """测试 RAG 服务"""
    # 创建知识检索器
    retriever = KnowledgeRetriever()
    test_knowledge = {
        'T001': {
            'knowledge_type': 'guide',
            'title': '图书馆文献检索指南',
            'content': '文献检索步骤：1. 确定检索主题和关键词 2. 选择合适的数据库 3. 构建检索策略',
            'tags': ['research', 'library'],
            'difficulty_level': 'beginner',
            'estimated_read_time': 10,
            'prerequisites': None,
            'related_tasks': []
        }
    }
    retriever.load_knowledge_base(test_knowledge)
    
    # 创建 RAG 服务
    rag_service = RAGService(retriever)
    
    # 测试任务信息
    task_info = {
        'task_id': 'T001',
        'title': '图书馆文献检索',
        'description': '在图书馆完成指定主题的文献检索任务',
        'location_name': '邵逸夫图书馆',
        'location_lat': 22.3364,
        'location_lng': 114.2654
    }
    
    # 处理聊天请求
    result = rag_service.process_chat_request('T001', '如何进行文献检索？', task_info)
    
    # 验证结果
    assert isinstance(result, RAGResult)
    assert result.answer
    assert isinstance(result.citations, list)
    assert 'lat' in result.map_anchor
    assert 'lng' in result.map_anchor
    
    # 测试不存在的任务
    no_task_result = rag_service.process_chat_request('T999', '测试问题', task_info)
    assert no_task_result.answer
    assert len(no_task_result.citations) == 0


def test_rag_integration():
    """测试 RAG 集成功能"""
    # 测试知识库数据
    test_knowledge = {
        'T001': {
            'knowledge_type': 'guide',
            'title': '图书馆文献检索指南',
            'content': '文献检索是学术研究的重要技能。主要步骤包括：确定检索主题、选择数据库、构建检索策略、执行检索、筛选结果。',
            'tags': ['research', 'library', 'database'],
            'difficulty_level': 'beginner',
            'estimated_read_time': 10,
            'prerequisites': None,
            'related_tasks': ['T005']
        }
    }
    
    # 初始化 RAG 服务
    success = initialize_rag_service(test_knowledge)
    assert success
    
    # 测试任务信息
    task_info = {
        'task_id': 'T001',
        'title': '图书馆文献检索',
        'description': '学习文献检索技能',
        'location_name': '邵逸夫图书馆',
        'location_lat': 22.3364,
        'location_lng': 114.2654
    }
    
    # 处理聊天请求
    result = process_npc_chat('T001', '请介绍文献检索的步骤', task_info)
    
    # 验证结果
    assert result.answer
    assert len(result.citations) >= 0
    assert result.map_anchor['lat'] == 22.3364
    assert result.map_anchor['lng'] == 114.2654
    
    # 测试跨任务意图检测
    cross_task_result = process_npc_chat('T001', '实验室安全注意事项', task_info)
    assert cross_task_result.answer


@pytest.mark.integration
def test_api_integration():
    """测试 API 集成（服务器未运行时跳过）"""
    import requests

    base_url = "http://localhost:8000"

    # 先探测健康检查，不通过则跳过
    try:
        health = requests.get(f"{base_url}/healthz", timeout=2)
        if health.status_code != 200:
            pytest.skip("后端服务器未运行，跳过 API 集成测试")
    except Exception:
        pytest.skip("无法连接服务器，跳过 API 集成测试")

    # 测试 NPC 聊天端点
    chat_data = {"question": "请介绍一下这个任务的具体要求"}

    response = requests.post(
        f"{base_url}/npc/T001/chat",
        json=chat_data,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("answer", ""), str)
    assert "map_anchor" in data
    assert len(data.get("answer", "")) > 0