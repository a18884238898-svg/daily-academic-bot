import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

# 模拟浏览器头部，防止被反爬虫拦截
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_content(url, selector, tag_type="a", encoding='utf-8'):
    """
    通用抓取函数
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = encoding # 处理 GBK 等编码问题
        soup = BeautifulSoup(response.text, 'html.parser')
        items = []
        
        # 查找目标区域
        container = soup.select_one(selector)
        if container:
            links = container.find_all(tag_type, limit=5) # 每个源只抓取前5条，保证App流畅
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                # 补全相对路径
                if href.startswith('/'):
                    from urllib.parse import urljoin
                    href = urljoin(url, href)
                
                if len(title) > 5 and href.startswith('http'):
                    items.append({"title": title, "url": href})
        return items
    except Exception as e:
        print(f"抓取失败 {url}: {e}")
        return []

def main():
    # 任务配置列表：网站名、URL、CSS选择器、编码
    # 这里的选择器是根据各网站当前结构预估的，如果网站改版需要更新选择器
    tasks = [
        # --- 学术前沿板块 ---
        {"cate": "academic", "site": "科学网", "url": "news.sciencenet.cn", "selector": "#list_inner", "enc": "utf-8"},
        {"cate": "academic", "site": "中国社会科学网", "url": "http://www.cssn.cn/zx/zx_gx/", "selector": ".list_ul", "enc": "utf-8"},
        {"cate": "academic", "site": "PubScholar", "url": "https://pubscholar.cn/", "selector": ".news-list", "enc": "utf-8"},
        
        # --- 政策/会议板块 ---
        {"cate": "policy", "site": "中国学术会议在线", "url": "https://www.meeting.edu.cn/zh/meeting/list", "selector": ".list-item", "enc": "utf-8"},
        {"cate": "policy", "site": "教育部学位中心", "url": "https://www.cdgdc.edu.cn/xwyyjsjyxx/index.shtml", "selector": ".news_list", "enc": "utf-8"},
        {"cate": "policy", "site": "国家社科文献中心", "url": "http://www.ncpssd.org/notice.aspx", "selector": "#list_con", "enc": "utf-8"}
    ]

    all_data = {"academic": [], "policy": [], "update_time": ""}

    for t in tasks:
        print(f"正在抓取: {t['site']}")
        results = fetch_content(t['url'], t['selector'], encoding=t['enc'])
        for item in results:
            # 在标题前加上来源标签，方便App识别
            item['title'] = f"[{t['site']}] {item['title']}"
            all_data[t['cate']].append(item)
        time.sleep(1) # 礼貌抓取，避免频率过快

    all_data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
