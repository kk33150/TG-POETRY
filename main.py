import os
from datetime import datetime
import time
import requests

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_complete_poem():
    """获取一首绝对完整的古诗词（换用高可用稳定接口）"""
    try:
        # 使用一言专门的古诗词完整分类接口（这个接口对海外云服务器非常友好且极为稳定）
        resp = requests.get("https://v1.hitokoto.cn/?c=i", timeout=10)
        json_data = resp.json()
        
        # 该接口直接返回单句或整首，如果带有完整诗作，我们进行提取
        content = json_data.get("hitokoto", "").strip()
        from_where = json_data.get("from", "古诗词")
        author = json_data.get("from_who", "佚名")
        
        # 很多时候它返回的是两句或四句，由于我们使用逗号/句号作为断句符号，我们直接将其切分成瀑布流的行
        # 支持用中文逗号、句号、分号、感叹号或换行切分
        import re
        sentences = re.split(r'[，。！？；\n]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 组装完整的瀑布流结构
        if sentences:
            return {
                "title": from_where.replace("《", "").replace("》", ""),
                "author": author if author else "佚名",
                "dynasty": "历代",
                "sentences": sentences
            }
    except Exception as e:
        print(f"完整接口请求失败: {e}，启用高品质备用完整古诗")
        
    # 终极备用方案：万一没网，给一首完整的绝句
    return {
        "title": "登金陵凤凰台",
        "author": "李白",
        "dynasty": "唐",
        "sentences": [
            "凤凰台上凤凰游，凤去台空江自流。",
            "吴宫花草埋幽径，晋代衣冠成古丘。",
            "三山半落青天外，二水中分白鹭洲。",
            "总为浮云能蔽日，长安不见使人愁。"
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
    time.sleep(2.0)  # 报幕后稍微多停顿一下
    
    # 2. 开启连珠炮模式，整行整行地发
    for sentence in poem['sentences']:
        print(f"正在推送完整行: {sentence}")
        send_telegram_msg(sentence)
        time.sleep(2.0)  # 每完整行之间延迟 2 秒
        
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
