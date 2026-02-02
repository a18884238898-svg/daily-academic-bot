import json
import os
from datetime import datetime, timedelta

def update_database(new_items, category, current_data):
    """合并新旧数据并去重，保留10天内的内容"""
    ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取原有数据
    existing_items = current_data.get(category, [])
    
    # 合并、去重（根据 URL）并过滤掉10天前的旧闻
    combined = new_items + existing_items
    unique_items = []
    seen_urls = set()
    
    for item in combined:
        # 确保有抓取时间，如果没有则设为现在
        item_time = item.get("fetch_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        item["fetch_time"] = item_time
        
        if item["url"] not in seen_urls and item_time >= ten_days_ago:
            unique_items.append(item)
            seen_urls.add(item["url"])
            
    # 按时间降序排列（最新的在最上面）
    unique_items.sort(key=lambda x: x["fetch_time"], reverse=True)
    return unique_items

def main():
    # 1. 加载本地现有数据
    file_path = "news.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    else:
        db = {"academic": [], "policy": []}

    # 2. 执行你的抓取逻辑 (示例)
    new_academic = [
        {"title": "最新论文：AI在结构工程中的应用", "url": "https://arxiv.org/abs/xxxx", "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    ]
    new_policy = [
        {"title": "教育部：2026年高校科研经费管理办法", "url": "http://moe.gov.cn/xxx", "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    ]

    # 3. 更新并保存
    db["academic"] = update_database(new_academic, "academic", db)
    db["policy"] = update_database(new_policy, "policy", db)
    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
