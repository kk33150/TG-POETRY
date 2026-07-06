import os
from datetime import datetime
import time
import requests

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_random_poem():
    try:
        # 使用今日诗词官方开放接口，只返回单首诗，响应极快
        resp = requests.get("https://v1.jinrishici.com/all.json", timeout=10)
        data = resp.json()
        
        title = data.get("title", "无题")
        author = data.get("author", "佚名")
        dynasty = data.get("dynasty", "唐")
        content = data.get("content", "暂无内容")
        
        message = f"""📜 **{title}**  
— [{dynasty}] {author}

{content}

🌸 每日一诗 · {datetime.now().strftime("%Y年%m月%d日")}"""
        return message
    except Exception as e:
        # 备用方案：万一接口挂了，返回一首固定的诗防止崩掉
        return f"""📜 **送杜少府之任蜀州**  
— [唐] 王勃

城阙辅三秦，风烟望五津。
与君离别意，同是宦游人。
海内存知己，天涯若比邻。
无为在歧路，儿女共沾巾。

🌸 每日一诗 · {datetime.now().strftime("%Y年%m月%d日")}"""

def send_poem():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 未设置 BOT_TOKEN 或 CHAT_ID")
        return
    
    message = get_random_poem()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200:
            print(f"✅ {datetime.now().strftime('%H:%M:%S')} 推送成功")
        else:
            print(f"❌ 推送失败 状态码: {r.status_code}, 原因: {r.text}")
    except Exception as e:
        print("发送异常:", e)

if __name__ == "__main__":
    print("🤖 古诗 Bot 已常驻启动...")
    send_poem()  # 启动时立即推送一次，方便你在 Railway 部署完看效果
    
    # 记录最后一次推送的“日期”
    last_pushed_date = ""
    
    while True:
        # 获取当前的北京时间 (GMT+8)
        # 这一步很关键！直接通过 offset 计算出北京时间，不受 Railway 服务器时区影响
        tz_offset = 8 * 3600
        current_bj_time = datetime.fromtimestamp(time.time() + tz_offset)
        
        current_date = current_bj_time.strftime("%Y-%m-%d")
        current_hour = current_bj_time.strftime("%H:%M")
        
        # 判断时间：如果是早上 08:00，且今天还没推送过
        if current_hour == "08:00" and last_pushed_date != current_date:
            print(f"⏰ 到达目标时间 08:00，开始今日推送...")
            send_poem()
            last_pushed_date = current_date  # 标记今天已推送，防止这一分钟内重复触发
            
        # 每隔 30 秒检查一次时间
        time.sleep(30)
