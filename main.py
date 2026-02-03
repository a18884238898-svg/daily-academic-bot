import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from urllib.parse import urljoin

# 更强大的浏览器伪装
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,en;q=0.5,en-US;q=0.3',
}

def smart_fetch(url, site_name):
    items = []
    try:
        # verify=False 绕过证书错误，timeout 增加到 20 秒
        response = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        response.encoding = response.apparent_encoding # 自动识别编码（解决乱码）
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 核心逻辑：不再死磕某个 ID，而是抓取前 15 个包含标题文字的链接
        links = soup.find_all('a')
        count = 0
        for link in links:
            title = link.get_text().strip()
            href = link.get('href', '')
            
            # 过滤逻辑：标题长度在 8-40 之间，且不是“更多”、“首页”等干扰词
            if 8 <= len(title) <= 40 and href and not href.startswith('javascript'):
                full_url = urljoin(url, href)
                if full_url.startswith('http'):
                    items.append({"title": f"[{site_name}] {title}", "url": full_url})
                    count += 1
            if count >= 8: break # 每个站只取前 8 条，防止 App 刷不动
            
        print(f"✅ {site_name} 抓取成功: {len(items)} 条")
    except Exception as e:
        print(f"❌ {site_name} 抓取失败: {e}")
    return items

def main():
    # 重新梳理的最稳健入口地址
    tasks = [
        # 学术前沿
        {"cate": "academic", "site": "科学网", "url": "https://news.sciencenet.cn/sublist.aspx?type=1&id=1"},
        {"cate": "academic", "site": "社科网", "url": "http://www.cssn.cn/zx/zx_gx/"},
        {"cate": "academic", "site": "PubScholar", "url": "https://pubscholar.cn/news/index"},
        
        # 政策/会议
        {"cate": "policy", "site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list"},
        {"cate": "policy", "site": "学位中心", "url": "https://www.cdgdc.edu.cn/xwyyjsjyxx/index.shtml"},
        {"cate": "policy", "site": "社科文献", "url": "http://www.ncpssd.org/notice.aspx"}
    ]

    news_data = {"academic": [], "policy": [], "update_time": ""}

    for t in tasks:
        results = smart_fetch(t['url'], t['site'])
        news_data[t['cate']].extend(results)
        time.sleep(2) # 增加延迟，防止被封

    news_data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=4)
    print("🎉 抓取任务完成！")

if __name__ == "__main__":
    main()
