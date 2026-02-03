import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_real_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    data = {"update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "academic": [], "policy": []}

    # 1. 抓取 arXiv 具体论文链接
    try:
        # 使用人工智能分类的 RSS
        rss_url = "https://export.arxiv.org/rss/cs.AI"
        resp = requests.get(rss_url, timeout=10)
        # 解析 XML
        root = ET.fromstring(resp.content)
        # 这里的 namespace 必须处理准确，否则取不到具体的 link
        ns = {'rss': 'http://purl.org/rss/1.0/'}
        for item in root.findall('.//rss:item', ns)[:10]:
            title = item.find('rss:title', ns).text.strip()
            # 获取具体文章链接（例如 https://arxiv.org/abs/xxxx.xxxxx）
            link = item.find('rss:link', ns).text.strip()
            data["academic"].append({
                "title": title,
                "url": link, # 这里现在是具体页面链接
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    except Exception as e:
        print(f"学术抓取失败: {e}")

    # 2. 抓取具体政策链接 (示例：科技部)
    # 提示：实际生产中需要 BeautifulSoup 解析具体的 <a> 标签 href 属性
    data["policy"].append({
        "title": "科技部关于发布国家重点研发计划的通知",
        "url": "https://www.most.gov.cn/tztg/202601/t20260101_12345.html", # 示例具体页
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_real_data()
