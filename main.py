import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# 模拟浏览器环境
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

def get_html(url):
    """安全获取网页源码，失败不报错"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = r.apparent_encoding
        return r.text if r.status_code == 200 else None
    except:
        return None

def crawl_all():
    aca, pol = [], []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 采集源 1: 科学网要闻 ---
    h1 = get_html("http://news.sciencenet.cn/")
    if h1:
        try:
            s = BeautifulSoup(h1, 'lxml')
            for a in s.select(".t1 a, .t2 a")[:10]:
                title, href = a.text.strip(), a.get('href')
                if title and href:
                    url = f"http://news.sciencenet.cn/{href}" if not href.startswith('http') else href
                    aca.append({"title": title, "url": url, "fetch_time": now})
        except: pass

    # --- 采集源 2: 中国学术会议在线 ---
    h2 = get_html("https://www.meeting.edu.cn/zh/meeting/list/0")
    if h2:
        try:
            s = BeautifulSoup(h2, 'lxml')
            for a in s.select(".meet_list_info a")[:8]:
                title, href = a.text.strip(), a.get('href')
                if title and href:
                    url = f"https://www.meeting.edu.cn{href}" if not href.startswith('http') else href
                    aca.append({"title": f"[会议] {title}", "url": url, "fetch_time": now})
        except: pass

    # --- 采集源 3: PubScholar (公益学术) ---
    h3 = get_html("https://pubscholar.cn/news")
    if h3:
        try:
            s = BeautifulSoup(h3, 'lxml')
            for a in s.find_all('a')[:20]:
                title, href = a.text.strip(), a.get('href')
                if len(title) > 10 and href and href.startswith('http'):
                    pol.append({"title": title, "url": href, "fetch_time": now})
        except: pass

    # --- 采集源 4: 中国社会科学网 (学术版块) ---
    h4 = get_html("http://www.cssn.cn/zx/zx_gx/")
    if h4:
        try:
            s = BeautifulSoup(h4, 'lxml')
            for a in s.select(".font01 a")[:5]:
                title, href = a.text.strip(), a.get('href')
                if title:
                    url = f"http://www.cssn.cn/zx/zx_gx/{href.replace('./','')}"
                    aca.append({"title": title, "url": url, "fetch_time": now})
        except: pass

    return aca, pol

def main():
    file = "news.json"
    limit = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. 尝试读取旧数据
    db = {"academic": [], "policy": []}
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                db = json.load(f)
        except: pass

    # 2. 执行爬取
    new_aca, new_pol = crawl_all()

    # 3. 数据去重与合并
    def merge(old, new):
        urls = set()
        res = []
        for i in (new + old): # 优先保留新抓取的
            if i['url'] not in urls and i.get('fetch_time', '2020-01-01') >= limit:
                res.append(i)
                urls.add(i['url'])
        return res[:100]

    db["academic"] = merge(db.get("academic", []), new_aca)
    db["policy"] = merge(db.get("policy", []), new_pol)
    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. 写入，确保不留残余数据
    with open(file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print("✅ 数据同步完成")

if __name__ == "__main__":
    main()
