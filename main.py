import json
from datetime import datetime

def get_data():
    # 模拟抓取：实际操作中你可以使用 requests 分别抓取各站 RSS 或 HTML
    data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "academic": [
            {"title": "万方：新型复合材料研究进展", "url": "https://www.wanfangdata.com.cn"},
            {"title": "Google Scholar: Machine Learning in Engineering", "url": "https://scholar.google.com"}
        ],
        "policy": [
            {"title": "科技部：关于进一步加强科研诚信建设的若干意见", "url": "https://www.most.gov.cn"},
            {"title": "教育部：2026年高校科研经费分配方案", "url": "http://www.moe.gov.cn"}
        ]
    }
    return data

def save_json(data):
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    save_json(get_data())
