import json, requests, os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

def crawl_site(url, selector):
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'lxml')
        # 排除导航栏常用的关键词，精准定位新闻链接
        for a in soup.select(selector):
            title = a.get_text(strip=True)
            href = a.get('href')
            if not href or len(title) < 6: continue
            
            full_url = urljoin(url, href)
            # 关键过滤：正文链接通常比官网链接长，且包含数字或 html 字样
            if len(full_url) > len(url) + 5:
                results.append({"title": title, "url": full_url, "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    except: pass
    return results

def main():
    # 针对你提供的需求，精准配置爬虫路径
    academic_sources = [
        ("http://news.sciencenet.cn/", ".t1 a, .t2 a"),
        ("https://www.meeting.edu.cn/zh/meeting/list/0", ".meet_list_info a"),
        ("http://www.cssn.cn/zx/zx_gx/", ".font01 a")
    ]
    
    db = {"academic": [], "policy": [], "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    for url, sel in academic_sources:
        db["academic"].extend(crawl_site(url, sel))
    
    # 简单的去重逻辑
    seen = set()
    final_aca = []
    for item in db["academic"]:
        if item['url'] not in seen:
            final_aca.append(item)
            seen.add(item['url'])
    db["academic"] = final_aca[:50]

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
