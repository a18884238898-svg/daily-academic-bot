import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_site(url, site_name, selector, encoding='utf-8'):
    items = []
    try:
        # 增加 verify=False 解决证书问题，提高兼容性
        res = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        res.encoding = encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 寻找指定的容器
        container = soup.select_one(selector)
        if not container:
            # 如果找不到容器，尝试缩小范围搜寻
            container = soup
            
        links = container.find_all('a', limit=15)
        for link in links:
            title = link.get_text().strip()
            href = link.get('href', '')
            
            # 排除掉常见的垃圾词汇
            blacklist = ['Français', '备案', '登录', '注册', '首页', 'About', 'English']
            if any(word in title for word in blacklist): continue
            
            if 10 <= len(title) <= 50 and href:
                full_url = urljoin(url, href)
                if full_url.startswith('http'):
                    items.append({"title": f"[{site_name}] {title}", "url": full_url})
                    if len(items) >= 6: break # 每个源留 6 条精华
        print(f"✅ {site_name} 成功抓取 {len(items)} 条")
    except Exception as e:
        print(f"❌ {site_name} 失败: {e}")
    return items

def main():
    # 针对性配置：每个站点的 URL 和 最精准的 CSS 选择器
    # 如果 selector 为空，则全局搜索
    tasks = [
        # --- 学术前沿 ---
        {"cate": "academic", "site": "科学网", "url": "https://news.sciencenet.cn/", "selector": "#list_inner"},
        {"cate": "academic", "site": "社科网", "url": "http://www.cssn.cn/zx/zx_gx/", "selector": ".list_ul"},
        {"cate": "academic", "site": "PubScholar", "url": "https://pubscholar.cn/news/index", "selector": ".list-content"},
        
        # --- 政策/会议 ---
        {"cate": "policy", "site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list", "selector": ".list-item-box"},
        {"cate": "policy", "site": "学位中心", "url": "https://www.cdgdc.edu.cn/xwyyjsjyxx/index.shtml", "selector": ".news_list"},
        {"cate": "policy", "site": "社科文献", "url": "http://www.ncpssd.org/notice.aspx", "selector": ".list_con"}
    ]

    result = {"academic": [], "policy": [], "update_time": ""}

    for t in tasks:
        # 增加一秒随机延迟，防止反爬
        time.sleep(1)
        data = fetch_site(t['url'], t['site'], t['selector'])
        result[t['cate']].extend(data)

    result["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("Done!")

if __name__ == "__main__":
    main()
