mport requests
import re
import json
import os
from datetime import datetime

FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
KEYWORDS = ["护肤", "穿搭", "职场"]  # 改你想要的关键词

def send_feishu(title, content):
    if not FEISHU_WEBHOOK:
        print("未配置 webhook")
        return
    payload = {
        "msg_type": "post",
        "content": {"post": {"zh_cn": {"title": title, "content": [[{"tag": "text", "text": content}]]}}}
    }
    requests.post(FEISHU_WEBHOOK, json=payload, timeout=10)

def fetch_xhs(keyword):
    url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        # 提取页面数据
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', r.text)
        if match:
            data = json.loads(match.group(1))
            notes = data.get('notes', [])[:5]  # 每个词抓5条
            return [{"title": n.get("title",""), "likes": n.get("likes",0), 
                    "link": f"https://xhs.link/{n.get('id','')}"} for n in notes]
    except Exception as e:
        print(f"失败 {keyword}: {e}")
    return []

def main():
    print(f"开始 {datetime.now()}")
    all_content = []
    for kw in KEYWORDS:
        notes = fetch_xhs(kw)
        if notes:
            content = f"【{kw}】\n"
            for i, n in enumerate(notes, 1):
                content += f"{i}. {n['title']} 👍{n['likes']}\n{n['link']}\n\n"
            all_content.append(content)
    
    if all_content:
        send_feishu(f"📕 小红书 {datetime.now().strftime('%m-%d')}", "\n".join(all_content))
        print("推送成功")
    else:
        print("无数据")

if __name__ == "__main__":
    main()
