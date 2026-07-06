import os
import random
import requests
from datetime import datetime
import schedule
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

POETRY_URL = "https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master/json/poet.tang.0.json"

def get_random_poem():
    try:
        resp = requests.get(POETRY_URL, timeout=15)
        poems = resp.json()
        poem = random.choice(poems)
        
        title = poem.get("title", "无题")
        author = poem.get("author", "佚名")
        content = "\n".join(poem.get("paragraphs", ["暂无内容"]))
        
        return f"""📜 **{title}**  
— {author}

{content}

🌸 每日一诗 · {datetime.now().strftime("%Y年%m月%d日")}"""
    except:
        return "今日诗词加载失败～请稍后再试。"

def send_poem():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 未设置 Token 或 Chat ID")
        return
    message = get_random_poem()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=data)
    print(f"✅ {datetime.now().strftime('%H:%M')} 推送成功")

if __name__ == "__main__":
    print("🤖 古诗 Bot 已启动...")
    send_poem()                     # 启动时立即推送一次
    schedule.every().day.at("08:00").do(send_poem)   # 每天早上8点推送
    
    while True:
        schedule.run_pending()
        time.sleep(60)
