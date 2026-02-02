import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import os
import re

SEND_KEY = os.environ.get("SERVERCHAN_SENDKEY")

def get_engineering_academic():
    """抓取 arXiv 工程学相关的所有分类 (Electrical, Mechanical, etc.)"""
    # 搜索：工程(eng), 系统与控制(sys), 电力(el)
    url = "http://export.arxiv.org/api/query?search_query=cat:eess.*+OR+cat:cs.SY&sortBy=submittedDate&max_results=5"
    try:
        res = requests.get(url)
        root = ET.fromstring(res.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        items = ["### 🛠️ 工科最新学术进展"]
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip()
            link = entry.find('atom:id', ns).text.strip()
            items.append(f"- {title}\n  [查看原文]({link})")
        return "\n".join(items)
    except:
        return "学术源抓取失败"

def get_policy_news():
    """抓取行业政策动态 (以工信部政务动态为例)"""
    # 注意：政府网站通常没有RSS，此处演示解析其动态列表页面的思路
    url = "https://www.miit.gov.cn/gxgz/index.html" 
    # 备注：实际操作中，政府网站常有反爬。推荐使用第三方聚合后的RSS源（如RSSHub）
    # 这里以一个公共的工信部RSS源为例
    rss_url = "https://rsshub.app/miit/wjfb/yjfg" 
    try:
        res = requests.get(rss_url, timeout=10)
        root = ET.fromstring(res.content)
        items = ["### 📜 行业政策动态"]
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            link = item.find('link').text
            items.append(f"- {title}\n  [政策链接]({link})")
        return "\n".join(items)
    except:
        return "政策源抓取延迟，请稍后查看。"

def main():
    academic = get_engineering_academic()
    policy = get_policy_news()
    full_content = f"{policy}\n\n---\n\n{academic}"
    
    # 推送到 Server 酱
    if SEND_KEY:
        requests.post(f"https://sctapi.ftqq.com/{SEND_KEY}.send", 
                      data={"title": "工科资讯与政策日报", "desp": full_content})

if __name__ == "__main__":
    main()
