import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AcademicScraper:
    def __init__(self):
        self.results = {"academic": [], "policy": [], "update_time": ""}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer': 'https://www.baidu.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

    def fetch(self, url, site_name, category, selector=None):
        try:
            res = requests.get(url, headers=self.headers, timeout=25, verify=False)
            res.encoding = 'utf-8' # 强制统一编码
            soup = BeautifulSoup(res.text, 'lxml')
            
            target = soup.select_one(selector) if selector else soup
            if not target: target = soup

            links = target.find_all('a')
            count = 0
            
            # 严格过滤黑名单
            blacklist = ['备案', '跳转', '点击这里', '登录', '注册', 'About', 'English', '版权', '隐私', '联系', '首页']
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                full_url = urljoin(url, href)
                
                # 核心过滤：长度 12-60，排除黑名单
                if 12 <= len(title) <= 60 and full_url.startswith('http'):
                    if not any(word in title for word in blacklist):
                        self.results[category].append({
                            "title": f"[{site_name}] {title}",
                            "url": full_url
                        })
                        count += 1
                if count >= 8: break
            print(f"✅ {site_name} 成功获取: {count} 条")
        except Exception as e:
            print(f"❌ {site_name} 失败: {e}")

    def run(self):
        # 换用对海外 IP 响应更友好的高质量数据源
        tasks = [
            # --- Academic (学术前沿) ---
            {"site": "科学网", "url": "https://news.sciencenet.cn/", "cate": "academic", "sel": "#list_inner"},
            {"site": "中科院", "url": "https://www.cas.cn/syky/", "cate": "academic", "sel": ".m_list"},
            
            # --- Policy (政策公告) ---
            # 基金委公告 (NSFC)
            {"site": "基金委", "url": "https://www.nsfc.gov.cn/publish/portal0/tab38/", "cate": "policy", "sel": "#articleList"},
            # 中国政府网 (科技政策)
            {"site": "科技政策", "url": "https://www.gov.cn/zhengce/zhengceku/index.htm", "cate": "policy", "sel": ".list"}
        ]

        for t in tasks:
            self.fetch(t["url"], t["site"], t["cate"], t["sel"])
            time.sleep(2)

        self.results["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    AcademicScraper().run()
