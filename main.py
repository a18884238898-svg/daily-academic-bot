import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from urllib.parse import urljoin

# 模拟真实浏览器头部
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def safe_fetch(url, selector, site_name, encoding='utf-8'):
    """
    带容错的抓取函数：如果一个网站挂了，返回空列表而不是崩溃
    """
    items = []
    try:
        # verify=False 解决部分政府网站证书过期的报错
        response = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        response.encoding = encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找匹配的容器
        container = soup.select_one(selector)
        if container:
            # 限制每个源抓取 5 条
            links = container.find_all('a', limit=8)
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                if not href: continue
                # 补全相对路径 (例如 /news/123.html -> http://site.com/news/123.html)
                full_url = urljoin(url, href)
                
                # 过滤掉干扰项（如“更多”、“查看详细”等短语）
                if len(title) > 6 and full_url.startswith('http'):
                    items.append({"title": f"[{site_name}] {title}", "url": full_url})
        print(f"✅ {site_name} 抓取成功: {len(items)} 条")
    except Exception as e:
        print(f"❌ {site_name} 抓取失败: {e}")
    return items

def main():
    # 任务配置清单
    tasks = [
        # --- 学术前沿 ---
        {"cate": "academic", "site": "科学网", "url": "https://news.sciencenet.cn/", "selector": "#list_inner"},
        {"cate": "academic", "site": "社科网", "url": "http://www.cssn.cn/zx/zx_gx/", "selector": ".list_ul"},
        {"cate": "academic", "site": "PubScholar", "url": "https://pubscholar.cn/news/index", "selector": ".list-content"},
        
        # --- 政策/会议 ---
        {"cate": "policy", "site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list", "selector": ".list-item-box"},
        {"cate": "policy", "site": "学位中心", "url": "https://www.cdgdc.edu.cn/xwyyjsjyxx/index.shtml", "selector": ".news_list"},
        {"cate": "policy", "site": "社科文献中心", "url": "http://www.ncpssd.org/notice.aspx", "selector": ".list_con"}
    ]

    news_data = {"academic": [], "policy": [], "update_time": ""}

    for t in tasks:
        results = safe_fetch(t['url'], t['selector'], t['site'])
        news_data[t['cate']].extend(results)
        time.sleep(1) # 间隔1秒，避免被封IP

    # 记录最后更新时间
    news_data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 写入 JSON
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=4)
    print("🎉 任务圆满完成！")

if __name__ == "__main__":
    main()
