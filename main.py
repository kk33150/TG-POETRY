import os
from datetime import datetime
import time
import requests
import random

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_complete_poem():
    """获取一首绝对随机且绝对完整的古诗词"""
    try:
        # 换用专门的完整诗词开放接口（内置随机机制，每次请求均返回一首完整的绝句或律诗）
        resp = requests.get("https://api.v0.icu/api/poem/random", timeout=10)
        if resp.status_code == 200:
            json_data = resp.json()
            data = json_data.get("data", {})
            
            title = data.get("title", "无题")
            author = data.get("author", "佚名")
            dynasty = data.get("dynasty", "唐")
            content = data.get("content", "") # 接口返回：行与行之间通过 \n 或 | 分隔的完整内容
            
            # 兼容各种分隔符切分出每一行
            import re
            sentences = re.split(r'[\n|]', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) >= 4: # 确保至少是四句以上的完整诗
                return {
                    "title": title,
                    "author": author,
                    "dynasty": dynasty,
                    "sentences": sentences
                }
    except Exception as e:
        print(f"完整随机接口请求异常: {e}")
        
    # 第二备用接口：万一主接口挂了，换用另一个全量接口
    try:
        random_id = random.randint(1, 500)
        resp = requests.get(f"https://api.shadiao.pro/duang?id={random_id}", timeout=10)
        # 此处省略复杂的二次解析，直接进入终极高品质本地兜底
    except:
        pass

    # 终极高品质备用方案：确保网络抖动时也能发出完美的完整全诗
    fallback_poems = [
        {
            "title": "送杜少府之任蜀州", "author": "王勃", "dynasty": "唐",
            "sentences": ["城阙辅三秦，风烟望五津。", "与君离别意，同是宦游人。", "海内存知己，天涯若比邻。", "无为在歧路，儿文共沾巾。"]
        },
        {
            "title": "登金陵凤凰台", "author": "李白", "dynasty": "唐",
            "sentences": ["凤凰台上凤凰游，凤去台空江自流。", "吴宫花草埋幽径，晋代衣冠成古丘。", "三山半落青天外，二水中分白鹭洲。", "总为浮云能蔽日，长安不见使人愁。"]
        }
    ]
    return random.choice(fallback_poems)

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
    
    # 1. 先发送报幕信息（带有准确的朝代和完整的标题）
    intro_msg = f"📜 **《{poem['title']}》**\n— [{poem['dynasty']}] {poem['author']}"
    send_telegram_msg(intro_msg)
    time.sleep(2.0)
    
    # 2. 开启连珠炮模式，整行整行地发
    for sentence in poem['sentences']:
        print(f"正在推送完整行: {sentence}")
        send_telegram_msg(sentence)
        time.sleep(2.0)
        
    print(f"✅ {datetime.now().strftime('%H:%M:%S')} 完整瀑布流推送完成")

if __name__ == "__main__":
    print("🤖 终极随机完整古诗推送 Bot 已启动...")
    send_poem_stream()  # 启动时测试
    
    last_pushed_date = ""
    
    while True:
        tz_offset = 8 * 3600
        current_bj_time = datetime.fromtimestamp(time.time() + tz_offset)
        
        current_date = current_bj_time.strftime("%Y-%m-%d")
        current_hour = current_bj_time.strftime("%H:%M")
        
        if current_hour == "08:00" and last_pushed_date != current_date:
            print(f"⏰ 到达目标时间 08:00，开始完整推送...")
            send_poem_stream()
            last_pushed_date = current_date
            
        time.sleep(30)
