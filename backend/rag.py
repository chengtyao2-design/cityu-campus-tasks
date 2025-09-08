"""
RAG (Retrieval-Augmented Generation) 系统实现
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import re

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """RAG 检索结果"""
    answer: str
    citations: List[Dict[str, Any]]
    map_anchor: Dict[str, float]
    suggestions: Optional[List[Dict[str, Any]]] = None
    uncertain_reason: Optional[str] = None


class KnowledgeRetriever:
    """知识库检索器"""
    
    def __init__(self, embedding_service=None):
        """
        初始化知识库检索器
        
        Args:
            embedding_service: 嵌入服务实例
        """
        self.embedding_service = embedding_service
        self.knowledge_base = {}  # task_id -> knowledge
        
    def load_knowledge_base(self, knowledge_data: Dict[str, Any]):
        """
        加载知识库数据
        
        Args:
            knowledge_data: 知识库数据字典
        """
        self.knowledge_base = knowledge_data
        logger.info(f"知识库加载完成，任务数量: {len(self.knowledge_base)}")
    
    def retrieve_task_knowledge(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        检索指定任务的知识库信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            知识库信息或 None
        """
        knowledge_obj = self.knowledge_base.get(task_id)
        if knowledge_obj is None:
            return None
        
        # 如果已经是字典，直接返回
        if isinstance(knowledge_obj, dict):
            return knowledge_obj
        
        # 将 TaskKnowledge 对象转换为字典
        try:
            # 尝试使用 dataclass 的 asdict
            from dataclasses import asdict
            return asdict(knowledge_obj)
        except:
            # 手动转换
            return {
                'task_id': getattr(knowledge_obj, 'task_id', ''),
                'knowledge_type': getattr(knowledge_obj, 'knowledge_type', ''),
                'content': getattr(knowledge_obj, 'content', ''),
                'title': getattr(knowledge_obj, 'title', ''),
                'tags': getattr(knowledge_obj, 'tags', []),
                'difficulty_level': getattr(knowledge_obj, 'difficulty', 'beginner'),
                'estimated_read_time': getattr(knowledge_obj, 'estimated_time', 0),
                'course_code': getattr(knowledge_obj, 'course_code', ''),
            }
    
    def search_relevant_chunks(self, task_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        搜索相关知识片段
        
        Args:
            task_id: 任务ID
            query: 查询文本
            top_k: 返回片段数量
            
        Returns:
            相关知识片段列表
        """
        knowledge = self.retrieve_task_knowledge(task_id)
        if not knowledge:
            return []
        
        # 简单的关键词匹配（如果没有嵌入服务）
        if not self.embedding_service:
            return self._keyword_search(knowledge, query, top_k)
        
        # 使用嵌入服务进行语义搜索
        try:
            # 这里可以集成之前实现的嵌入服务
            return self._semantic_search(knowledge, query, top_k)
        except Exception as e:
            logger.warning(f"语义搜索失败，回退到关键词搜索: {e}")
            return self._keyword_search(knowledge, query, top_k)
    
    def _keyword_search(self, knowledge: Dict[str, Any], query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        基于关键词的搜索
        
        Args:
            knowledge: 知识库条目
            query: 查询文本
            top_k: 返回数量
            
        Returns:
            匹配的知识片段
        """
        content = knowledge.get('content', '')
        title = knowledge.get('title', '')
        
        # 简单的关键词匹配评分（支持中文）
        import re
        
        def extract_terms(text):
            # 提取中文字符和英文单词
            chinese_chars = set(re.findall(r'[\u4e00-\u9fff]', text.lower()))
            english_words = set(re.findall(r'[a-zA-Z]+', text.lower()))
            return chinese_chars.union(english_words)
        
        query_terms = extract_terms(query)
        content_terms = extract_terms(content)
        title_terms = extract_terms(title)
        
        # 计算匹配分数
        content_score = len(query_terms.intersection(content_terms))
        title_score = len(query_terms.intersection(title_terms)) * 2  # 标题权重更高
        total_score = content_score + title_score
        
        if total_score > 0:
            # 分割内容为片段
            chunks = self._split_content(content)
            
            # 为每个片段评分
            scored_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_terms = extract_terms(chunk)
                chunk_score = len(query_terms.intersection(chunk_terms))
                
                if chunk_score > 0:
                    scored_chunks.append({
                        'content': chunk,
                        'score': chunk_score,
                        'source': knowledge.get('title', ''),
                        'chunk_id': i
                    })
            
            # 按分数排序并返回前 top_k 个
            scored_chunks.sort(key=lambda x: x['score'], reverse=True)
            return scored_chunks[:top_k]
        
        return []
    
    def _semantic_search(self, knowledge: Dict[str, Any], query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        基于语义的搜索（预留接口）
        
        Args:
            knowledge: 知识库条目
            query: 查询文本
            top_k: 返回数量
            
        Returns:
            匹配的知识片段
        """
        # 这里可以集成嵌入服务进行语义搜索
        # 目前回退到关键词搜索
        return self._keyword_search(knowledge, query, top_k)
    
    def _split_content(self, content: str, chunk_size: int = 200) -> List[str]:
        """
        将内容分割为片段
        
        Args:
            content: 原始内容
            chunk_size: 片段大小
            
        Returns:
            内容片段列表
        """
        if not content:
            return []
        
        # 按句号分割
        sentences = re.split(r'[。！？\n]', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk + sentence) <= chunk_size:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [content[:chunk_size]]


class PromptTemplate:
    """提示词模板"""
    
    SYSTEM_PROMPT = """你是香港城市大学校园任务系统的智能助手。你的职责是帮助学生完成校园任务，提供准确、有用的信息和指导。

## 角色设定
- 你是一个友好、专业的校园助手
- 你熟悉香港城市大学的校园环境和各种任务
- 你会基于提供的知识库信息回答问题
- 你会诚实地承认不确定的信息

## 回答原则
1. 基于提供的知识库信息回答问题
2. 如果信息不足，明确说明不确定的原因
3. 提供具体、可操作的建议
4. 保持友好、专业的语调
5. 如果问题超出当前任务范围，建议相关任务

## 输出格式
请严格按照以下 JSON 格式回答：
{
  "answer": "你的详细回答",
  "confidence": "high/medium/low",
  "key_points": ["要点1", "要点2"],
  "actionable_steps": ["步骤1", "步骤2"],
  "uncertain_aspects": ["不确定的方面1", "不确定的方面2"]
}"""

    USER_PROMPT_TEMPLATE = """## 当前任务信息
任务ID: {task_id}
任务标题: {task_title}
任务描述: {task_description}
任务位置: {task_location}

## 相关知识库信息
{knowledge_context}

## 用户问题
{user_question}

请基于上述信息回答用户问题。如果知识库信息不足以完全回答问题，请在 uncertain_aspects 中说明。"""

    @classmethod
    def format_user_prompt(cls, task_info: Dict[str, Any], knowledge_chunks: List[Dict[str, Any]], user_question: str) -> str:
        """
        格式化用户提示词
        
        Args:
            task_info: 任务信息
            knowledge_chunks: 知识片段
            user_question: 用户问题
            
        Returns:
            格式化的提示词
        """
        # 格式化知识库上下文
        knowledge_context = ""
        for i, chunk in enumerate(knowledge_chunks, 1):
            knowledge_context += f"\n### 知识片段 {i}\n"
            knowledge_context += f"来源: {chunk.get('source', '未知')}\n"
            knowledge_context += f"内容: {chunk.get('content', '')}\n"
            knowledge_context += f"相关性分数: {chunk.get('score', 0)}\n"
        
        if not knowledge_context.strip():
            knowledge_context = "暂无相关知识库信息"
        
        return cls.USER_PROMPT_TEMPLATE.format(
            task_id=task_info.get('task_id', ''),
            task_title=task_info.get('title', ''),
            task_description=task_info.get('description', ''),
            task_location=task_info.get('location_name', ''),
            knowledge_context=knowledge_context,
            user_question=user_question
        )


class MockLLMService:
    """模拟 LLM 服务（用于测试）"""
    
    def __init__(self):
        self.responses = {
            "default": {
                "answer": "根据提供的信息，我可以为您提供以下建议和指导。",
                "confidence": "medium",
                "key_points": ["基于知识库信息", "提供实用建议"],
                "actionable_steps": ["查看任务详情", "按照指导完成"],
                "uncertain_aspects": []
            },
            "图书馆": {
                "answer": "关于图书馆文献检索任务，您需要掌握以下要点：1. 熟悉图书馆的数据库系统；2. 学会使用关键词搜索；3. 了解文献分类方法。建议您先到邵逸夫图书馆熟悉环境，然后在工作人员指导下完成检索练习。",
                "confidence": "high",
                "key_points": ["数据库使用", "关键词搜索", "文献分类"],
                "actionable_steps": ["前往邵逸夫图书馆", "咨询工作人员", "完成检索练习"],
                "uncertain_aspects": []
            },
            "安全": {
                "answer": "实验室安全培训是非常重要的必修环节。培训内容包括：1. 实验室基本安全规范；2. 设备操作注意事项；3. 应急处理程序。请务必认真参加培训并通过考核，这关系到您和他人的安全。",
                "confidence": "high",
                "key_points": ["安全规范", "设备操作", "应急处理"],
                "actionable_steps": ["参加安全培训", "认真学习规范", "通过安全考核"],
                "uncertain_aspects": []
            }
        }
    
    def generate_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        生成模拟响应
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Returns:
            模拟的 LLM 响应
        """
        # 简单的关键词匹配来选择响应
        for keyword, response in self.responses.items():
            if keyword != "default" and keyword in user_prompt:
                return response
        
        return self.responses["default"]


class RAGService:
    """RAG 服务主类"""
    
    def __init__(self, knowledge_retriever: KnowledgeRetriever, llm_service=None):
        """
        初始化 RAG 服务
        
        Args:
            knowledge_retriever: 知识检索器
            llm_service: LLM 服务（可选，默认使用模拟服务）
        """
        self.retriever = knowledge_retriever
        self.llm_service = llm_service or MockLLMService()
        self.prompt_template = PromptTemplate()
    
    def process_chat_request(self, task_id: str, user_question: str, task_info: Dict[str, Any]) -> RAGResult:
        """
        处理聊天请求
        
        Args:
            task_id: 任务ID
            user_question: 用户问题
            task_info: 任务信息
            
        Returns:
            RAG 处理结果
        """
        try:
            # 1. 检索相关知识
            logger.info(f"检索任务 {task_id} 的相关知识")
            knowledge_chunks = self.retriever.search_relevant_chunks(task_id, user_question, top_k=3)
            
            # 2. 构建提示词
            user_prompt = self.prompt_template.format_user_prompt(
                task_info, knowledge_chunks, user_question
            )
            
            # 3. 调用 LLM
            logger.info(f"调用 LLM 生成回答")
            llm_response = self.llm_service.generate_response(
                self.prompt_template.SYSTEM_PROMPT,
                user_prompt
            )
            
            # 4. 构建引用信息
            citations = []
            for chunk in knowledge_chunks:
                citations.append({
                    "source": chunk.get('source', ''),
                    "content": chunk.get('content', '')[:100] + "...",
                    "score": chunk.get('score', 0)
                })
            
            # 5. 构建地图锚点
            map_anchor = {
                "lat": task_info.get('location_lat', 0.0),
                "lng": task_info.get('location_lng', 0.0)
            }
            
            # 6. 处理不确定性
            uncertain_reason = None
            if llm_response.get('confidence') == 'low' or llm_response.get('uncertain_aspects'):
                uncertain_reason = "知识库信息不足，建议咨询相关工作人员或查看更多资料"
            
            # 7. 构建建议（如果需要）
            suggestions = None
            if not knowledge_chunks or llm_response.get('confidence') == 'low':
                suggestions = self._generate_suggestions(user_question, task_info)
            
            return RAGResult(
                answer=llm_response.get('answer', '抱歉，我无法回答这个问题。'),
                citations=citations,
                map_anchor=map_anchor,
                suggestions=suggestions,
                uncertain_reason=uncertain_reason
            )
            
        except Exception as e:
            logger.error(f"RAG 处理失败: {e}")
            return RAGResult(
                answer="抱歉，处理您的问题时出现了错误，请稍后重试。",
                citations=[],
                map_anchor={"lat": 0.0, "lng": 0.0},
                uncertain_reason="系统处理错误"
            )
    
    def _generate_suggestions(self, user_question: str, task_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成相关建议
        
        Args:
            user_question: 用户问题
            task_info: 任务信息
            
        Returns:
            建议列表
        """
        suggestions = []
        
        # 基于任务类别的建议
        category = task_info.get('category', '')
        if category == 'academic':
            suggestions.append({
                "type": "related_task",
                "title": "学术研究方法指导",
                "description": "了解更多学术研究相关的任务和资源"
            })
        elif category == 'activity':
            suggestions.append({
                "type": "related_task", 
                "title": "校园活动参与指南",
                "description": "查看更多校园活动和参与方式"
            })
        
        # 通用建议
        suggestions.append({
            "type": "contact",
            "title": "联系相关工作人员",
            "description": "如需更详细信息，建议直接联系任务负责人"
        })
        
        return suggestions


# 全局 RAG 服务实例
rag_service = None


def initialize_rag_service(knowledge_data: Dict[str, Any]) -> bool:
    """
    初始化 RAG 服务
    
    Args:
        knowledge_data: 知识库数据
        
    Returns:
        初始化是否成功
    """
    global rag_service
    try:
        retriever = KnowledgeRetriever()
        retriever.load_knowledge_base(knowledge_data)
        rag_service = RAGService(retriever)
        logger.info("RAG 服务初始化成功")
        return True
    except Exception as e:
        logger.error(f"RAG 服务初始化失败: {e}")
        return False


def process_npc_chat(task_id: str, user_question: str, task_info: Dict[str, Any]) -> RAGResult:
    """
    处理 NPC 聊天请求
    
    Args:
        task_id: 任务ID
        user_question: 用户问题
        task_info: 任务信息
        
    Returns:
        RAG 处理结果
    """
    global rag_service
    if not rag_service:
        raise RuntimeError("RAG 服务未初始化")
    
    return rag_service.process_chat_request(task_id, user_question, task_info)