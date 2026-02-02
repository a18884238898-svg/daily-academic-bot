import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import json
import os

def fetch_engineering_data():
    # 示例：抓取 arXiv 工程类资讯
    url = "http://export.arxiv.org/api/query?search_query=cat:eess.*+OR+cat:cs.SY&sortBy=submittedDate&max_results=10"
    res = requests.get(url)
    root = ET.fromstring(res.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    news_text = "【工科资讯动态】\n"
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip().replace('\n', '')
        news_text += f"• {title}\n"
        
    return news_text

def save_json(content):
    # 构建 App 需要的 JSON 格式
    data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": content
    }
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    content = fetch_engineering_data()
    save_json(content)
