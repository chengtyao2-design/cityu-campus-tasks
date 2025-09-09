#!/usr/bin/env python3
"""
性能基准测试脚本
测试API端点的响应时间，验证P95 ≤ 2.5s目标
"""
import asyncio
import time
import statistics
import json
from typing import List, Dict, Any
import httpx
import argparse
from datetime import datetime

# 测试配置
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_CONCURRENT_REQUESTS = 10
DEFAULT_TOTAL_REQUESTS = 100

# 种子数据集
SEED_QUERIES = [
    "图书馆文献检索",
    "实验室安全培训", 
    "学生会议组织",
    "数据结构课程",
    "校园活动参与",
    "安全规范学习",
    "学术研究方法",
    "课程任务完成",
    "志愿服务活动",
    "迎新活动参与"
]

SEED_CHAT_QUESTIONS = [
    "这个任务怎么完成？",
    "需要准备什么材料？",
    "在哪里可以找到相关信息？",
    "有什么注意事项吗？",
    "完成这个任务需要多长时间？",
    "如果遇到问题应该联系谁？",
    "这个任务的难度如何？",
    "有相关的学习资源吗？",
    "完成后如何提交？",
    "是否有截止日期？"
]

TASK_IDS = [
    "T001", "T002", "T003", "T004", "T005",
    "T006", "T007", "T008", "T009", "T010"
]


