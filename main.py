import os
from datetime import datetime
import time
import requests
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==================== 赛马接口 1：今日诗词（最完整） ====================
def fetch_jinrishici():
    headers = {"X-User-Token": "v2.jinrishici.token"}
    resp = requests.get("https://v2.jinrishici.com/one.json", headers=headers, timeout=4)
    if resp.status_code == 200 and resp.json().get("status") == "success":
        origin = resp.json()["data"]["origin"]
        sentences = [s.strip() for s in origin.get("content", []) if s.strip()]
        if sentences:
            return {
                "title": origin.get("title", "无题"),
                "author": origin.get("author", "佚名"),
                "dynasty": origin.get("dynasty", "唐"),
                "sentences": sentences
            }
    raise Exception("今日诗词接口未返回有效数据")

# ==================== 赛马接口 2：韩小韩 API（完整长句版） ====================
def fetch_vvhan():
    resp = requests.get("https://api.vvhan.com/api/ian/poem", timeout=4)
    if resp.status_code == 200 and resp.json().get("success") is True:
        data = resp.json().get("data", {})
        content = data.get("content", "")
        sentences = re.split(r'[，。！？；\n]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 两两合成长句，保证句式工整
        paired = []
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                paired.append(f"{sentences[i]}，{sentences[i+1]}。")
            else:
                paired.append(f"{sentences[i]}。")
        if paired:
            return {
                "title": data.get("title", "无题"),
                "author": data.get("author", "佚名"),
                "dynasty": data.get("dynasty", "唐"),
                "sentences": paired
            }
    raise Exception("韩小韩接口未返回有效数据")

# ==================== 赛马接口 3：一言古诗词（容易残篇，用于高强度断句） ====================
def fetch_hitokoto():
    resp = requests.get("https://v1.hitokoto.cn/?c=i", timeout=4)
    if resp.status_code == 200:
        data = resp.json()
        content = data.get("hitokoto", "").strip()
        sentences = re.split(r'[，。！？；\n]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences:
            return {
                "title": data.get("from", "古诗词").replace("《", "").replace("》", ""),
                "author": data.get("from_who", "佚名") or "佚名",
                "dynasty": "历代",
                "sentences": sentences
            }
    raise Exception("一言接口未返回有效数据")


def get_complete_poem():
    """多接口并发赛马 + 严格长度质检"""
    tasks = [fetch_jinrishici, fetch_vvhan, fetch_hitokoto]
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(task): task.__name__ for task in tasks}
        
        for future in as_completed(futures):
            task_name = futures[future]
            try:
                result = future.result()
                # 🛡️ 核心质检逻辑：检查句子数量。如果是残篇（少于4句/4行），直接判定不合格，继续等别的接口
                if result and len(result.get("sentences", [])) >= 4:
                    print(f"🚀 赛马成功且通过质检！胜出接口: {task_name}，句数: {len(result['sentences'])}")
                    return result
                else:
                    print(f"⚠️ 接口 {task_name} 抢答成功，但因句数不足（少于4句）被质检拦截。")
            except Exception as e:
                print(f"⚠️ 接口 {task_name} 失败: {e}")

    print("🚨 外部所有接口未通过质检或全军覆没，启动本地大随机池兜底！")
    # ==================== 终极本地大随机池（全部为标准4句或8句全诗） ====================
    fallback_pool = [
        {"title": "黄鹤楼", "author": "崔颢", "dynasty": "唐", "sentences": ["昔人已乘黄鹤去，此地空余黄鹤楼。", "黄鹤一去不复返，白云千载空悠悠。", "晴川历历汉阳树，芳草萋萋鹦鹉洲。", "日暮乡关何处是？烟波江上使人愁。"]},
        {"title": "锦瑟", "author": "李商隐", "dynasty": "唐", "sentences": ["锦瑟无端五十弦，一弦一柱思华年。", "庄生晓梦迷蝴蝶，望帝春心托杜鹃。", "沧海月明珠有泪，蓝田日暖玉生烟。", "此情可待成追忆？只是当时已惘然。"]},
        {"title": "无题·相见时难别亦难", "author": "李商隐", "dynasty": "唐", "sentences": ["相见时难别亦难，东风无力百花残。", "春蚕到死丝方尽，蜡炬成灰泪始干。", "晓镜但愁云鬓改，夜吟应觉月光寒。", "蓬山此去无多路，青鸟殷勤为探看。"]},
        {"title": "望岳", "author": "杜甫", "dynasty": "唐", "sentences": ["岱宗夫如何？齐鲁青未了。", "造化钟神秀，阴阳割昏晓。", "荡胸生曾云，决眦入归鸟。", "会当凌绝顶，一览众山小。"]},
        {"title": "登金陵凤凰台", "author": "李白", "dynasty": "唐", "sentences": ["凤凰台上凤凰游，凤去台空江自流。", "吴宫花草埋幽径，晋代衣冠成古丘。", "三山半落青天外，二水中分白鹭洲。", "总为浮云能蔽日，长安不见使人愁。"]},
        {"title": "送杜少府之任蜀州", "author": "王勃", "dynasty": "唐", "sentences": ["城阙辅三秦，风烟望五津。", "与君离别意，同是宦游人。", "海内存知己，天涯若比邻。", "无为在歧路，儿女共沾巾。"]}
    ]
    return random.choice(fallback_pool)

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
    print("🤖 终极质检赛马版古诗推送 Bot 已启动...")
    send_poem_stream()  # 启动时热启动测试
    
    last_pushed_date = ""
    
    while True:
        tz_offset = 8 * 3600
        current_bj_time = datetime.fromtimestamp(time.time() + tz_offset)
        
        current_date = current_bj_time.strftime("%Y-%m-%d")
        current_hour = current_bj_time.strftime("%H:%M")
        
        if current_hour == "08:00" and last_pushed_date != current_date:
            print(f"⏰ 到达目标时间 08:00，开始并发抓取推送...")
            send_poem_stream()
            last_pushed_date = current_date
            
        time.sleep(30)
