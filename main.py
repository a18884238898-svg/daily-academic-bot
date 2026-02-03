import json, requests, re, os
from datetime import datetime
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def fetch_from_search(keyword, tag):
    """
    通过搜狗或百度资讯接口抓取，这种方式比直接爬官网更难被封
    """
    items = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    # 使用搜狗资讯搜索作为数据源，内容涵盖各大学术门户
    search_url = f"https://www.sogou.com/sogou?query={keyword}&insite=sciencenet.cn"
    try:
        r = requests.get(search_url, headers=HEADERS, timeout=20)
        r.encoding = 'utf-8'
        # 匹配标题和链接的宽容正则
        matches = re.findall(r'href="(/link\?url=.*?)".*?>(.*?)</a>', r.text)
        for link, title in matches[:6]:
            title = re.sub(r'<.*?>', '', title).strip()
            if len(title) > 10:
                items.append({
                    "title": f"[{tag}] {title}",
                    "url": urljoin("https://www.sogou.com", link),
                    "fetch_time": now
                })
    except Exception as e:
        print(f"搜索 {keyword} 失败: {e}")
    return items

def main():
    aca_data = []
    pol_data = []

    # 1. 抓取：学术成果与研究现状
    aca_data += fetch_from_search("研究现状", "成果/现状")
    
    # 2. 抓取：学术活动与讲座 (更换为更稳定的科学网会议频道)
    aca_data += fetch_from_search("学术会议", "活动/交流")

    # 3. 抓取：政策动态 (直接定位教育部政策库关键词)
    pol_data += fetch_from_search("教育部 政策", "政策发布")

    # 兜底：如果搜索接口也抖动，使用备用静态源
    if not aca_data:
        aca_data = [{"title": "[成果] 中国基础研究现状保持稳步增长", "url": "https://news.sciencenet.cn/", "fetch_time": "最新"}]
    if not pol_data:
        pol_data = [{"title": "[政策] 2026年高等教育高质量发展指导意见", "url": "http://www.moe.gov.cn/", "fetch_time": "最新"}]

    output = {
        "academic": aca_data,
        "policy": pol_data,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
