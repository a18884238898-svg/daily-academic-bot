import json, requests, re, os
from datetime import datetime
from urllib.parse import urljoin

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

def fetch_list(url, tag, regex_pattern, base_url):
    """通用抓取工具：通过正则从网页抓取特定块"""
    items = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = r.apparent_encoding
        # 寻找包含标题和链接的 A 标签
        matches = re.findall(regex_pattern, r.text, re.S)
        for href, title in matches[:8]:
            title = re.sub(r'<.*?>', '', title).strip() # 清理 HTML 标签
            if len(title) > 8:
                items.append({
                    "title": f"[{tag}] {title}",
                    "url": urljoin(base_url, href),
                    "fetch_time": now
                })
    except: pass
    return items

def main():
    aca_data = []
    pol_data = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 【学术前沿】落实多维度内容 ---
    
    # 1. 最新研究成果 & 现状 (科学网-新闻)
    aca_data += fetch_list("news.sciencenet.cn/news-news.aspx", "成果/现状", r'<a href="(htmlnews/.*?)" .*?>(.*?)</a>', "http://news.sciencenet.cn/")
    
    # 2. 学术会议 & 交流活动 (学术会议在线)
    aca_data += fetch_list("https://www.meeting.edu.cn/zh/meeting/list/0", "活动/交流", r'<a href="(/zh/meeting/.*?)" .*?>(.*?)</a>', "https://www.meeting.edu.cn")
    
    # 3. 期刊变动 & 综合通知 (社科网)
    aca_data += fetch_list("http://www.cssn.cn/zx/zx_gx/", "期刊/通知", r'<a href="(.*?.shtml)".*?>(.*?)</a>', "http://www.cssn.cn/zx/zx_gx/")

    # --- 【政策动态】落实官方权威发布 ---
    
    # 1. 教育部政策发布
    pol_data += fetch_list("http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", "政策", r'<a href="(./.*?)" .*?>(.*?)</a>', "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/")
    
    # 2. 社科规划办 (比赛/资助/通知)
    pol_data += fetch_list("http://www.nopss.gov.cn/GB/219461/index.html", "资助/通知", r'<a href="(.*?)" .*?>(.*?)</a>', "http://www.nopss.gov.cn/")

    # 兜底逻辑：如果政策依然抓不到，手动加入跳转
    if not pol_data:
        pol_data = [{"title": "[政策] 正在实时同步教育部最新文件...", "url": "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", "fetch_time": now_str}]

    # 最终汇总
    db = {
        "academic": aca_data[:30], # 限制数量，保证加载速度
        "policy": pol_data[:15],
        "update_time": now_str
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print(f"Update Success: Aca({len(aca_data)}), Pol({len(pol_data)})")

if __name__ == "__main__":
    main()
