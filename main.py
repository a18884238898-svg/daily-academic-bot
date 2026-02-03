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
            # 针对国内部分高校/政府网，尝试增加特定请求头绕过海外拦截
            res = requests.get(url, headers=self.headers, timeout=25, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'lxml')
            
            target = soup.select_one(selector) if selector else soup
            if not target: target = soup

            links = target.find_all('a')
            count = 0
            
            # 🔴 核心改进：极其严格的黑名单，彻底过滤备案号和无效链接
            blacklist = ['备案', '版权', 'ICP', '公网安备', '登录', '注册', 'About', 'English', 'Français', '更多', '联系', '返回', '首页', '小木虫论坛']
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                full_url = urljoin(url, href)
                
                # 🟡 核心改进：标题必须包含新闻特征，且长度适中
                if 12 <= len(title) <= 60 and full_url.startswith('http'):
                    if not any(word in title for word in blacklist):
                        # 额外校验：排除那些纯数字或明显不是新闻的链接
                        if title.isdigit() or len(set(title)) < 5: continue
                        
                        self.results[category].append({
                            "title": f"[{site_name}] {title}",
                            "url": full_url
                        })
                        count += 1
                if count >= 10: break
            
            print(f"✅ {site_name} 抓取成功: {count} 条")
        except Exception as e:
            print(f"❌ {site_name} 失败: {e}")

    def run(self):
        tasks = [
            # 1. 科学网 (已经通了，保持原样)
            {"site": "科学网", "url": "https://news.sciencenet.cn/", "cate": "academic", "sel": "#list_inner"},
            
            # 2. 社科网 (尝试更换为新闻子频道，绕过首页拦截)
            {"site": "社科网", "url": "http://www.cssn.cn/zx/zx_gx/", "cate": "academic", "sel": ".list_ul"},
            
            # 3. 学术会议 (更换具体分类页)
            {"site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list", "cate": "academic", "sel": ".list-item-box"},
            
            # 4. 小木虫 (锁定今日头条区)
            {"site": "小木虫", "url": "http://muchong.com/bbs/index.php?gid=29", "cate": "policy", "sel": ".stitle"},
            
            # 5. 文献中心 (政府背景，易被挡)
            {"site": "文献中心", "url": "http://www.ncpssd.org/notice.aspx", "cate": "policy", "sel": ".list_con"}
        ]

        for t in tasks:
            self.fetch(t["url"], t["site"], t["cate"], t["sel"])
            time.sleep(2)

        self.results["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    AcademicScraper().run()
