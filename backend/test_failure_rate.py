#!/usr/bin/env python3
"""
测试25%失败概率的脚本
"""

import random
import time
from collections import Counter

def test_failure_rate(num_tests=100):
    """测试失败概率"""
    print(f"开始测试 {num_tests} 次训练任务...")
    
    results = []
    for i in range(num_tests):
        # 模拟训练过程
        print(f"任务 {i+1}: 开始训练...")
        
        # 25%的失败概率
        if random.random() < 0.25:
            print(f"任务 {i+1}: ❌ 失败")
            results.append("failed")
        else:
            print(f"任务 {i+1}: ✅ 成功")
            results.append("success")
        
        time.sleep(0.1)  # 模拟训练时间
    
    # 统计结果
    counter = Counter(results)
    total = len(results)
    success_rate = counter["success"] / total * 100
    failure_rate = counter["failed"] / total * 100
    
    print("\n" + "="*50)
    print("测试结果统计:")
    print(f"总任务数: {total}")
    print(f"成功任务: {counter['success']} ({success_rate:.1f}%)")
    print(f"失败任务: {counter['failed']} ({failure_rate:.1f}%)")
    print(f"预期失败率: 25.0%")
    print(f"实际失败率: {failure_rate:.1f}%")
    print("="*50)
    
    return failure_rate

if __name__ == "__main__":
    # 运行多次测试来验证概率
    print("🎯 测试25%失败概率功能")
    print()
    
    test_failure_rate(100) 