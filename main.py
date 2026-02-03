import json, requests, os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = r.apparent_encoding
        return BeautifulSoup(r.text, 'lxml') if r.status_code == 200 else None
    except: return None

def crawl():
    aca, pol = [], []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 1. 科学网新闻 (精准定位：列表中的标题链接) ---
    soup = get_soup("http://news.sciencenet.cn/")
    if soup:
        # 定位到新闻列表区域，避免抓到导航栏
        for a in soup.select(".t1 a, .t2 a, .t3 a")[:10]:
            title, href = a.text.strip(), a.get('href')
            if href and "html" in href: # 文章通常以.html结尾
                aca.append({"title": title, "url": urljoin("http://news.sciencenet.cn/", href), "fetch_time": now})

    # --- 2. 中国社会科学网 (精准定位：资讯列表) ---
    soup = get_soup("http://www.cssn.cn/zx/zx_gx/")
    if soup:
        # 排除导航，只抓正文列表
        for a in soup.select(".font01 a, .List_Title a")[:8]:
            title, href = a.text.strip(), a.get('href')
            if href and "t20" in href: # 该站正文链接通常带日期，如 t2026...
                aca.append({"title": title, "url": urljoin("http://www.cssn.cn/zx/zx_gx/", href), "fetch_time": now})

    # --- 3. 中国学术会议在线 (精准定位) ---
    soup = get_soup("https://www.meeting.edu.cn/zh/meeting/list/0")
    if soup:
        for a in soup.select(".meet_list_info a")[:8]:
            title, href = a.text.strip(), a.get('href')
            if "/zh/meeting/" in href:
                aca.append({"title": f"[会议] {title}", "url": urljoin("https://www.meeting.edu.cn", href), "fetch_time": now})

    # --- 4. PubScholar (精准定位：动态列表) ---
    soup = get_soup("https://pubscholar.cn/news")
    if soup:
        for a in soup.select(".news-list a, .item-title a")[:8]:
            title, href = a.text.strip(), a.get('href')
            if href and len(title) > 10:
                pol.append({"title": title, "url": urljoin("https://pubscholar.cn/", href), "fetch_time": now})

    # --- 5. 中文学术集刊网 (南京大学) ---
    soup = get_soup("https://3c.nju.edu.cn/xsjk/news/list") # 修正为新闻列表页
    if soup:
        for a in soup.select(".news_list a, .list_box a")[:5]:
            title, href = a.text.strip(), a.get('href')
            pol.append({"title": f"[集刊] {title}", "url": urljoin("https://3c.nju.edu.cn/", href), "fetch_time": now})

    return aca, pol

def main():
    file = "news.json"
    limit = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    db = {"academic": [], "policy": []}
    
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: db = json.load(f)
        except: pass

    n_aca, n_pol = crawl()

    def merge(old, new):
        urls, res = set(), []
        for i in (new + old):
            # 这里的核心逻辑：如果URL深度太浅（比如只是域名），则剔除
            if i['url'].count('/') > 3 and i['url'] not in urls and i.get('fetch_time', '2000-01-01') >= limit:
                res.append(i)
                urls.add(i['url'])
        return res[:100]

    db["academic"], db["policy"] = merge(db.get("academic", []), n_aca), merge(db.get("policy", []), n_pol)
    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print("Done. Cleaned URLs saved.")

if __name__ == "__main__":
    main()
