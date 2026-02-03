import json, requests, re, os
from datetime import datetime
from urllib.parse import urljoin

# 模拟真实浏览器，防止被封
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def fetch_items(url, tag, patterns, base_url):
    """
    通用抓取函数：支持多重正则匹配
    """
    items = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # 增加超时限制，防止 Action 卡死
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.encoding = r.apparent_encoding # 自动识别编码（处理中文乱码）
        content = r.text
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.S)
            for href, title in matches:
                # 过滤 HTML 标签并清洗文字
                clean_title = re.sub(r'<.*?>', '', title).strip()
                if len(clean_title) > 8:
                    items.append({
                        "title": f"[{tag}] {clean_title}",
                        "url": urljoin(base_url, href),
                        "fetch_time": now
                    })
            if items: break 
    except Exception as e:
        print(f"Fetch Error ({tag}): {e}")
    return items[:15]

def main():
    # --- 1. 学术前沿 (落实：研究现状、成果、比赛、活动) ---
    aca_data = []
    
    # 维度 A: 最新研究成果与各领域现状 (科学网)
    aca_data += fetch_items(
        "http://news.sciencenet.cn/news-news.aspx", 
        "研究成果", 
        [r'<a href="(htmlnews/.*?)" .*?>(.*?)</a>'], 
        "http://news.sciencenet.cn/"
    )
    
    # 维度 B: 学术会议、讲座与学术交流 (中国学术会议在线)
    aca_data += fetch_items(
        "https://www.meeting.edu.cn/zh/meeting/list/0", 
        "学术交流", 
        [r'<a href="(/zh/meeting/.*?)" .*?>(.*?)</a>'], 
        "https://www.meeting.edu.cn"
    )

    # 维度 C: 学术比赛、奖项与期刊变动 (社科网资讯)
    aca_data += fetch_items(
        "http://www.cssn.cn/zx/zx_gx/", 
        "期刊/动态", 
        [r'<a href="(.*?.shtml)".*?>(.*?)</a>'], 
        "http://www.cssn.cn/zx/zx_gx/"
    )

    # --- 2. 政策动态 (落实：教育部最新政策) ---
    pol_data = fetch_items(
        "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", 
        "政策动态", 
        [r'<a href="(./.*?)" .*?>(.*?)</a>'], 
        "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/"
    )

    # --- 3. 数据汇总与纠错 ---
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 如果抓取全灭，加入兜底数据
    if not aca_data:
        aca_data = [{"title": "[提示] 正在同步全球学术现状...", "url": "https://news.sciencenet.cn/", "fetch_time": now_str}]
    if not pol_data:
        pol_data = [{"title": "[提示] 教育政策同步中...", "url": "http://www.moe.gov.cn/", "fetch_time": now_str}]

    db = {
        "academic": aca_data,
        "policy": pol_data, # 已修复：之前这里可能写成了 pol_list 导致报错
        "update_time": now_str
    }
    
    # 写入 JSON
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    
    print(f"Update Success. Aca Count: {len(aca_data)}, Policy Count: {len(pol_data)}")

if __name__ == "__main__":
    main()
