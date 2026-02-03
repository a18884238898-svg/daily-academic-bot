import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from urllib.parse import urljoin
import urllib3

# 禁用 SSL 证书警告（防止部分政府网站证书过期导致程序中断）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AcademicScraper:
    def __init__(self):
        self.results = {"academic": [], "policy": [], "update_time": ""}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

    def fetch(self, url, site_name, category, selector=None):
        print(f"📡 正在尝试抓取: {site_name}...")
        try:
            # 伪装来源：让服务器认为我们是从百度或者知网过来的
            current_headers = self.headers.copy()
            current_headers['Referer'] = 'https://www.baidu.com/'
            
            response = requests.get(url, headers=current_headers, timeout=25, verify=False)
            response.encoding = response.apparent_encoding # 自动纠正 GBK/UTF-8 编码
            
            if response.status_code != 200:
                print(f"⚠️ {site_name} 返回状态码: {response.status_code} (可能被屏蔽)")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找内容：如果没设选择器，则全站搜寻 <a> 标签
            target_area = soup.select_one(selector) if selector else soup
            if not target_area:
                target_area = soup

            links = target_area.find_all('a')
            count = 0
            
            # 过滤逻辑：去掉短词（如“更多”、“登录”），保留长标题
            blacklist = ['备案', '版权', '登录', '注册', 'About', 'English', 'Français', '更多', '联系']
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                # 补全 URL
                full_url = urljoin(url, href)
                
                # 判定为有效新闻的条件：标题长度在 12-50 之间，且不在黑名单中
                if 12 <= len(title) <= 55 and full_url.startswith('http'):
                    if not any(word in title for word in blacklist):
                        self.results[category].append({
                            "title": f"[{site_name}] {title}",
                            "url": full_url
                        })
                        count += 1
                
                if count >= 8: break # 每个站点最多取 8 条
            
            print(f"✅ {site_name} 成功获取 {count} 条")
            
        except Exception as e:
            print(f"❌ {site_name} 抓取异常: {str(e)}")

    def run(self):
        # --- 任务配置清单 ---
        tasks = [
            # 学术前沿 (Academic)
            {"site": "科学网", "url": "https://news.sciencenet.cn/", "cate": "academic", "sel": "#list_inner"},
            {"site": "社科网", "url": "http://www.cssn.cn/zx/zx_gx/", "cate": "academic", "sel": ".list_ul"},
            {"site": "PubScholar", "url": "https://pubscholar.cn/news/index", "cate": "academic", "sel": ".list-content"},
            {"site": "学术会议", "url": "https://www.meeting.edu.cn/zh/meeting/list", "cate": "academic", "sel": ".list-item-box"},
            
            # 政策论坛 (Policy)
            {"site": "学位中心", "url": "https://www.cdgdc.edu.cn/xwyyjsjyxx/index.shtml", "cate": "policy", "sel": ".news_list"},
            {"site": "文献中心", "url": "http://www.ncpssd.org/notice.aspx", "cate": "policy", "sel": ".list_con"},
            {"site": "小木虫", "url": "http://muchong.com/bbs/index.php?gid=29", "cate": "policy", "sel": ".stitle"}
        ]

        for t in tasks:
            self.fetch(t["url"], t["site"], t["cate"], t["sel"])
            time.sleep(2) # 礼貌延迟，防止 GitHub IP 被封

        # 更新时间戳
        self.results["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 写入文件
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        print("🎉 抓取任务圆满结束！")

if __name__ == "__main__":
    scraper = AcademicScraper()
    scraper.run()
