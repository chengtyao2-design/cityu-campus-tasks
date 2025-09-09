#!/usr/bin/env python3
"""
向量嵌入服务模块
提供文本分块、BGE-small-zh 嵌入和 FAISS 索引功能
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import faiss
from sentence_transformers import SentenceTransformer
import re
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """文本块数据类"""
    chunk_id: str
    text: str
    source: str
    metadata: Dict[str, Any]
    start_pos: int = 0
    end_pos: int = 0

@dataclass
class SearchResult:
    """搜索结果数据类"""
    chunk_id: str
    text: str
    similarity: float
    source: str
    metadata: Dict[str, Any]

class TextChunker:
    """文本分块器"""
    
    def __init__(self, chunk_size: int = 550, overlap: int = 100):
        """
        初始化文本分块器
        
        Args:
            chunk_size: 分块大小 (400-700)
            overlap: 重叠大小 (80-120)
        """
        self.chunk_size = max(400, min(700, chunk_size))
        self.overlap = max(80, min(120, overlap))
        logger.info(f"文本分块器初始化: chunk_size={self.chunk_size}, overlap={self.overlap}")
    
    def chunk_text(self, text: str, source: str = "", metadata: Dict[str, Any] = None) -> List[TextChunk]:
        """
        将文本分块
        
        Args:
            text: 输入文本
            source: 文本来源
            metadata: 元数据
            
        Returns:
            List[TextChunk]: 文本块列表
        """
        if not text or not text.strip():
            return []
        
        if metadata is None:
            metadata = {}
        
        text = text.strip()
        chunks = []
        
        # 如果文本长度小于分块大小，直接返回
        if len(text) <= self.chunk_size:
            chunk = TextChunk(
                chunk_id=f"{source}_0",
                text=text,
                source=source,
                metadata=metadata,
                start_pos=0,
                end_pos=len(text)
            )
            chunks.append(chunk)
            return chunks
        
        # 分块处理
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # 如果不是最后一块，尝试在句子边界分割
            if end < len(text):
                # 寻找句子结束符
                sentence_ends = []
                for i, char in enumerate(text[start:end]):
                    if char in '。！？.!?':
                        sentence_ends.append(start + i + 1)
                
                # 如果找到句子边界，在最后一个句子边界分割
                if sentence_ends:
                    end = sentence_ends[-1]
                # 否则寻找标点符号
                elif '，' in text[start:end] or ',' in text[start:end]:
                    for i in range(end - start - 1, -1, -1):
                        if text[start + i] in '，,':
                            end = start + i + 1
                            break
                # 最后寻找空格
                elif ' ' in text[start:end]:
                    for i in range(end - start - 1, -1, -1):
                        if text[start + i] == ' ':
                            end = start + i
                            break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk = TextChunk(
                    chunk_id=f"{source}_{chunk_index}",
                    text=chunk_text,
                    source=source,
                    metadata=metadata,
                    start_pos=start,
                    end_pos=end
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # 计算下一个起始位置（考虑重叠）
            start = max(start + 1, end - self.overlap)
            
            # 避免无限循环
            if start >= len(text):
                break
        
        logger.debug(f"文本分块完成: {len(chunks)} 个块, 来源: {source}")
        return chunks

class BGEEmbedder:
    """BGE-small-zh 嵌入模型"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """
        初始化 BGE 嵌入模型
        
        Args:
            model_name: 模型名称
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 512  # BGE-small-zh 的嵌入维度
        
    def load_model(self):
        """加载嵌入模型"""
        try:
            logger.info(f"正在加载嵌入模型: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"嵌入模型加载成功, 维度: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {str(e)}")
            # 回退到简单的模型
            logger.info("尝试使用备用模型...")
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"备用模型加载成功, 维度: {self.embedding_dim}")
            except Exception as e2:
                logger.error(f"备用模型也加载失败: {str(e2)}")
                raise e2
    
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        编码文本为向量
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
            
        Returns:
            np.ndarray: 嵌入向量矩阵
        """
        if self.model is None:
            self.load_model()
        
        if not texts:
            return np.array([]).reshape(0, self.embedding_dim)
        
        try:
            logger.debug(f"开始编码 {len(texts)} 个文本")
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 100,
                convert_to_numpy=True,
                normalize_embeddings=True  # 归一化嵌入向量
            )
            logger.debug(f"文本编码完成, 形状: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"文本编码失败: {str(e)}")
            raise

class FAISSIndex:
    """FAISS 向量索引"""
    
    def __init__(self, embedding_dim: int = 512):
        """
        初始化 FAISS 索引
        
        Args:
            embedding_dim: 嵌入向量维度
        """
        self.embedding_dim = embedding_dim
        self.index = None
        self.chunks = []  # 存储文本块
        self.chunk_id_to_idx = {}  # chunk_id 到索引的映射
        
    def build_index(self, chunks: List[TextChunk], embeddings: np.ndarray):
        """
        构建 FAISS 索引
        
        Args:
            chunks: 文本块列表
            embeddings: 嵌入向量矩阵
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"文本块数量 ({len(chunks)}) 与嵌入向量数量 ({len(embeddings)}) 不匹配")
        
        logger.info(f"开始构建 FAISS 索引: {len(chunks)} 个向量, 维度: {self.embedding_dim}")
        
        # 创建 FAISS 索引 (使用 L2 距离)
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # 添加向量到索引
        if len(embeddings) > 0:
            embeddings = embeddings.astype(np.float32)
            self.index.add(embeddings)
        
        # 存储文本块和映射
        self.chunks = chunks
        self.chunk_id_to_idx = {chunk.chunk_id: i for i, chunk in enumerate(chunks)}
        
        logger.info(f"FAISS 索引构建完成: {self.index.ntotal} 个向量")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 4, min_similarity: float = 0.35) -> List[SearchResult]:
        """
        搜索相似向量
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            min_similarity: 最小相似度阈值
            
        Returns:
            List[SearchResult]: 搜索结果列表
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("索引为空或未构建")
            return []
        
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        
        # 搜索最相似的向量
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS 返回 -1 表示无效结果
                continue
            
            # 将 L2 距离转换为余弦相似度
            # 由于向量已归一化，L2距离 = 2 * (1 - 余弦相似度)
            similarity = max(0.0, 1.0 - distance / 2.0)
            
            if similarity >= min_similarity:
                chunk = self.chunks[idx]
                result = SearchResult(
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    similarity=similarity,
                    source=chunk.source,
                    metadata=chunk.metadata
                )
                results.append(result)
        
        logger.debug(f"搜索完成: 返回 {len(results)} 个结果 (阈值: {min_similarity})")
        return results
    
    def save_index(self, index_path: str, metadata_path: str):
        """
        保存索引到文件
        
        Args:
            index_path: 索引文件路径
            metadata_path: 元数据文件路径
        """
        if self.index is None:
            raise ValueError("索引未构建，无法保存")
        
        # 保存 FAISS 索引
        faiss.write_index(self.index, index_path)
        
        # 保存元数据
        metadata = {
            'embedding_dim': self.embedding_dim,
            'total_vectors': self.index.ntotal,
            'chunks': [asdict(chunk) for chunk in self.chunks],
            'chunk_id_to_idx': self.chunk_id_to_idx
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"索引已保存: {index_path}, 元数据: {metadata_path}")
    
    def load_index(self, index_path: str, metadata_path: str):
        """
        从文件加载索引
        
        Args:
            index_path: 索引文件路径
            metadata_path: 元数据文件路径
        """
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(f"索引文件或元数据文件不存在")
        
        # 加载 FAISS 索引
        self.index = faiss.read_index(index_path)
        
        # 加载元数据
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.embedding_dim = metadata['embedding_dim']
        self.chunk_id_to_idx = metadata['chunk_id_to_idx']
        
        # 重建文本块对象
        self.chunks = []
        for chunk_data in metadata['chunks']:
            chunk = TextChunk(**chunk_data)
            self.chunks.append(chunk)
        
        logger.info(f"索引已加载: {self.index.ntotal} 个向量, 维度: {self.embedding_dim}")

class EmbeddingService:
    """嵌入服务主类"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5", chunk_size: int = 550, overlap: int = 100):
        """
        初始化嵌入服务
        
        Args:
            model_name: 嵌入模型名称
            chunk_size: 文本分块大小
            overlap: 分块重叠大小
        """
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)
        self.embedder = BGEEmbedder(model_name=model_name)
        self.index = None
        
        logger.info("嵌入服务初始化完成")
    
    def build_index_from_texts(self, texts: List[str], sources: List[str] = None, 
                              metadata_list: List[Dict[str, Any]] = None) -> FAISSIndex:
        """
        从文本列表构建索引
        
        Args:
            texts: 文本列表
            sources: 来源列表
            metadata_list: 元数据列表
            
        Returns:
            FAISSIndex: 构建的索引
        """
        if not texts:
            raise ValueError("文本列表不能为空")
        
        if sources is None:
            sources = [f"text_{i}" for i in range(len(texts))]
        
        if metadata_list is None:
            metadata_list = [{}] * len(texts)
        
        # 文本分块
        all_chunks = []
        for i, text in enumerate(texts):
            source = sources[i] if i < len(sources) else f"text_{i}"
            metadata = metadata_list[i] if i < len(metadata_list) else {}
            chunks = self.chunker.chunk_text(text, source, metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"文本分块完成: {len(all_chunks)} 个块")
        
        # 提取文本进行嵌入
        chunk_texts = [chunk.text for chunk in all_chunks]
        embeddings = self.embedder.encode_texts(chunk_texts)
        
        # 构建索引
        self.index = FAISSIndex(embedding_dim=self.embedder.embedding_dim)
        self.index.build_index(all_chunks, embeddings)
        
        return self.index
    
    def search(self, query: str, top_k: int = 4, min_similarity: float = 0.35) -> List[SearchResult]:
        """
        搜索相似文本
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            min_similarity: 最小相似度阈值
            
        Returns:
            List[SearchResult]: 搜索结果
        """
        if self.index is None:
            raise ValueError("索引未构建，请先调用 build_index_from_texts")
        
        # 编码查询文本
        query_embedding = self.embedder.encode_texts([query])
        
        # 搜索
        return self.index.search(query_embedding[0], top_k=top_k, min_similarity=min_similarity)
    
    def save_index(self, base_path: str):
        """
        保存索引
        
        Args:
            base_path: 基础路径 (不含扩展名)
        """
        if self.index is None:
            raise ValueError("索引未构建，无法保存")
        
        index_path = f"{base_path}.faiss"
        metadata_path = f"{base_path}.json"
        
        self.index.save_index(index_path, metadata_path)
        return index_path, metadata_path
    
    def load_index(self, base_path: str):
        """
        加载索引
        
        Args:
            base_path: 基础路径 (不含扩展名)
        """
        index_path = f"{base_path}.faiss"
        metadata_path = f"{base_path}.json"
        
        self.index = FAISSIndex()
        self.index.load_index(index_path, metadata_path)
        
        # 确保嵌入模型已加载
        if self.embedder.model is None:
            self.embedder.load_model()

