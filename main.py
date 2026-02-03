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
            
            target = soup.select_one(selector) if selector else soup
            if not target: target = soup

            links = target.find_all('a')
            count = 0
            
            # 🛑 极其严格的过滤黑名单
            blacklist = ['备案', '版权', 'ICP', '公安', '登录', '注册', 'About', 'English', '更多', '首页', '联系', '互动平台', '返回', '论坛']
            # ✅ 正向特征：标题中通常包含的学术/新闻关键词
            keywords = ['项目', '获', '揭示', '研究', '通知', '公告', '会议', '发展', '建设', '发布', '成果', '半导体', '装置', '机制', '突破']

            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                full_url = urljoin(url, href)
                
                # 过滤逻辑：1. 长度必须在 12-60 之间； 2. 不含黑名单词汇； 3. 不能是纯数字
                if 12 <= len(title) <= 60 and full_url.startswith('http'):
                    if not any(word in title for word in blacklist):
                        # 排除掉类似 "京公网安备xxx" 或者 "小木虫-学术..." 这种固定标题
                        if "1101" in title or "备" in title: continue
                        
                        self.results[category].append({
                            "title": f"[{site_name}] {title}",
                            "url": full_url
                        })
                        count += 1
                if count >= 8: break
            print(f"✅ {site_name} 有效数据: {count} 条")
        except Exception as e:
            print(f"❌ {site_name} 失败: {e}")

    def run(self):
        tasks = [
            # 学术前沿 (Academic)
            {"site": "科学网", "url": "https://news.sciencenet.cn/", "cate": "academic", "sel": "#list_inner"},
            # 调整社科网链接，直接进入“高层动态”子栏目
            {"site": "社科前沿", "url": "http://www.cssn.cn/zx/zx_gx/", "cate": "academic", "sel": ".list_ul"},
            
            # 政策/会议 (Policy)
            # 调整会议在线链接，锁定最新发布
            {"site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list", "cate": "policy", "sel": ".list-item-box"},
            # 锁定小木虫的“学术动态”具体版块
            {"site": "小木虫", "url": "http://muchong.com/bbs/forumdisplay.php?fid=330", "cate": "policy", "sel": ".stitle"}
        ]

        for t in tasks:
            self.fetch(t["url"], t["site"], t["cate"], t["sel"])
            time.sleep(2)

        self.results["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    AcademicScraper().run()
