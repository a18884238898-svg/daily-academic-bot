import json
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

def get_real_news():
    data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "academic": [],
        "policy": []
    }
    
    # 1. 抓取 arXiv 具体的学术文章 (RSS 源)
    try:
        r = requests.get("http://export.arxiv.org/rss/cs.AI", timeout=10)
        root = ET.fromstring(r.content)
        # 获取前 5 条具体论文链接
        for item in root.findall('.//{http://purl.org/rss/1.0/}item')[:5]:
            title = item.find('{http://purl.org/rss/1.0/}title').text
            link = item.find('{http://purl.org/rss/1.0/}link').text
            data["academic"].append({"title": title, "url": link})
    except:
        data["academic"].append({"title": "无法连接 arXiv，请检查爬虫", "url": "https://arxiv.org"})

    # 2. 抓取科技部具体动态 (模拟逻辑，实际需根据 HTML 解析)
    # 提示：实际生产中建议使用 BeautifulSoup 解析 http://www.most.gov.cn/
    data["policy"] = [
        {"title": "科技部关于发布国家重点研发计划的通知", "url": "https://www.most.gov.cn/tztg/202401/t20240101_189456.html"},
        {"title": "国家科技重大专项管理规定", "url": "https://www.most.gov.cn/xxgk/xinxigongkai/index.html"}
    ]
    return data

# ... 保存 JSON 逻辑同前 ...
