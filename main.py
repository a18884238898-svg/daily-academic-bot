import json
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os

def fetch_arxiv_news():
    """获取 arXiv 最新论文 (学术板块)"""
    news_list = []
    try:
        # 抓取人工智能方向最新论文
        url = "http://export.arxiv.org/rss/cs.AI"
        response = requests.get(url, timeout=15)
        root = ET.fromstring(response.content)
        # 命名空间处理
        ns = {'rss': 'http://purl.org/rss/1.0/', 'dc': 'http://purl.org/dc/elements/1.1/'}
        
        for item in root.findall('.//rss:item', ns)[:8]: # 取前8条
            title = item.find('rss:title', ns).text
            link = item.find('rss:link', ns).text
            news_list.append({
                "title": title.replace('\n', '').strip(),
                "url": link,
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    except Exception as e:
        print(f"Arxiv 抓取失败: {e}")
    return news_list

def fetch_policy_news():
    """获取模拟政策数据 (政策板块 - 实际开发建议使用 BeautifulSoup 抓取官网)"""
    # 示例数据，确保 App 永远有内容显示
    return [
        {
            "title": "教育部：关于加强新时代工科教育改革的指导意见",
            "url": "http://www.moe.gov.cn/",
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "title": "科技部：2026年度国家自然科学基金申请指南发布",
            "url": "https://www.most.gov.cn/",
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]

def main():
    file_name = "news.json"
    
    # 1. 加载现有数据 (如果文件不存在，则创建空结构)
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            try:
                db = json.load(f)
            except:
                db = {"academic": [], "policy": []}
    else:
        db = {"academic": [], "policy": []}

    # 2. 抓取新数据
    new_academic = fetch_arxiv_news()
    new_policy = fetch_policy_news()

    # 3. 合并数据并保留10天内的记录
    ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    
    for category, new_items in [("academic", new_academic), ("policy", new_policy)]:
        # 合并新旧数据
        existing_urls = {item['url'] for item in new_items}
        for old_item in db.get(category, []):
            if old_item['url'] not in existing_urls and old_item.get('fetch_time', '') >= ten_days_ago:
                new_items.append(old_item)
        
        # 按时间排序并更新
        new_items.sort(key=lambda x: x.get('fetch_time', ''), reverse=True)
        db[category] = new_items[:50] # 每个分类最多保留50条

    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. 写入文件
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print("✅ 数据抓取并更新成功！")

if __name__ == "__main__":
    main()
