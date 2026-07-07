import os
from datetime import datetime
import time
import requests
import random

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_complete_poem():
    """从今日诗词官方全球加速接口获取绝对随机且完整的古诗词"""
    try:
        # 今日诗词官方的免费全量随机接口（自带全球 CDN 节点加速，海外服务器访问极稳）
        headers = {"X-User-Token": "v2.jinrishici.token"} # 官方公共测试 Token
        resp = requests.get("https://v2.jinrishici.com/one.json", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            json_data = resp.json()
            if json_data.get("status") == "success":
                origin = json_data.get("data", {}).get("origin", {})
                
                title = origin.get("title", "无题")
                author = origin.get("author", "佚名")
                dynasty = origin.get("dynasty", "唐")
                content_list = origin.get("content", []) # 该接口直接返回一个包含完整每行诗句的数组
                
                # 清洗一下数据，去掉空行，确保有内容
                sentences = [s.strip() for s in content_list if s.strip()]
                
                if sentences:
                    return {
                        "title": title,
                        "author": author,
                        "dynasty": dynasty,
                        "sentences": sentences
                    }
    except Exception as e:
        print(f"今日诗词接口请求异常: {e}")
        
    # 终极本地备用池（万一海外网络遇到极端波动，用于兜底）
    fallback_poems = [
        {
            "title": "送杜少府之任蜀州", "author": "王勃", "dynasty": "唐",
            "sentences": ["城阙辅三秦，风烟望五津。", "与君离别意，同是宦游人。", "海内存知己，天涯若比邻。", "无为在歧路，儿女共沾巾。"]
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
    
    # 1. 先发送报幕信息
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
    print("🤖 今日诗词全球加速版推送 Bot 已启动...")
    send_poem_stream()  # 启动时测试一次
    
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
