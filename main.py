import json
import os
from datetime import datetime, timedelta
import random

def get_current_time(days_offset=0):
    """获取带偏移量的当前时间字符串"""
    target_time = datetime.now() - timedelta(days=days_offset)
    return target_time.strftime("%Y-%m-%d %H:%M:%S")

def main():
    # 1. 生成模拟的“新鲜”数据 (强制包含 fetch_time)
    mock_academic_data = [
        {
            "title": "【测试】Nature: 深度学习在土木工程中的最新应用", 
            "url": "https://www.nature.com",
            "fetch_time": get_current_time(0) # 今天
        },
        {
            "title": "【测试】arXiv: 2026年大型语言模型综述", 
            "url": "https://arxiv.org",
            "fetch_time": get_current_time(1) # 昨天
        },
        {
            "title": "【测试】Science: 新型环保建筑材料研究突破", 
            "url": "https://www.science.org",
            "fetch_time": get_current_time(3) # 3天前
        }
    ]

    mock_policy_data = [
        {
            "title": "【测试】科技部：发布2026年度国家重点研发计划指南", 
            "url": "https://www.most.gov.cn",
            "fetch_time": get_current_time(0) # 今天
        },
        {
            "title": "【测试】教育部：关于加强高校科研诚信建设的通知", 
            "url": "http://www.moe.gov.cn",
            "fetch_time": get_current_time(2) # 2天前
        }
    ]

    # 2. 构造最终的 JSON 结构
    data = {
        "update_time": get_current_time(0),
        "academic": mock_academic_data,
        "policy": mock_policy_data
    }

    # 3. 保存为 news.json
    # 注意：这里我们先不执行“合并去重”逻辑，直接覆盖，确保 App 能先看到数据
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("✅ news.json 已强制更新为最新测试数据！")

if __name__ == "__main__":
    main()
