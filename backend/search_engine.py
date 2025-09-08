"""
任务搜索引擎 - BM25 算法实现
"""
import math
import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class BM25SearchEngine:
    """BM25 搜索引擎"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        初始化 BM25 搜索引擎
        
        Args:
            k1: 控制词频饱和度的参数，通常在 1.2-2.0 之间
            b: 控制文档长度归一化的参数，通常在 0.75 左右
        """
        self.k1 = k1
        self.b = b
        self.documents = []  # 存储文档
        self.doc_freqs = defaultdict(int)  # 词汇在多少个文档中出现
        self.idf = {}  # 逆文档频率
        self.doc_len = []  # 每个文档的长度
        self.avgdl = 0  # 平均文档长度
        self.corpus_size = 0  # 语料库大小
        self.indexed = False
        
    def tokenize(self, text: str) -> List[str]:
        """
        文本分词
        
        Args:
            text: 输入文本
            
        Returns:
            分词结果列表
        """
        if not text:
            return []
            
        # 转换为小写
        text = text.lower()
        
        # 使用正则表达式分词，支持中英文
        # 匹配中文字符、英文单词、数字
        tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', text)
        
        # 对中文和英文都进行处理
        result = []
        for token in tokens:
            if re.match(r'[\u4e00-\u9fff]+', token):
                # 中文：只进行字符级分词
                result.extend(list(token))
            else:
                # 英文单词保持完整
                result.append(token)
                
        return result
    
    def build_index(self, documents: List[Dict[str, Any]]):
        """
        构建搜索索引
        
        Args:
            documents: 文档列表，每个文档包含 task_id, title, description 等字段
        """
        logger.info(f"开始构建搜索索引，文档数量: {len(documents)}")
        
        self.documents = documents
        self.corpus_size = len(documents)
        self.doc_freqs = defaultdict(int)
        self.doc_len = []
        
        # 统计词频和文档长度
        for doc in documents:
            # 合并标题和描述作为搜索内容
            content = f"{doc.get('title', '')} {doc.get('description', '')}"
            tokens = self.tokenize(content)
            self.doc_len.append(len(tokens))
            
            # 统计词汇在文档中的出现
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] += 1
        
        # 计算平均文档长度
        self.avgdl = sum(self.doc_len) / len(self.doc_len) if self.doc_len else 0
        
        # 计算 IDF
        for token, freq in self.doc_freqs.items():
            # 使用标准的IDF公式: log(N / df)，为常见词汇添加最小值
            idf_value = math.log(self.corpus_size / freq)
            self.idf[token] = max(0.1, idf_value)  # 最小IDF值为0.1
        
        self.indexed = True
        logger.info(f"搜索索引构建完成，词汇数量: {len(self.idf)}")
    
    def get_bm25_score(self, query_tokens: List[str], doc_index: int) -> float:
        """
        计算 BM25 分数
        
        Args:
            query_tokens: 查询词列表
            doc_index: 文档索引
            
        Returns:
            BM25 分数
        """
        if not self.indexed:
            return 0.0
            
        doc = self.documents[doc_index]
        content = f"{doc.get('title', '')} {doc.get('description', '')}"
        doc_tokens = self.tokenize(content)
        doc_token_counts = Counter(doc_tokens)
        doc_length = self.doc_len[doc_index]
        
        score = 0.0
        matched_tokens = 0
        
        for token in query_tokens:
            # 如果词汇不在索引中，跳过
            if token not in self.idf:
                continue
                
            # 词频
            tf = doc_token_counts.get(token, 0)
            if tf == 0:
                continue
                
            matched_tokens += 1
            
            # IDF
            idf = self.idf[token]
            
            # BM25 公式
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avgdl))
            score += idf * (numerator / denominator)
        
        # 如果没有匹配的词汇，返回0
        if matched_tokens == 0:
            return 0.0
            
        return score
    
    def search(self, query: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            top_n: 返回结果数量
            
        Returns:
            搜索结果列表，包含 task_id, title, score, lat, lng
        """
        if not self.indexed or not query.strip():
            return []
            
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []
            
        logger.info(f"执行搜索，查询: '{query}', 分词结果: {query_tokens}")
        
        # 计算每个文档的 BM25 分数
        scores = []
        for i, doc in enumerate(self.documents):
            score = self.get_bm25_score(query_tokens, i)
            
            # 计算匹配度：匹配的查询词数量 / 总查询词数量
            content = f"{doc.get('title', '')} {doc.get('description', '')}"
            doc_tokens = set(self.tokenize(content))
            matched_query_tokens = set(query_tokens) & doc_tokens
            match_ratio = len(matched_query_tokens) / len(set(query_tokens)) if query_tokens else 0
            
            # 严格的匹配要求：
            # 1. 分数必须大于0
            # 2. 必须有匹配的词汇
            # 3. 对于包含英文的查询，匹配度要求更高
            has_english = any(token.isalpha() and token.isascii() for token in query_tokens)
            min_match_ratio = 0.8 if has_english else 0.3
            
            if score > 0 and len(matched_query_tokens) > 0 and match_ratio >= min_match_ratio:
                scores.append({
                    'task_id': doc.get('task_id', ''),
                    'title': doc.get('title', ''),
                    'score': round(score, 4),
                    'lat': doc.get('location_lat', 0.0),
                    'lng': doc.get('location_lng', 0.0)
                })
        
        # 按分数降序排序
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回前 N 个结果
        results = scores[:top_n]
        logger.info(f"搜索完成，返回 {len(results)} 个结果")
        
        return results


# 全局搜索引擎实例
search_engine = BM25SearchEngine()


def initialize_search_engine(tasks: List[Dict[str, Any]]):
    """
    初始化搜索引擎
    
    Args:
        tasks: 任务列表
    """
    global search_engine
    try:
        # 转换任务数据格式
        documents = []
        for task in tasks:
            doc = {
                'task_id': getattr(task, 'task_id', ''),
                'title': getattr(task, 'title', ''),
                'description': getattr(task, 'description', ''),
                'location_lat': getattr(task, 'location_lat', 0.0),
                'location_lng': getattr(task, 'location_lng', 0.0)
            }
            documents.append(doc)
        
        search_engine.build_index(documents)
        logger.info("搜索引擎初始化成功")
        return True
    except Exception as e:
        logger.error(f"搜索引擎初始化失败: {e}")
        return False


def search_tasks(query: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    搜索任务
    
    Args:
        query: 搜索查询
        top_n: 返回结果数量
        
    Returns:
        搜索结果列表
    """
    global search_engine
    return search_engine.search(query, top_n)