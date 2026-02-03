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
            'Referer': 'https://www.baidu.com/'
        }

    def fetch(self, url, site_name, category, selector=None):
        try:
            res = requests.get(url, headers=self.headers, timeout=30, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'lxml')
            
            # 如果有选择器则锁定区域，没有则扫描全身
            target = soup.select_one(selector) if selector else soup
            if not target: target = soup

            links = target.find_all('a')
            count = 0
            
            # 严格黑名单：剔除干扰链接
            blacklist = ['备案', '版权', 'ICP', '公安', '登录', '注册', 'About', 'English', '更多', '首页', '联系']
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                full_url = urljoin(url, href)
                
                # 判定逻辑：标题 10-60 字，URL 必须合法
                if 10 <= len(title) <= 60 and full_url.startswith('http'):
                    if not any(word in title for word in blacklist):
                        # 特殊过滤：如果是 Policy 类别，我们要确保它看起来像条新闻或公告
                        self.results[category].append({
                            "title": f"[{site_name}] {title}",
                            "url": full_url
                        })
                        count += 1
                if count >= 8: break
            print(f"✅ {site_name} 抓取结果: {count} 条")
        except Exception as e:
            print(f"❌ {site_name} 抓取异常: {e}")

    def run(self):
        # 任务清单：换用更直接的子页面链接
        tasks = [
            # --- Academic 类 (目前最稳) ---
            {"site": "科学网", "url": "https://news.sciencenet.cn/", "cate": "academic", "sel": "#list_inner"},
            {"site": "社科前沿", "url": "http://www.cssn.cn/zx/zx_gx/", "cate": "academic", "sel": ".list_ul"},
            
            # --- Policy 类 (重点抢救) ---
            # 1. 学术会议在线：换成列表页，去掉选择器全页扫描
            {"site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list", "cate": "policy", "sel": None},
            # 2. 社科文献中心：公告页
            {"site": "社科文献", "url": "http://www.ncpssd.org/notice.aspx", "cate": "policy", "sel": ".list_con"},
            # 3. 小木虫：锁定学术动态版块
            {"site": "小木虫", "url": "http://muchong.com/bbs/index.php?gid=29", "cate": "policy", "sel": ".stitle"}
        ]

        for t in tasks:
            self.fetch(t["url"], t["site"], t["cate"], t["sel"])
            time.sleep(2)

        self.results["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    AcademicScraper().run()
