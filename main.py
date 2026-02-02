import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import os

# Server酱配置
SEND_KEY = os.environ.get("SERVERCHAN_SENDKEY")
# arXiv API 链接 (关注 AI 领域最新的 10 篇文章)
ARXIV_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=10"

def get_news():
    response = requests.get(ARXIV_URL)
    if response.status_code != 200:
        return "抓取失败"
    
    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    # 获取 24 小时内的时间范围
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(hours=24)
    
    items = []
    for entry in root.findall('atom:entry', ns):
        pub_str = entry.find('atom:published', ns).text
        pub_time = datetime.strptime(pub_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        
        if pub_time > yesterday:
            title = entry.find('atom:title', ns).text.strip()
            link = entry.find('atom:id', ns).text.strip()
            items.append(f"### {title}\n- [查看论文]({link})")
            
    return "\n\n".join(items) if items else "过去24小时没有新论文发布。"

def send_to_wechat(content):
    if not SEND_KEY: return
    url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
    requests.post(url, data={"title": "今日学术日报", "desp": content})

if __name__ == "__main__":
    content = get_news()
    send_to_wechat(content)
