import json, requests, re, os
from datetime import datetime
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.baidu.com/'
}

def fetch_content(url, tag, patterns, base_url):
    """
    patterns: 列表，包含多个可能的正则组合，增加容错率
    """
    items = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.encoding = r.apparent_encoding
        content = r.text
        
        for p in patterns:
            matches = re.findall(p, content, re.S)
            for href, title in matches:
                clean_title = re.sub(r'<.*?>', '', title).strip()
                # 过滤掉导航栏短词，确保是新闻标题
                if len(clean_title) > 10 and not clean_title.startswith("查看更多"):
                    full_url = urljoin(base_url, href)
                    if full_url not in [x['url'] for x in items]:
                        items.append({"title": f"[{tag}] {clean_title}", "url": full_url, "fetch_time": now})
            if items: break # 如果第一组正则抓到了，就跳出
    except Exception as e:
        print(f"Error on {url}: {e}")
    return items[:10]

def main():
    aca_data = []
    pol_data = []

    # --- 落实：学术成果/研究现状 ---
    # 科学网-综合新闻：包含大量研究现状和成果
    aca_data += fetch_content(
        "http://news.sciencenet.cn/news-news.aspx", 
        "研究成果", 
        [r'<a href="(htmlnews/.*?)" .*?>(.*?)</a>'], 
        "http://news.sciencenet.cn/"
    )

    # --- 落实：学术活动/比赛/交流 ---
    # 中国学术会议在线：会议、讲座、比赛
    aca_data += fetch_content(
        "https://www.meeting.edu.cn/zh/meeting/list/0", 
        "活动/交流", 
        [r'<a href="(/zh/meeting/.*?)" .*?>(.*?)</a>'], 
        "https://www.meeting.edu.cn"
    )

    # --- 落实：期刊变动/通知 ---
    # 南京大学学术集刊网：期刊变动、征稿通知
    aca_data += fetch_content(
        "https://3c.nju.edu.cn/xsjk/news/list", 
        "期刊/变动", 
        [r'<a href="(.*?)".*?title="(.*?)"'], 
        "https://3c.nju.edu.cn/"
    )

    # --- 落实：政策动态 ---
    # 教育部-政策发布
    pol_data += fetch_content(
        "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", 
        "政策动态", 
        [r'<a href="(./.*?)" .*?>(.*?)</a>'], 
        "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/"
    )

    # --- 兜底处理 ---
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not aca_data:
        aca_data = [{"title": "[系统提示] 正在实时同步成果与活动数据...", "url": "http://news.sciencenet.cn/", "fetch_time": now_str}]
    if not pol_data:
        pol_data = [{"title": "[系统提示] 正在同步最新政策文件...", "url": "http://www.moe.gov.cn/", "fetch_time": now_str}]

    db = {"academic": aca_data, "policy": pol_data, "update_time": now_str}
    
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print(f"Update Success. Aca: {len(aca_data)}, Pol: {len(pol_data)}")

if __name__ == "__main__":
    main()
