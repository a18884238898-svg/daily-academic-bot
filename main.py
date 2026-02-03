import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# 模拟浏览器头部，防止被网站屏蔽
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def safe_get(url):
    """安全请求网页，失败返回 None，不抛出异常"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = resp.apparent_encoding
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"请求失败 {url}: {e}")
    return None

def crawl_task():
    academic_list = []
    policy_list = []
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 1. 科学网 (学术板块) ---
    html = safe_get("http://news.sciencenet.cn/")
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        # 抓取要闻区的链接
        for a in soup.select(".t1 a, .t2 a")[:10]:
            title = a.get_text().strip()
            link = a.get('href')
            if title and link:
                full_url = f"http://news.sciencenet.cn/{link}" if not link.startswith('http') else link
                academic_list.append({"title": title, "url": full_url, "fetch_time": now_time})

    # --- 2. 中国学术会议在线 (学术板块) ---
    html = safe_get("https://www.meeting.edu.cn/zh/meeting/list/0")
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.select(".meet_list_info a")[:8]:
            title = "[会议] " + a.get_text().strip()
            link = a.get('href')
            if link:
                full_url = f"https://www.meeting.edu.cn{link}" if not link.startswith('http') else link
                academic_list.append({"title": title, "url": full_url, "fetch_time": now_time})

    # --- 3. PubScholar 公益学术 (政府/公益板块) ---
    html = safe_get("https://pubscholar.cn/news")
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a')[:15]: # 粗筛选
            title = a.get_text().strip()
            link = a.get('href')
            if len(title) > 12 and link and link.startswith('http'):
                policy_list.append({"title": title, "url": link, "fetch_time": now_time})

    # --- 4. 容错逻辑：如果以上都抓不到，填入保底数据，防止 App 显示为空 ---
    if not academic_list:
        academic_list.append({"title": "科学网：探索生命演化的奥秘", "url": "http://www.sciencenet.cn/", "fetch_time": now_time})
    if not policy_list:
        policy_list.append({"title": "国家哲学社会科学文献中心资源更新", "url": "http://www.ncpssd.org/", "fetch_time": now_time})

    return academic_list, policy_list

def main():
    file_name = "news.json"
    limit_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")

    # 读取旧数据
    db = {"academic": [], "policy": []}
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                db = json.load(f)
        except: pass

    # 抓取新数据
    new_aca, new_pol = crawl_task()

    # 合并、去重、保留10日数据
    def clean_data(old_data, new_data):
        unique_urls = set()
        result = []
        # 优先放入新数据
        for item in (new_data + old_data):
            u = item.get('url')
            t = item.get('fetch_time', '2000-01-01')
            if u not in unique_urls and t >= limit_date:
                result.append(item)
                unique_urls.add(u)
        return result[:100] # 最多存100条

    db["academic"] = clean_data(db.get("academic", []), new_aca)
    db["policy"] = clean_data(db.get("policy", []), new_pol)
    db["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 写入文件
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print("Update Successful.")

if __name__ == "__main__":
    main()
