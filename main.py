import json, requests, re
from datetime import datetime
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

def fetch_list(url, tag, regex_pattern, base_url):
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.encoding = r.apparent_encoding
        # 核心逻辑：使用更宽容的正则寻找 A 标签
        matches = re.findall(regex_pattern, r.text, re.S)
        for href, title in matches:
            # 清理 HTML 标签并过滤短标题
            title = re.sub(r'<.*?>', '', title).strip()
            if len(title) > 8:
                items.append({
                    "title": f"[{tag}] {title}",
                    "url": urljoin(base_url, href),
                    "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    except Exception as e:
        print(f"Error on {tag}: {e}")
    return items[:10]

def main():
    aca_data = []
    pol_data = []

    # --- 落实：学术成果/现状 (科学网) ---
    aca_data += fetch_list(
        "http://news.sciencenet.cn/news-news.aspx", 
        "研究成果", 
        r'<a href="(htmlnews/.*?)" .*?>(.*?)</a>', 
        "http://news.sciencenet.cn/"
    )

    # --- 落实：学术会议/比赛/交流 (中国学术会议在线) ---
    aca_data += fetch_list(
        "https://www.meeting.edu.cn/zh/meeting/list/0", 
        "活动/交流", 
        r'<a href="(/zh/meeting/.*?)" .*?>(.*?)</a>', 
        "https://www.meeting.edu.cn"
    )

    # --- 落实：政策动态 (教育部) ---
    pol_data += fetch_list(
        "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", 
        "政策发布", 
        r'<a href="(\./.*?)" .*?>(.*?)</a>', 
        "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/"
    )

    # 最终汇总
    db = {
        "academic": aca_data if aca_data else [{"title": "[提示] 正在重新同步成果与活动数据...", "url": "http://news.sciencenet.cn/", "fetch_time": "实时"}],
        "policy": pol_data if pol_data else [{"title": "[提示] 正在同步教育部最新政策...", "url": "http://www.moe.gov.cn/", "fetch_time": "实时"}],
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
