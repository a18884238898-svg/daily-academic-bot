import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from urllib.parse import urljoin
import urllib3

# 禁用不安全请求警告（针对一些政府网站的证书问题）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_items(url, site_name, selector):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': url,
        'Connection': 'keep-alive'
    }
    items = []
    try:
        # 增加超时和 verify=False
        response = requests.get(url, headers=headers, timeout=25, verify=False)
        response.encoding = response.apparent_encoding
        
        # 调试输出：如果抓取结果为空，可以在日志看到网页前100个字
        print(f"[{site_name}] HTTP状态码: {response.status_code}, 内容预览: {response.text[:100].strip()}")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 优先尝试精准选择器
        target = soup.select_one(selector) if selector else soup
        
        # 2. 如果精准选择器失效，回退到全局搜索
        if not target:
            target = soup

        links = target.find_all('a')
        for link in links:
            title = link.get_text().strip()
            href = link.get('href', '')
            
            # 精细化过滤：标题长度 10-50，排除常见导航词
            blacklist = ['Français', '备案', '登录', '注册', '首页', '版权', 'About', '更多', '联系我们']
            if any(word in title for word in blacklist): continue
            
            if 10 <= len(title) <= 60 and href and not href.startswith('javascript'):
                full_url = urljoin(url, href)
                if full_url.startswith('http'):
                    items.append({"title": f"[{site_name}] {title}", "url": full_url})
                    if len(items) >= 8: break # 每个源取8条
        
        print(f"✅ {site_name} 成功获取: {len(items)} 条")
    except Exception as e:
        print(f"❌ {site_name} 抓取异常: {e}")
    return items

def main():
    tasks = [
        # --- 学术前沿 ---
        {"cate": "academic", "site": "科学网", "url": "https://news.sciencenet.cn/", "selector": "#list_inner"},
        {"cate": "academic", "site": "社科网", "url": "http://www.cssn.cn/zx/zx_gx/", "selector": ".list_ul"},
        {"cate": "academic", "site": "PubScholar", "url": "https://pubscholar.cn/news/index", "selector": ".list-content"},
        
        # --- 政策/论坛 ---
        {"cate": "policy", "site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list", "selector": ".list-item-box"},
        {"cate": "policy", "site": "学位中心", "url": "https://www.cdgdc.edu.cn/xwyyjsjyxx/index.shtml", "selector": "body"},
        {"cate": "policy", "site": "小木虫", "url": "http://muchong.com/bbs/index.php?gid=29", "selector": ".stitle"}
    ]

    final_data = {"academic": [], "policy": [], "update_time": ""}

    for t in tasks:
        results = get_items(t['url'], t['site'], t['selector'])
        final_data[t['cate']].extend(results)
        time.sleep(2) # 礼貌性延迟，防止被封 IP

    final_data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("Done!")

if __name__ == "__main__":
    main()
