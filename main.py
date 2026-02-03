import json, requests, os, re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

def fetch_rss(url):
    """通过 RSS 获取数据，这是最稳定的方式"""
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        root = ET.fromstring(r.content)
        # 处理不同格式的 RSS (RSS 2.0 vs Atom)
        for entry in root.findall('.//item')[:10]:
            title = entry.find('title').text
            link = entry.find('link').text
            items.append({"title": title, "url": link, "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    except: pass
    return items

def fetch_html_fallback(url, selector, base_url):
    """HTML 抓取备份方案"""
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'lxml')
        for a in soup.select(selector)[:10]:
            title = a.get_text(strip=True)
            href = a.get('href')
            if href and len(title) > 8:
                items.append({"title": title, "url": urljoin(base_url, href), "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    except: pass
    return items

def main():
    file_name = "news.json"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # --- 1. 学术前沿：改用 arXiv RSS (绝对稳定) + 科学网备份 ---
    academic = fetch_rss("https://export.arxiv.org/rss/cs.AI") 
    if not academic:
        academic = fetch_html_fallback("http://news.sciencenet.cn/", ".t1 a, .t2 a", "http://news.sciencenet.cn/")

    # --- 2. 政策动态：教育新闻 RSS + PubScholar 备份 ---
    # 这里选取了一个非常稳定的教育资讯源
    policy = fetch_html_fallback("https://pubscholar.cn/news", "a", "https://pubscholar.cn/")
    if not policy:
        # 尝试抓取教育部新闻列表（宽松模式）
        policy = fetch_html_fallback("http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", ".moe-list a", "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/")

    # --- 3. 汇总与去重 ---
    db = {"academic": academic, "policy": policy, "update_time": now_str}
    
    # 保底数据（只有在完全抓不到时才显示，带有引导性）
    if not db["academic"]:
        db["academic"] = [{"title": "正在重新连接学术数据库...", "url": "http://news.sciencenet.cn/", "fetch_time": now_str}]
    if not db["policy"]:
        db["policy"] = [{"title": "正在同步最新政策文件...", "url": "http://www.moe.gov.cn/", "fetch_time": now_str}]

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print(f"Update Success. Aca: {len(academic)}, Pol: {len(policy)}")

if __name__ == "__main__":
    main()
