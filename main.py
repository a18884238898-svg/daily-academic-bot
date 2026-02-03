import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from urllib.parse import urljoin

# 模拟浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_content(url, selector, encoding='utf-8'):
    try:
        # 增加 verify=False 防止部分政府网站 SSL 证书过期导致报错
        response = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        response.encoding = encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        items = []
        
        container = soup.select_one(selector)
        if container:
            # 查找所有 a 标签
            links = container.find_all('a', limit=6)
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                if href and not href.startswith('http'):
                    href = urljoin(url, href)
                
                if len(title) > 4 and href.startswith('http'):
                    items.append({"title": title, "url": href})
        return items
    except Exception as e:
        print(f"跳过网站 {url}, 原因: {e}")
        return []

def main():
    # 任务列表：cate(分类), site(来源), url(地址), selector(CSS选择器), enc(编码)
    tasks = [
        # --- 学术前沿 ---
        {"cate": "academic", "site": "科学网", "url": "https://news.sciencenet.cn/", "selector": "#list_inner", "enc": "utf-8"},
        {"cate": "academic", "site": "社科网", "url": "http://www.cssn.cn/zx/zx_gx/", "selector": ".list_ul", "enc": "utf-8"},
        {"cate": "academic", "site": "PubScholar", "url": "https://pubscholar.cn/news/index", "selector": ".list-content", "enc": "utf-8"},
        
        # --- 政策/会议 ---
        {"cate": "policy", "site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list", "selector": ".list-item-box", "enc": "utf-8"},
        {"cate": "policy", "site": "社科文献中心", "url": "http://www.ncpssd.org/notice.aspx", "selector": ".list_con", "enc": "utf-8"},
        {"cate": "policy", "site": "学位中心", "url": "https://www.cdgdc.edu.cn/xwyyjsjyxx/index.shtml", "selector": ".news_list", "enc": "utf-8"}
    ]

    all_data = {"academic": [], "policy": [], "update_time": ""}

    for t in tasks:
        print(f"正在尝试抓取: {t['site']}")
        results = fetch_content(t['url'], t['selector'], encoding=t['enc'])
        for item in results:
            item['title'] = f"[{t['site']}] {item['title']}"
            all_data[t['cate']].append(item)
        time.sleep(1)

    all_data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("同步完成，news.json 已更新")

if __name__ == "__main__":
    main()
