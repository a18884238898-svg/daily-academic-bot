import json, requests, re, os
from datetime import datetime
from urllib.parse import urljoin

# 模拟真实浏览器请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

def fetch_items(url, tag, patterns, base_url):
    items = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = r.apparent_encoding
        content = r.text
        # 支持传入多个正则模式以提高成功率
        for pattern in patterns:
            matches = re.findall(pattern, content, re.S)
            for href, title in matches:
                clean_title = re.sub(r'<.*?>', '', title).strip()
                if len(clean_title) > 8:
                    items.append({
                        "title": f"[{tag}] {clean_title}",
                        "url": urljoin(base_url, href),
                        "fetch_time": now
                    })
            if items: break # 如果第一组抓到了，就不试后续模式
    except Exception as e:
        print(f"Error fetching {tag}: {e}")
    return items[:12]

def main():
    # --- 学术前沿：成果、活动、讲座、比赛 ---
    aca_data = []
    # 成果现状
    aca_data += fetch_items("https://news.sciencenet.cn/news-news.aspx", "研究成果", [r'<a href="(htmlnews/.*?)" .*?>(.*?)</a>'], "https://news.sciencenet.cn/")
    # 会议活动
    aca_data += fetch_items("https://www.meeting.edu.cn/zh/meeting/list/0", "学术活动", [r'<a href="(/zh/meeting/.*?)" .*?>(.*?)</a>'], "https://www.meeting.edu.cn")
    # 期刊动态
    aca_data += fetch_items("http://www.cssn.cn/zx/zx_gx/", "期刊动态", [r'<a href="(.*?.shtml)".*?>(.*?)</a>'], "http://www.cssn.cn/zx/zx_gx/")

    # --- 政策动态 ---
    pol_data = fetch_items("http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", "政策动态", [r'<a href="(./.*?)" .*?>(.*?)</a>'], "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 兜底内容：防止完全空白
    if not aca_data:
        aca_data = [{"title": "[系统] 正在同步学术资源...", "url": "https://news.sciencenet.cn/", "fetch_time": now_str}]
    if not pol_data:
        pol_data = [{"title": "[系统] 正在更新政策库...", "url": "http://www.moe.gov.cn/", "fetch_time": now_str}]

    db = {"academic": aca_data, "policy": pol_list, "update_time": now_str}
    
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print(f"Sync Success. Academic: {len(aca_data)}, Policy: {len(pol_data)}")

if __name__ == "__main__":
    main()
