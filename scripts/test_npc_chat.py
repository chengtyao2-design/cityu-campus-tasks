#!/usr/bin/env python3
"""
NPC 聊天功能测试脚本

使用方法:
python scripts/test_npc_chat.py
python scripts/test_npc_chat.py --task T002 --question "实验室安全注意事项"
"""

import sys
import os
import argparse
import requests
import json
from typing import Dict, Any

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_npc_chat_api(base_url: str = "http://localhost:8000", task_id: str = "T001", question: str = None):
    """
    测试 NPC 聊天 API
    
    Args:
        base_url: API 基础URL
        task_id: 任务ID
        question: 用户问题
    """
    
    # 默认测试问题
    if question is None:
        test_questions = [
            "请介绍一下这个任务的具体要求",
            "这个任务需要多长时间完成？",
            "有什么注意事项吗？",
            "实验室安全注意事项有哪些？"  # 跨任务意图测试
        ]
    else:
        test_questions = [question]
    
    print(f"🤖 NPC 聊天功能测试")
    print(f"📍 服务器: {base_url}")
    print(f"🎯 任务ID: {task_id}")
    print("=" * 60)
    
    # 检查服务器状态
    try:
        health_response = requests.get(f"{base_url}/healthz", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ 服务器健康检查失败: {health_response.status_code}")
            return False
        print("✅ 服务器运行正常")
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("💡 请确保服务器正在运行: cd backend && python main.py")
        return False
    
    # 测试每个问题
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 测试 {i}: {question}")
        print("-" * 40)
        
        try:
            # 发送聊天请求
            chat_data = {"question": question}
            response = requests.post(
                f"{base_url}/npc/{task_id}/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 显示回答
                print(f"🤖 NPC 回答:")
                print(f"   {data.get('answer', '无回答')}")
                
                # 显示引用
                citations = data.get('citations', [])
                if citations:
                    print(f"\n📚 引用来源 ({len(citations)} 个):")
                    for j, citation in enumerate(citations, 1):
                        print(f"   {j}. {citation.get('source', '未知来源')}")
                        print(f"      内容: {citation.get('content', '')[:50]}...")
                        print(f"      相关性: {citation.get('score', 0):.2f}")
                
                # 显示地图锚点
                map_anchor = data.get('map_anchor', {})
                if map_anchor and map_anchor.get('lat', 0) != 0:
                    print(f"\n📍 地图位置:")
                    print(f"   位置: {map_anchor.get('location_name', '未知位置')}")
                    print(f"   坐标: ({map_anchor.get('lat', 0):.4f}, {map_anchor.get('lng', 0):.4f})")
                
                # 显示建议
                suggestions = data.get('suggestions', [])
                if suggestions:
                    print(f"\n💡 相关建议 ({len(suggestions)} 个):")
                    for j, suggestion in enumerate(suggestions, 1):
                        print(f"   {j}. {suggestion.get('title', '无标题')}")
                        print(f"      {suggestion.get('description', '无描述')}")
                
                # 显示不确定原因
                uncertain_reason = data.get('uncertain_reason')
                if uncertain_reason:
                    print(f"\n⚠️  不确定原因: {uncertain_reason}")
                
                print("✅ 请求成功")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 测试完成")
    return True


def interactive_chat(base_url: str = "http://localhost:8000", task_id: str = "T001"):
    """
    交互式聊天模式
    
    Args:
        base_url: API 基础URL
        task_id: 任务ID
    """
    print(f"🤖 NPC 交互式聊天")
    print(f"📍 任务ID: {task_id}")
    print("💬 输入 'quit' 或 'exit' 退出")
    print("=" * 40)
    
    while True:
        try:
            question = input("\n👤 您: ").strip()
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not question:
                continue
            
            # 发送请求
            chat_data = {"question": question}
            response = requests.post(
                f"{base_url}/npc/{task_id}/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '抱歉，我无法回答这个问题。')
                print(f"🤖 NPC: {answer}")
                
                # 显示地图位置（如果有）
                map_anchor = data.get('map_anchor', {})
                if map_anchor and map_anchor.get('lat', 0) != 0:
                    location = map_anchor.get('location_name', '未知位置')
                    print(f"📍 位置: {location}")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="NPC 聊天功能测试工具")
    parser.add_argument("--url", default="http://localhost:8000", help="API 基础URL")
    parser.add_argument("--task", default="T001", help="任务ID")
    parser.add_argument("--question", help="测试问题")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式聊天模式")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_chat(args.url, args.task)
    else:
        test_npc_chat_api(args.url, args.task, args.question)


if __name__ == "__main__":
    main()