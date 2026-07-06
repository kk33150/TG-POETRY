import os
from datetime import datetime
import time
import requests
import re
import random

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_complete_poem():
    """获取一首绝对完整的古诗词（完全随机）"""
    try:
        # 随机生成一个页码（1 到 1000 页），确保每次请求和测试都是全新的诗
        random_page = random.randint(1, 1000)
        url = f"https://api.apiopen.top/api/getTangPoetry?page={random_page}&size=1"
        
        resp = requests.get(url, timeout=10)
        json_data = resp.json()
        
        if json_data.get("code") == 200 and json_data.get("result"):
            item = json_data["result"][0]
            # 过滤掉内容里的换行和杂质，统一用标准的中文句号或换行来处理
            raw_content = item.get("content", "")
            # 将古诗内容按行切分
            sentences = [s.strip() for s in raw_content.split("|") if s.strip()]
            if not sentences:
                sentences = [s.strip() for s in raw_content.split("\n") if s.strip()]
                
            return {
                "title": item.get("title", "无题"),
                "author": item.get("author", "佚名"),
                "dynasty": "唐",
                "sentences": sentences
            }
    except Exception as e:
        print(f"完整接口请求失败: {e}，启用高品质备用完整古诗")
        
    # 备用方案：给一首绝对完整且意境极佳的诗
    return {
        "title": "送杜少府之任蜀州",
        "author": "王勃",
        "dynasty": "唐",
        "sentences": [
            "城阙辅三秦，风烟望五津。",
            "与君离别意，同是宦游人。",
            "海内存知己，天涯若比邻。",
            "无为在歧路，儿女共沾巾。"
        ]
    }

def send_telegram_msg(text):
    """封装底层的单条消息发送逻辑"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=data, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"发送单条异常: {e}")
        return False

def send_poem_stream():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 未设置 BOT_TOKEN 或 CHAT_ID")
        return
    
    poem = get_complete_poem()
    
    # 1. 先发送报幕信息（标题和作者）
    intro_msg = f"📜 **《{poem['title']}》**\n— [{poem['dynasty']}] {poem['author']}"
    send_telegram_msg(intro_msg)
    time.sleep(2.0)  # 报幕后稍微多停顿一下，准备高潮
    
    # 2. 开启连珠炮模式，整行整行地发（例如：城阙辅三秦，风烟望五津。）
    for sentence in poem['sentences']:
        print(f"正在推送完整行: {sentence}")
        send_telegram_msg(sentence)
        time.sleep(2.0)  # 每完整行之间延迟 2 秒，节奏更舒服
        
    print(f"✅ {datetime.now().strftime('%H:%M:%S')} 完整瀑布流推送完成")

if __name__ == "__main__":
    print("🤖 完整古诗级联推送 Bot 已启动...")
    send_poem_stream()  # 启动时立即测试
    
    last_pushed_date = ""
    
    while True:
        # 锁定北京时间 (GMT+8)
        tz_offset = 8 * 3600
        current_bj_time = datetime.fromtimestamp(time.time() + tz_offset)
        
        current_date = current_bj_time.strftime("%Y-%m-%d")
        current_hour = current_bj_time.strftime("%H:%M")
        
        if current_hour == "08:00" and last_pushed_date != current_date:
            print(f"⏰ 到达目标时间 08:00，开始完整推送...")
            send_poem_stream()
            last_pushed_date = current_date
            
        time.sleep(30)
