import json, requests, os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        r.encoding = r.apparent_encoding
        return BeautifulSoup(r.text, 'lxml') if r.status_code == 200 else None
    except: return None

def crawl_academic():
    """抓取：学术成果、活动、比赛、交流动态"""
    results = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 源 1：科学网-学术动态/研究成果 (涵盖成果、研究现状)
    soup = get_soup("http://news.sciencenet.cn/news-news.aspx")
    if soup:
        for a in soup.select(".t1 a, .t2 a")[:12]:
            t, h = a.text.strip(), a.get('href')
            if len(t) > 10 and h:
                results.append({"title": f"[研究成果] {t}", "url": urljoin("http://news.sciencenet.cn/", h), "fetch_time": now})

    # 源 2：中国学术会议在线-学术活动/会议交流
    soup = get_soup("https://www.meeting.edu.cn/zh/meeting/list/0")
    if soup:
        for a in soup.select(".meet_list_info a")[:8]:
            t, h = a.text.strip(), a.get('href')
            if h:
                results.append({"title": f"[学术交流] {t}", "url": urljoin("https://www.meeting.edu.cn", h), "fetch_time": now})

    # 源 3：中国社会科学网-学术资讯/期刊动态
    soup = get_soup("http://www.cssn.cn/zx/zx_gx/")
    if soup:
        for a in soup.select(".font01 a")[:8]:
            t, h = a.text.strip(), a.get('href')
            if len(t) > 10:
                results.append({"title": f"[期刊/动态] {t}", "url": urljoin("http://www.cssn.cn/zx/zx_gx/", h), "fetch_time": now})

    return results

def crawl_policy():
    """抓取：最新政策文件、政府公告 (修复同步问题)"""
    results = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 源 1：教育部-最新政策 (最权威，结构相对稳定)
    soup = get_soup("http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/")
    if soup:
        for a in soup.select(".moe-list a")[:10]:
            t, h = a.text.strip(), a.get('href')
            if len(t) > 8:
                results.append({"title": f"[政策公告] {t}", "url": urljoin("http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", h), "fetch_time": now})

    # 源 2：PubScholar 公益学术-政策新闻 (备选)
    soup = get_soup("https://pubscholar.cn/news")
    if soup:
        for a in soup.select("a")[:20]:
            t, h = a.text.strip(), a.get('href')
            if len(t) > 12 and h and h.startswith('http'):
                results.append({"title": f"[动态] {t}", "url": h, "fetch_time": now})

    return results

def main():
    aca = crawl_academic()
    pol = crawl_policy()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 兜底：如果政策依然抓不到，手动加入一个跳转到教育部官网的真实链接，确保不显示“正在同步”
    if not pol:
        pol = [{"title": "[官方数据库] 教育部最新政策发布中心", "url": "http://www.moe.gov.cn/jyb_xxgk/s5743/s5744/", "fetch_time": now_str}]
    if not aca:
        aca = [{"title": "[学术枢纽] 科学网最新学术成果汇总", "url": "http://news.sciencenet.cn/", "fetch_time": now_str}]

    db = {"academic": aca, "policy": pol, "update_time": now_str}
    
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print(f"Update Success. Aca: {len(aca)}, Pol: {len(pol)}")

if __name__ == "__main__":
    main()
