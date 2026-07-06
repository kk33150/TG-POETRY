import os
from datetime import datetime
import time
import requests
import re

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_random_poem_data():
    """获取古诗词数据，返回标题、作者、朝代和内容"""
    try:
        resp = requests.get("https://v1.jinrishici.com/all.json", timeout=10)
        data = resp.json()
        return {
            "title": data.get("title", "无题"),
            "author": data.get("author", "佚名"),
            "dynasty": data.get("dynasty", "唐"),
            "content": data.get("content", "")
        }
    except Exception as e:
        print(f"接口请求失败: {e}，启用备用古诗")
        return {
            "title": "送杜少府之任蜀州",
            "author": "王勃",
            "dynasty": "唐",
            "content": "城阙辅三秦，风烟望五津。与君离别意，同是宦游人。海内存知己，天涯若比邻。无为在歧路，儿女共沾巾。"
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
    
    poem = get_random_poem_data()
    
    # 1. 先发送报幕信息（标题和作者）
    intro_msg = f"📜 **《{poem['title']}》**\n— [{poem['dynasty']}] {poem['author']}"
    send_telegram_msg(intro_msg)
    time.sleep(1.5)  # 稍微停顿一下
    
    # 2. 将内容切分成单独的句子
    # 使用正则，按照 逗号、句号、感叹号、问号、分号 以及换行符 切分
    sentences = re.split(r'[，。！？；\n]', poem['content'])
    # 过滤掉切分出来的空字符串
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 3. 开启连珠炮模式，一句一句发
    for sentence in sentences:
        print(f"正在推送: {sentence}")
        send_telegram_msg(sentence)
        time.sleep(1.5)  # 每句之间延迟 1.5 秒
        
    print(f"✅ {datetime.now().strftime('%H:%M:%S')} 瀑布流推送完成")

if __name__ == "__main__":
    print("🤖 古诗级联推送 Bot 已启动...")
    send_poem_stream()  # 启动时立即测试一次
    
    last_pushed_date = ""
    
    while True:
        # 锁定北京时间 (GMT+8)
        tz_offset = 8 * 3600
        current_bj_time = datetime.fromtimestamp(time.time() + tz_offset)
        
        current_date = current_bj_time.strftime("%Y-%m-%d")
        current_hour = current_bj_time.strftime("%H:%M")
        
        if current_hour == "08:00" and last_pushed_date != current_date:
            print(f"⏰ 到达目标时间 08:00，开始轰炸推送...")
            send_poem_stream()
            last_pushed_date = current_date
            
        time.sleep(30)