class PerformanceBenchmark:
    """性能基准测试类"""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url
        self.results = {
            'search_endpoint': [],
            'chat_endpoint': [],
            'list_endpoint': [],
            'detail_endpoint': []
        }
        self.errors = []
    
    async def test_search_endpoint(self, session: httpx.AsyncClient, query: str) -> Dict[str, Any]:
        """测试搜索端点"""
        url = f"{self.base_url}/tasks/search"
        payload = {"query": query, "top_n": 10}
        
        start_time = time.time()
        try:
            response = await session.post(url, json=payload)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'endpoint': 'search',
                    'response_time': response_time,
                    'status': response.status_code,
                    'success': True,
                    'results_count': len(data.get('data', []))
                }
            else:
                return {
                    'endpoint': 'search',
                    'response_time': response_time,
                    'status': response.status_code,
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return {
                'endpoint': 'search',
                'response_time': response_time,
                'status': 0,
                'success': False,
                'error': str(e)
            }
    
    async def test_chat_endpoint(self, session: httpx.AsyncClient, task_id: str, question: str) -> Dict[str, Any]:
        """测试聊天端点"""
        url = f"{self.base_url}/npc/{task_id}/chat"
        payload = {"question": question}
        
        start_time = time.time()
        try:
            response = await session.post(url, json=payload)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'endpoint': 'chat',
                    'response_time': response_time,
                    'status': response.status_code,
                    'success': True,
                    'has_answer': bool(data.get('answer'))
                }
            else:
                return {
                    'endpoint': 'chat',
                    'response_time': response_time,
                    'status': response.status_code,
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return {
                'endpoint': 'chat',
                'response_time': response_time,
                'status': 0,
                'success': False,
                'error': str(e)
            }
    
    async def test_list_endpoint(self, session: httpx.AsyncClient) -> Dict[str, Any]:
        """测试任务列表端点"""
        url = f"{self.base_url}/tasks?page=1&size=20"
        
        start_time = time.time()
        try:
            response = await session.get(url)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'endpoint': 'list',
                    'response_time': response_time,
                    'status': response.status_code,
                    'success': True,
                    'tasks_count': len(data.get('data', []))
                }
            else:
                return {
                    'endpoint': 'list',
                    'response_time': response_time,
                    'status': response.status_code,
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return {
                'endpoint': 'list',
                'response_time': response_time,
                'status': 0,
                'success': False,
                'error': str(e)
            }
    
    async def test_detail_endpoint(self, session: httpx.AsyncClient, task_id: str) -> Dict[str, Any]:
        """测试任务详情端点"""
        url = f"{self.base_url}/tasks/{task_id}"
        
        start_time = time.time()
        try:
            response = await session.get(url)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'endpoint': 'detail',
                    'response_time': response_time,
                    'status': response.status_code,
                    'success': True,
                    'has_task': bool(data.get('data'))
                }
            else:
                return {
                    'endpoint': 'detail',
                    'response_time': response_time,
                    'status': response.status_code,
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return {
                'endpoint': 'detail',
                'response_time': response_time,
                'status': 0,
                'success': False,
                'error': str(e)
            }
    
    async def run_concurrent_tests(self, concurrent_requests: int, total_requests: int):
        """运行并发测试"""
        print(f"开始性能基准测试...")
        print(f"目标URL: {self.base_url}")
        print(f"并发请求数: {concurrent_requests}")
        print(f"总请求数: {total_requests}")
        print(f"P95目标: ≤ 2.5s")
        print("-" * 50)
        
        timeout = httpx.Timeout(30.0)
        
        async with httpx.AsyncClient(timeout=timeout, limits=httpx.Limits(max_connections=concurrent_requests * 2)) as session:
            # 创建任务列表
            tasks = []
            
            for i in range(total_requests):
                # 轮询不同的端点和参数
                endpoint_type = i % 4
                
                if endpoint_type == 0:  # 搜索端点
                    query = SEED_QUERIES[i % len(SEED_QUERIES)]
                    task = self.test_search_endpoint(session, query)
                elif endpoint_type == 1:  # 聊天端点
                    task_id = TASK_IDS[i % len(TASK_IDS)]
                    question = SEED_CHAT_QUESTIONS[i % len(SEED_CHAT_QUESTIONS)]
                    task = self.test_chat_endpoint(session, task_id, question)
                elif endpoint_type == 2:  # 列表端点
                    task = self.test_list_endpoint(session)
                else:  # 详情端点
                    task_id = TASK_IDS[i % len(TASK_IDS)]
                    task = self.test_detail_endpoint(session, task_id)
                
                tasks.append(task)
            
            # 执行并发测试
            print("执行测试中...")
            start_time = time.time()
            
            # 分批执行以控制并发数
            results = []
            for i in range(0, len(tasks), concurrent_requests):
                batch = tasks[i:i + concurrent_requests]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        self.errors.append(str(result))
                    else:
                        results.append(result)
                        # 按端点分类存储结果
                        endpoint = result['endpoint']
                        if endpoint in self.results:
                            self.results[endpoint].append(result)
                
                # 显示进度
                completed = min(i + concurrent_requests, len(tasks))
                print(f"已完成: {completed}/{len(tasks)} ({completed/len(tasks)*100:.1f}%)")
            
            total_time = time.time() - start_time
            print(f"测试完成，总耗时: {total_time:.2f}s")
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """计算统计信息"""
        stats = {}
        
        for endpoint, results in self.results.items():
            if not results:
                continue
            
            response_times = [r['response_time'] for r in results if r['success']]
            success_count = len([r for r in results if r['success']])
            total_count = len(results)
            
            if response_times:
                stats[endpoint] = {
                    'total_requests': total_count,
                    'successful_requests': success_count,
                    'success_rate': success_count / total_count * 100,
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'avg_response_time': statistics.mean(response_times),
                    'median_response_time': statistics.median(response_times),
                    'p95_response_time': self._calculate_percentile(response_times, 95),
                    'p99_response_time': self._calculate_percentile(response_times, 99),
                    'meets_p95_target': self._calculate_percentile(response_times, 95) <= 2.5
                }
            else:
                stats[endpoint] = {
                    'total_requests': total_count,
                    'successful_requests': 0,
                    'success_rate': 0,
                    'meets_p95_target': False
                }
        
        return stats
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        stats = self.calculate_statistics()
        
        # 计算总体统计
        all_response_times = []
        total_requests = 0
        successful_requests = 0
        
        for endpoint_stats in stats.values():
            total_requests += endpoint_stats['total_requests']
            successful_requests += endpoint_stats['successful_requests']
            
            # 收集所有成功请求的响应时间
            endpoint_results = self.results.get(endpoint_stats.get('endpoint', ''), [])
            all_response_times.extend([
                r['response_time'] for r in endpoint_results if r['success']
            ])
        
        overall_stats = {}
        if all_response_times:
            overall_stats = {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'success_rate': successful_requests / total_requests * 100 if total_requests > 0 else 0,
                'avg_response_time': statistics.mean(all_response_times),
                'p95_response_time': self._calculate_percentile(all_response_times, 95),
                'p99_response_time': self._calculate_percentile(all_response_times, 99),
                'meets_p95_target': self._calculate_percentile(all_response_times, 95) <= 2.5
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'test_config': {
                'base_url': self.base_url,
                'p95_target': 2.5
            },
            'overall_performance': overall_stats,
            'endpoint_performance': stats,
            'errors': self.errors
        }
    
    def print_report(self, report: Dict[str, Any]):
        """打印测试报告"""
        print("\n" + "=" * 60)
        print("性能基准测试报告")
        print("=" * 60)
        
        overall = report['overall_performance']
        if overall:
            print(f"\n📊 总体性能:")
            print(f"  总请求数: {overall['total_requests']}")
            print(f"  成功请求数: {overall['successful_requests']}")
            print(f"  成功率: {overall['success_rate']:.1f}%")
            print(f"  平均响应时间: {overall['avg_response_time']:.3f}s")
            print(f"  P95响应时间: {overall['p95_response_time']:.3f}s")
            print(f"  P99响应时间: {overall['p99_response_time']:.3f}s")
            
            target_met = "✅" if overall['meets_p95_target'] else "❌"
            print(f"  P95目标达成: {target_met} (目标: ≤2.5s)")
        
        print(f"\n📈 各端点性能:")
        for endpoint, stats in report['endpoint_performance'].items():
            if stats['total_requests'] > 0:
                print(f"\n  {endpoint.upper()} 端点:")
                print(f"    请求数: {stats['total_requests']}")
                print(f"    成功率: {stats['success_rate']:.1f}%")
                if stats['successful_requests'] > 0:
                    print(f"    平均响应时间: {stats['avg_response_time']:.3f}s")
                    print(f"    P95响应时间: {stats['p95_response_time']:.3f}s")
                    target_met = "✅" if stats['meets_p95_target'] else "❌"
                    print(f"    P95目标达成: {target_met}")
        
        if report['errors']:
            print(f"\n❌ 错误信息 ({len(report['errors'])} 个):")
            for error in report['errors'][:5]:  # 只显示前5个错误
                print(f"  - {error}")
            if len(report['errors']) > 5:
                print(f"  ... 还有 {len(report['errors']) - 5} 个错误")
        
        print("\n" + "=" * 60)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="API性能基准测试")
    parser.add_argument("--url", default=DEFAULT_BASE_URL, help="API基础URL")
    parser.add_argument("--concurrent", type=int, default=DEFAULT_CONCURRENT_REQUESTS, help="并发请求数")
    parser.add_argument("--total", type=int, default=DEFAULT_TOTAL_REQUESTS, help="总请求数")
    parser.add_argument("--output", help="输出报告文件路径")
    
    args = parser.parse_args()
    
    # 创建基准测试实例
    benchmark = PerformanceBenchmark(args.url)
    
    try:
        # 运行测试
        await benchmark.run_concurrent_tests(args.concurrent, args.total)
        
        # 生成报告
        report = benchmark.generate_report()
        
        # 打印报告
        benchmark.print_report(report)
        
        # 保存报告文件
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 报告已保存到: {args.output}")
        
        # 返回退出码
        overall = report['overall_performance']
        if overall and overall['meets_p95_target']:
            print("\n🎉 性能测试通过！")
            return 0
        else:
            print("\n⚠️  性能测试未达到目标")
            return 1
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n测试执行失败: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))