import json, requests, os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin

# 模拟更真实的浏览器指纹
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

def get_soup(url):
    try:
        # 增加 verify=False 防止 SSL 证书报错导致抓取失败
        r = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        r.encoding = r.apparent_encoding
        if r.status_code == 200:
            return BeautifulSoup(r.text, 'lxml')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def crawl():
    aca, pol = [], []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 策略 1: 科学网 (尝试更通用的选择器) ---
    soup = get_soup("http://news.sciencenet.cn/")
    if soup:
        # 如果精准选择器失效，尝试抓取所有包含 html 的 A 标签
        links = soup.select(".t1 a, .t2 a") or soup.find_all('a', href=True)
        count = 0
        for a in links:
            title, href = a.text.strip(), a.get('href')
            if count < 10 and len(title) > 8 and "html" in href:
                aca.append({"title": title, "url": urljoin("http://news.sciencenet.cn/", href), "fetch_time": now})
                count += 1

    # --- 策略 2: 中国学术会议在线 (API 或列表页) ---
    soup = get_soup("https://www.meeting.edu.cn/zh/meeting/list/0")
    if soup:
        links = soup.select(".meet_list_info a") or soup.find_all('a', href=True)
        for a in links:
            title, href = a.text.strip(), a.get('href')
            if "/zh/meeting/" in href and len(aca) < 15:
                aca.append({"title": f"[会议] {title}", "url": urljoin("https://www.meeting.edu.cn", href), "fetch_time": now})

    # --- 策略 3: 公益学术 PubScholar ---
    soup = get_soup("https://pubscholar.cn/news")
    if soup:
        for a in soup.find_all('a', href=True):
            title = a.text.strip()
            href = a.get('href')
            if len(title) > 10 and "http" in href and len(pol) < 10:
                pol.append({"title": title, "url": href, "fetch_time": now})

    # --- ⚠️ 兜底逻辑：如果抓取全灭，手动插入一条数据证明脚本在跑 ---
    if not aca:
        aca.append({"title": "数据源连接波动，请稍后再试", "url": "http://news.sciencenet.cn/", "fetch_time": now})
    
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

    n_aca, n_pol = crawl()

    def merge(old, new):
        urls, res = set(), []
        # 混合新旧数据
        for i in (new + old):
            # 排除重复和非文章链接（通过/的数量初步判断）
            if i['url'].count('/') > 2 and i['url'] not in urls and i.get('fetch_time', '2000-01-01') >= limit:
                res.append(i)
                urls.add(i['url'])
        return res[:100]

    db["academic"] = merge(db.get("academic", []), n_aca)
    db["policy"] = merge(db.get("policy", []), n_pol)
    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print(f"Update finished at {db['update_time']}. Found {len(n_aca)} items.")

if __name__ == "__main__":
    main()
