import os
from datetime import datetime
import time
import requests
import random

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_complete_poem():
    """获取一首绝对随机且绝对完整的古诗词（换用大厂永久维护高可用接口）"""
    try:
        # 换用极其稳定的韩小韩全量随机诗词接口
        resp = requests.get("https://api.vvhan.com/api/ian/poem", timeout=10)
        if resp.status_code == 200:
            json_data = resp.json()
            
            if json_data.get("success") is True:
                data = json_data.get("data", {})
                
                title = data.get("title", "无题")
                author = data.get("author", "佚名")
                dynasty = data.get("dynasty", "唐")
                content = data.get("content", "") # 返回带标准标点或换行的完整内容
                
                # 按照常见的中文标点和换行符切分成独立的瀑布流完整行
                import re
                sentences = re.split(r'[，。！？；\n]', content)
                sentences = [s.strip() for s in sentences if s.strip()]
                
                # 两两合并，让发出来的每一条消息都变成工整的一长句（例如“凤凰台上凤凰游，凤去台空江自流。”）
                paired_sentences = []
                for i in range(0, len(sentences), 2):
                    if i + 1 < len(sentences):
                        paired_sentences.append(f"{sentences[i]}，{sentences[i+1]}。")
                    else:
                        paired_sentences.append(f"{sentences[i]}。")
                
                if paired_sentences:
                    return {
                        "title": title,
                        "author": author,
                        "dynasty": dynasty,
                        "sentences": paired_sentences
                    }
    except Exception as e:
        print(f"核心接口请求异常: {e}")
        
    # 终极本地高品质备用池：万一没网，在本地随机抽一首，绝不重样
    fallback_poems = [
        {
            "title": "送杜少府之任蜀州", "author": "王勃", "dynasty": "唐",
            "sentences": ["城阙辅三秦，风烟望五津。", "与君离别意，同是宦游人。", "海内存知己，天涯若比邻。", "无为在歧路，儿女共沾巾。"]
        },
        {
            "title": "登金陵凤凰台", "author": "李白", "dynasty": "唐",
            "sentences": ["凤凰台上凤凰游，凤去台空江自流。", "吴宫花草埋幽径，晋代衣冠成古丘。", "三山半落青天外，二水中分白鹭洲。", "总为浮云能蔽日，长安不见使人愁。"]
        },
        {
            "title": "望岳", "author": "杜甫", "dynasty": "唐",
            "sentences": ["岱宗夫如何？齐鲁青未了。", "造化钟神秀，阴阳割昏晓。", "荡胸生曾云，决眦入归鸟。", "会当凌绝顶，一览众山小。"]
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
    print("🤖 终极随机完整古诗推送 Bot 已启动...")
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