# 便捷函数
def create_embedding_service(model_name: str = "BAAI/bge-small-zh-v1.5", 
                           chunk_size: int = 550, overlap: int = 100) -> EmbeddingService:
    """创建嵌入服务实例"""
    return EmbeddingService(model_name=model_name, chunk_size=chunk_size, overlap=overlap)

if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 测试文本
    test_texts = [
        "香港城市大学是一所位于香港九龙塘的公立研究型大学。学校成立于1984年，是香港八所受政府大学教育资助委员会资助并可颁授学位的高等教育院校之一。",
        "计算机科学系提供本科和研究生课程，涵盖人工智能、数据科学、软件工程等领域。学生可以参与各种研究项目和实习机会。",
        "校园内有现代化的图书馆、实验室和体育设施。邵逸夫图书馆是学生学习和研究的重要场所，提供丰富的学术资源。"
    ]
    
    print("🔧 嵌入服务测试")
    print("=" * 50)
    
    # 创建服务
    service = create_embedding_service()
    
    # 构建索引
    print("📚 构建索引...")
    index = service.build_index_from_texts(test_texts)
    
    # 测试搜索
    queries = ["图书馆在哪里", "计算机专业", "香港城市大学"]
    
    for query in queries:
        print(f"\n🔍 查询: {query}")
        results = service.search(query, top_k=2, min_similarity=0.3)
        
        for i, result in enumerate(results, 1):
            print(f"  [{i}] 相似度: {result.similarity:.3f}")
            print(f"      文本: {result.text[:100]}...")
            print(f"      来源: {result.source}")
    
    print("\n✅ 测试完成!")