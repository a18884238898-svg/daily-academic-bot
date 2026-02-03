import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

def get_headers():
    return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def safe_request(url):
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.encoding = response.apparent_encoding # 自动处理中文乱码
        return response.text
    except:
        return None

def crawl_sites():
    academic_list = []
    policy_list = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 1. 科学网新闻 (综合性强，解析稳定) ---
    html = safe_request("http://news.sciencenet.cn/")
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        # 抓取头条或要闻
        items = soup.select(".t1 a") + soup.select(".t2 a")
        for a in items[:10]:
            title = a.get_text().strip()
            link = a.get('href')
            if link and title:
                full_url = "http://news.sciencenet.cn/" + link if not link.startsWith('http') else link
                academic_list.append({"title": title, "url": full_url, "fetch_time": now_str})

    # --- 2. 中国学术会议在线 (抓取最新会议) ---
    html = safe_request("https://www.meeting.edu.cn/zh/meeting/list/0")
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select(".meet_list_info a")
        for a in items[:8]:
            title = "[会议] " + a.get_text().strip()
            link = a.get('href')
            if link:
                full_url = "https://www.meeting.edu.cn" + link
                academic_list.append({"title": title, "url": full_url, "fetch_time": now_str})

    # --- 3. PubScholar 公益学术 (政策与动态) ---
    html = safe_request("https://pubscholar.cn/news")
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        # 假设其结构有 news-item 类
        for a in soup.select("a")[:10]:
            title = a.get_text().strip()
            if len(title) > 10: # 简单过滤掉导航栏链接
                policy_list.append({"title": title, "url": a.get('href'), "fetch_time": now_str})

    # --- 4. 容错补丁：如果某些动态网站抓不到，加入保底数据 ---
    if not policy_list:
        policy_list.append({
            "title": "国家哲学社会科学文献中心：资源更新公告",
            "url": "http://www.ncpssd.org/",
            "fetch_time": now_str
        })

    return academic_list, policy_list

def main():
    file_name = "news.json"
    ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    
    # 加载旧数据
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            try: db = json.load(f)
            except: db = {"academic": [], "policy": []}
    else:
        db = {"academic": [], "policy": []}

    # 抓取新数据
    new_aca, new_pol = crawl_sites()

    # 合并、去重、时间过滤
    def merge(old, new):
        combined = new + old
        unique = []
        seen = set()
        for item in combined:
            if item['url'] not in seen and item.get('fetch_time', '') >= ten_days_ago:
                unique.append(item)
                seen.add(item['url'])
        return unique[:60] # 每个分类保存60条

    db["academic"] = merge(db.get("academic", []), new_aca)
    db["policy"] = merge(db.get("policy", []), new_pol)
    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
