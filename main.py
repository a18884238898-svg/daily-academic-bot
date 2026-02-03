import json, requests, os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, verify=False)
        r.encoding = r.apparent_encoding
        return BeautifulSoup(r.text, 'lxml') if r.status_code == 200 else None
    except: return None

def crawl():
    aca, pol = [], []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- A. 学术前沿 (维持精准规则) ---
    sources_aca = [
        ("http://news.sciencenet.cn/", ".t1 a, .t2 a", "http://news.sciencenet.cn/"),
        ("https://www.meeting.edu.cn/zh/meeting/list/0", ".meet_list_info a", "https://www.meeting.edu.cn"),
        ("http://www.cssn.cn/zx/zx_gx/", ".font01 a", "http://www.cssn.cn/zx/zx_gx/")
    ]
    for base_url, sel, join_base in sources_aca:
        soup = get_soup(base_url)
        if soup:
            for a in soup.select(sel)[:10]:
                title, href = a.text.strip(), a.get('href')
                if not href or len(title) < 5: continue
                full_url = urljoin(join_base, href)
                # 学术类过滤：确保不是主页
                if len(full_url) > len(base_url) + 5:
                    aca.append({"title": title, "url": full_url, "fetch_time": now})

    # --- B. 政策动态 (修复点：使用宽松规则 + 新增源) ---
    sources_pol = [
        ("https://pubscholar.cn/news", "a"), # PubScholar
        ("http://www.nopss.gov.cn/GB/219461/index.html", ".fl a"), # 社科规划办
        ("http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb", ".moe-list a")  # 教育部数据发布
    ]
    for base_url, sel, in sources_pol:
        soup = get_soup(base_url)
        if soup:
            count = 0
            for a in soup.select(sel):
                title, href = a.text.strip(), a.get('href')
                # 政策类逻辑：标题够长且有链接就抓，不强制要求.html后缀
                if href and len(title) > 10 and count < 8:
                    full_url = urljoin(base_url, href)
                    if "javascript" not in full_url:
                        pol.append({"title": title, "url": full_url, "fetch_time": now})
                        count += 1

    # 如果政策动态依然为空，插入一条保底信息防止UI报错
    if not pol:
        pol.append({"title": "政策动态库维护中，请访问教育部官网查看", "url": "http://www.moe.gov.cn/", "fetch_time": now})

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

    def merge_data(old, new, limit_date):
        urls, res = set(), []
        for i in (new + old):
            if i['url'] not in urls and i.get('fetch_time', '2000-01-01') >= limit_date:
                res.append(i)
                urls.add(i['url'])
        return res[:60]

    db["academic"] = merge_data(db.get("academic", []), n_aca, limit)
    db["policy"] = merge_data(db.get("policy", []), n_pol, limit)
    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print(f"Update Success. Academic: {len(n_aca)}, Policy: {len(n_pol)}")

if __name__ == "__main__":
    main()
