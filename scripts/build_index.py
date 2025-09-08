#!/usr/bin/env python3
"""
FAISS 索引构建脚本
从知识库数据构建向量索引，支持 CLI 使用和测试
"""

import sys
import os
import argparse
import logging
import json
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.services.embedder import EmbeddingService, create_embedding_service
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所需依赖: pip install sentence-transformers faiss-cpu numpy")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IndexBuilder:
    """索引构建器"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5", 
                 chunk_size: int = 550, overlap: int = 100):
        """
        初始化索引构建器
        
        Args:
            model_name: 嵌入模型名称
            chunk_size: 文本分块大小 (400-700)
            overlap: 重叠大小 (80-120)
        """
        self.service = create_embedding_service(
            model_name=model_name,
            chunk_size=chunk_size,
            overlap=overlap
        )
        logger.info(f"索引构建器初始化: model={model_name}, chunk_size={chunk_size}, overlap={overlap}")
    
    def load_knowledge_data(self, data_path: str) -> List[Dict[str, Any]]:
        """
        加载知识库数据
        
        Args:
            data_path: 数据文件路径 (支持 .jsonl 和 .json)
            
        Returns:
            List[Dict]: 知识库数据列表
        """
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"数据文件不存在: {data_path}")
        
        data = []
        
        if data_path.endswith('.jsonl'):
            # 读取 JSONL 格式
            with open(data_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            item = json.loads(line)
                            data.append(item)
                        except json.JSONDecodeError as e:
                            logger.warning(f"第 {line_num} 行 JSON 解析失败: {e}")
        
        elif data_path.endswith('.json'):
            # 读取 JSON 格式
            with open(data_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                if isinstance(json_data, list):
                    data = json_data
                else:
                    data = [json_data]
        
        else:
            raise ValueError(f"不支持的文件格式: {data_path}")
        
        logger.info(f"加载知识库数据: {len(data)} 条记录")
        return data
    
    def extract_texts_from_knowledge(self, knowledge_data: List[Dict[str, Any]]) -> tuple:
        """
        从知识库数据中提取文本
        
        Args:
            knowledge_data: 知识库数据列表
            
        Returns:
            tuple: (texts, sources, metadata_list)
        """
        texts = []
        sources = []
        metadata_list = []
        
        for item in knowledge_data:
            # 提取文本内容
            text_content = ""
            if 'content' in item:
                text_content = str(item['content'])
            elif 'text' in item:
                text_content = str(item['text'])
            elif 'description' in item:
                text_content = str(item['description'])
            else:
                # 尝试从其他字段提取文本
                for key, value in item.items():
                    if isinstance(value, str) and len(value) > 20:
                        text_content = value
                        break
            
            if not text_content.strip():
                logger.warning(f"跳过空文本记录: {item}")
                continue
            
            # 提取来源
            source = item.get('task_id', item.get('id', item.get('source', 'unknown')))
            
            # 提取元数据
            metadata = {k: v for k, v in item.items() if k not in ['content', 'text', 'description']}
            
            texts.append(text_content)
            sources.append(str(source))
            metadata_list.append(metadata)
        
        logger.info(f"提取文本完成: {len(texts)} 个有效文本")
        return texts, sources, metadata_list
    
    def build_index(self, data_path: str, output_path: str = "data/index") -> str:
        """
        构建索引
        
        Args:
            data_path: 知识库数据路径
            output_path: 输出路径 (不含扩展名)
            
        Returns:
            str: 索引文件路径
        """
        logger.info(f"开始构建索引: {data_path} -> {output_path}")
        
        # 加载数据
        knowledge_data = self.load_knowledge_data(data_path)
        
        # 提取文本
        texts, sources, metadata_list = self.extract_texts_from_knowledge(knowledge_data)
        
        if not texts:
            raise ValueError("没有找到有效的文本数据")
        
        # 构建索引
        logger.info("开始构建向量索引...")
        index = self.service.build_index_from_texts(texts, sources, metadata_list)
        
        # 保存索引
        output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else "."
        os.makedirs(output_dir, exist_ok=True)
        index_path, metadata_path = self.service.save_index(output_path)
        
        logger.info(f"索引构建完成: {index_path}")
        return index_path
    
    def test_index(self, index_path: str, test_queries: List[str] = None, 
                   top_k: int = 4, min_similarity: float = 0.35) -> Dict[str, Any]:
        """
        测试索引
        
        Args:
            index_path: 索引路径 (不含扩展名)
            test_queries: 测试查询列表
            top_k: 返回结果数量
            min_similarity: 最小相似度阈值
            
        Returns:
            Dict: 测试结果
        """
        logger.info(f"开始测试索引: {index_path}")
        
        # 加载索引
        self.service.load_index(index_path)
        
        # 默认测试查询
        if test_queries is None:
            test_queries = [
                "图书馆在哪里",
                "如何使用实验室设备",
                "学生活动中心的开放时间",
                "计算机科学课程",
                "校园安全规定"
            ]
        
        test_results = {
            'total_queries': len(test_queries),
            'successful_queries': 0,
            'average_similarity': 0.0,
            'results': []
        }
        
        total_similarity = 0.0
        successful_count = 0
        
        for query in test_queries:
            logger.info(f"测试查询: {query}")
            
            try:
                results = self.service.search(query, top_k=top_k, min_similarity=min_similarity)
                
                query_result = {
                    'query': query,
                    'results_count': len(results),
                    'max_similarity': max([r.similarity for r in results]) if results else 0.0,
                    'results': [
                        {
                            'text': r.text[:200] + '...' if len(r.text) > 200 else r.text,
                            'similarity': r.similarity,
                            'source': r.source
                        }
                        for r in results
                    ]
                }
                
                test_results['results'].append(query_result)
                
                if results:
                    successful_count += 1
                    total_similarity += query_result['max_similarity']
                    
                    print(f"✅ 查询: {query}")
                    print(f"   找到 {len(results)} 个结果, 最高相似度: {query_result['max_similarity']:.3f}")
                    for i, result in enumerate(results[:2], 1):
                        print(f"   [{i}] {result.similarity:.3f} - {result.text[:100]}...")
                else:
                    print(f"❌ 查询: {query} - 未找到满足阈值的结果")
                
                print()
                
            except Exception as e:
                logger.error(f"查询失败: {query}, 错误: {str(e)}")
                query_result = {
                    'query': query,
                    'error': str(e),
                    'results_count': 0,
                    'max_similarity': 0.0,
                    'results': []
                }
                test_results['results'].append(query_result)
        
        test_results['successful_queries'] = successful_count
        test_results['average_similarity'] = total_similarity / successful_count if successful_count > 0 else 0.0
        
        # 输出测试总结
        print("📊 测试总结")
        print("=" * 50)
        print(f"总查询数: {test_results['total_queries']}")
        print(f"成功查询数: {test_results['successful_queries']}")
        print(f"成功率: {test_results['successful_queries'] / test_results['total_queries'] * 100:.1f}%")
        print(f"平均相似度: {test_results['average_similarity']:.3f}")
        print(f"相似度阈值: {min_similarity}")
        
        # 验证是否满足要求
        meets_requirements = (
            test_results['successful_queries'] > 0 and
            test_results['average_similarity'] >= min_similarity
        )
        
        if meets_requirements:
            print("✅ 测试通过: 满足相似度要求")
        else:
            print("❌ 测试未通过: 未满足相似度要求")
        
        return test_results

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="FAISS 索引构建和测试工具")
    
    parser.add_argument('--data', '-d', required=True, 
                       help='知识库数据文件路径 (.json 或 .jsonl)')
    parser.add_argument('--output', '-o', default='data/index',
                       help='输出索引路径 (不含扩展名, 默认: data/index)')
    parser.add_argument('--model', '-m', default='BAAI/bge-small-zh-v1.5',
                       help='嵌入模型名称 (默认: BAAI/bge-small-zh-v1.5)')
    parser.add_argument('--chunk-size', type=int, default=550,
                       help='文本分块大小 (400-700, 默认: 550)')
    parser.add_argument('--overlap', type=int, default=100,
                       help='分块重叠大小 (80-120, 默认: 100)')
    parser.add_argument('--test', action='store_true',
                       help='构建后进行测试')
    parser.add_argument('--test-only', action='store_true',
                       help='仅测试现有索引 (需要 --index 参数)')
    parser.add_argument('--index', help='现有索引路径 (用于 --test-only)')
    parser.add_argument('--top-k', type=int, default=4,
                       help='搜索返回结果数量 (默认: 4)')
    parser.add_argument('--min-similarity', type=float, default=0.35,
                       help='最小相似度阈值 (默认: 0.35)')
    parser.add_argument('--queries', nargs='+',
                       help='自定义测试查询')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 验证参数
    if args.chunk_size < 400 or args.chunk_size > 700:
        print("错误: chunk-size 必须在 400-700 之间")
        sys.exit(1)
    
    if args.overlap < 80 or args.overlap > 120:
        print("错误: overlap 必须在 80-120 之间")
        sys.exit(1)
    
    try:
        # 创建索引构建器
        builder = IndexBuilder(
            model_name=args.model,
            chunk_size=args.chunk_size,
            overlap=args.overlap
        )
        
        if args.test_only:
            # 仅测试模式
            if not args.index:
                print("错误: --test-only 模式需要 --index 参数")
                sys.exit(1)
            
            test_results = builder.test_index(
                args.index,
                test_queries=args.queries,
                top_k=args.top_k,
                min_similarity=args.min_similarity
            )
            
        else:
            # 构建索引
            print(f"🔧 开始构建索引")
            print(f"数据文件: {args.data}")
            print(f"输出路径: {args.output}")
            print(f"模型: {args.model}")
            print(f"分块大小: {args.chunk_size}, 重叠: {args.overlap}")
            print("=" * 60)
            
            index_path = builder.build_index(args.data, args.output)
            
            print(f"✅ 索引构建完成: {index_path}")
            
            # 可选测试
            if args.test:
                print("\n🧪 开始测试索引...")
                test_results = builder.test_index(
                    args.output,
                    test_queries=args.queries,
                    top_k=args.top_k,
                    min_similarity=args.min_similarity
                )
        
        print("\n🎉 操作完成!")
        
    except Exception as e:
        logger.error(f"操作失败: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()