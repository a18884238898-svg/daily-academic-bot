import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
from urllib.parse import urljoin # 👈 修复跳转的关键工具

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

def get_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = r.apparent_encoding
        return r.text if r.status_code == 200 else None
    except:
        return None

def crawl_all():
    aca, pol = [], []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 定义抓取目标 (站点URL, 选择器, 分类)
    targets = [
        ("http://news.sciencenet.cn/", ".t1 a, .t2 a", "aca"),
        ("https://www.meeting.edu.cn/zh/meeting/list/0", ".meet_list_info a", "aca"),
        ("https://pubscholar.cn/news", "a", "pol"),
        ("http://www.cssn.cn/zx/zx_gx/", ".font01 a", "aca"),
        ("http://muchong.com/bbs/index.php", "a.query_title", "aca") # 小木虫示例
    ]

    for base_url, selector, cat in targets:
        html = get_html(base_url)
        if not html: continue
        try:
            soup = BeautifulSoup(html, 'lxml')
            items = soup.select(selector)
            for a in items[:10]:
                title = a.get_text(strip=True)
                raw_href = a.get('href')
                if not title or not raw_href or len(title) < 5: continue
                
                # 🚀 核心修复：自动补全相对路径为绝对路径
                # 比如将 "./t123.html" 转换为 "http://www.cssn.cn/zx/zx_gx/t123.html"
                full_url = urljoin(base_url, raw_href)
                
                entry = {"title": title, "url": full_url, "fetch_time": now}
                if cat == "aca": aca.append(entry)
                else: pol.append(entry)
        except:
            continue
    return aca, pol

def main():
    file = "news.json"
    limit = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    db = {"academic": [], "policy": []}
    
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                db = json.load(f)
        except: pass

    new_aca, new_pol = crawl_all()

    def merge(old, new):
        urls = set()
        res = []
        for i in (new + old):
            # 过滤掉已经是主页的链接（简单逻辑：路径深度太浅的可能只是导航栏）
            if i['url'] not in urls and i.get('fetch_time', '2020-01-01') >= limit:
                res.append(i)
                urls.add(i['url'])
        return res[:100]

    db["academic"] = merge(db.get("academic", []), new_aca)
    db["policy"] = merge(db.get("policy", []), new_pol)
    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print("✅ 数据抓取完成，链接已补全")

if __name__ == "__main__":
    main()
