import json, requests, re, os
from datetime import datetime
from urllib.parse import unquote

def fetch_rss_simple(url, tag_prefix="[动态]"):
    """
    使用正则手动解析 RSS，不依赖外部库，防止 GitHub 环境报错
    """
    items = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # 设置更长超时，防止网络波动
        r = requests.get(url, timeout=30)
        r.encoding = 'utf-8'
        content = r.text
        
        # 提取 item 块
        entries = re.findall(r'<item>(.*?)</item>', content, re.S)
        for entry in entries[:15]:
            title_match = re.search(r'<title>(.*?)</title>', entry, re.S)
            link_match = re.search(r'<link>(.*?)</link>', entry, re.S)
            
            if title_match and link_match:
                title = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                link = link_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                items.append({
                    "title": f"{tag_prefix} {title}",
                    "url": link,
                    "fetch_time": now
                })
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return items

def main():
    # --- 1. 学术前沿 (使用科学网 RSS + arXiv RSS) ---
    # 科学网论文频道 RSS 是目前最稳定的学术新闻源
    academic = fetch_rss_simple("https://www.sciencenet.cn/xml/news.xml?di=0", "[成果]")
    # 如果科学网挂了，换 arXiv (AI领域示例)
    if not academic:
        academic = fetch_rss_simple("https://export.arxiv.org/rss/cs.AI", "[论文]")

    # --- 2. 政策动态 (使用权威机构 RSS 或 聚合源) ---
    # 我们使用一个镜像聚合源来获取教育政策，防止直连教育部被封
    policy = fetch_rss_simple("https://www.sciencenet.cn/xml/news.xml?di=2", "[政策]")
    
    # --- 3. 汇总 ---
    db = {
        "academic": academic,
        "policy": policy,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # --- 4. 救生圈：如果连 RSS 都抓不到，存入真实有效的静态链接 ---
    if not db["academic"]:
        db["academic"] = [{"title": "[官方] 科学网学术论文中心", "url": "https://news.sciencenet.cn/paper/index.aspx", "fetch_time": db["update_time"]}]
    if not db["policy"]:
        db["policy"] = [{"title": "[官方] 中华人民共和国教育部政策发布", "url": "http://www.moe.gov.cn/jyb_xwfb/s5147/sjfb/", "fetch_time": db["update_time"]}]

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print(f"Sync complete. Aca: {len(academic)}, Pol: {len(policy)}")

if __name__ == "__main__":
    main()
