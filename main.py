import os
from datetime import datetime
import time
import requests
import random

# 从 Railway 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==================== 终极本地 50 首词库 ====================
POEM_POOL = [
    {"title": "黄鹤楼", "author": "崔颢", "dynasty": "唐", "sentences": ["昔人已乘黄鹤去，此地空余黄鹤楼。", "黄鹤一去不复返，白云千载空悠悠。", "晴川历历汉阳树，芳草萋萋鹦鹉洲。", "日暮乡关何处是？烟波江上使人愁。"]},
    {"title": "锦瑟", "author": "李商隐", "dynasty": "唐", "sentences": ["锦瑟无端五十弦，一弦一柱思华年。", "庄生晓梦迷蝴蝶，望帝春心托杜鹃。", "沧海月明珠有泪，蓝田日暖玉生烟。", "此情可待成追忆？只是当时已惘然。"]},
    {"title": "无题·相见时难别亦难", "author": "李商隐", "dynasty": "唐", "sentences": ["相见时难别亦难，东风无力百花残。", "春蚕到死丝方尽，蜡炬成灰泪始干。", "晓镜但愁云鬓改，夜吟应觉月光寒。", "蓬山此去无多路，青鸟殷勤为探看。"]},
    {"title": "望岳", "author": "杜甫", "dynasty": "唐", "sentences": ["岱宗夫如何？齐鲁青未了。", "造化钟神秀，阴阳割昏晓。", "荡胸生曾云，决眦入归鸟。", "会当凌绝顶，一览众山小。"]},
    {"title": "登金陵凤凰台", "author": "李白", "dynasty": "唐", "sentences": ["凤凰台上凤凰游，凤去台空江自流。", "吴宫花草埋幽径，晋代衣冠成古丘。", "三山半落青天外，二水中分白鹭洲。", "总为浮云能蔽日，长安不见使人愁。"]},
    {"title": "送杜少府之任蜀州", "author": "王勃", "dynasty": "唐", "sentences": ["城阙辅三秦，风烟望五津。", "与君离别意，同是宦游人。", "海内存知己，天涯若比邻。", "无为在歧路，儿女共沾巾。"]},
    {"title": "登高", "author": "杜甫", "dynasty": "唐", "sentences": ["风急天高猿啸哀，渚清沙白鸟飞回。", "无边落木萧萧下，不尽长江滚滚来。", "万里悲秋常作客，百年多病独登台。", "艰难苦恨繁霜鬓，潦倒新停浊酒杯。"]},
    {"title": "蜀相", "author": "杜甫", "dynasty": "唐", "sentences": ["丞相祠堂何处寻？锦官城外柏森森。", "映阶碧草自春色，隔叶黄鹂空好音。", "三顾频烦天下计，两朝开济老臣心。", "出师未捷身先死，长使英雄泪满襟。"]},
    {"title": "客至", "author": "杜甫", "dynasty": "唐", "sentences": ["舍南舍北皆春水，但见群鸥日日来。", "花径不曾缘客扫，蓬门今始为君开。", "盘飧市远无兼味，樽酒家贫只旧醅。", "肯与邻翁相对饮，隔篱呼取尽余杯。"]},
    {"title": "山居秋暝", "author": "王维", "dynasty": "唐", "sentences": ["空山新雨后，天气晚来秋。", "明月松间照，清泉石上流。", "竹喧归浣女，莲动下渔舟。", "随意春芳歇，王孙自可留。"]},
    {"title": "使至塞上", "author": "王维", "dynasty": "唐", "sentences": ["单车欲问边，属国过居延。", "征蓬出汉塞，归雁入胡天。", "大漠孤烟直，长河落日圆。", "萧关逢候骑，都护在燕然。"]},
    {"title": "酬乐天扬州初逢席上见赠", "author": "刘禹锡", "dynasty": "唐", "sentences": ["巴山楚水凄凉地，二十三年弃置身。", "怀旧空吟闻笛赋，到乡翻似烂柯人。", "沉舟侧畔千帆过，病树前头万木春。", "今日听君歌一曲，暂凭杯酒长精神。"]},
    {"title": "夜雨寄北", "author": "李商隐", "dynasty": "唐", "sentences": ["君问归期未有期，巴山夜雨涨秋池。", "何当共剪西窗烛，却话巴山夜雨时。"]},
    {"title": "清明", "author": "杜牧", "dynasty": "唐", "sentences": ["清明时节雨纷纷，路上行人欲断魂。", "借问酒家何处有？牧童遥指杏花村。"]},
    {"title": "山行", "author": "杜牧", "dynasty": "唐", "sentences": ["远上寒山石径斜，白云生处有人家。", "停车坐爱枫林晚，霜叶红于二月花。"]},
    {"title": "九月九日忆山东兄弟", "author": "王维", "dynasty": "唐", "sentences": ["独在异乡为异客，每逢佳节倍思亲。", "遥知兄弟登高处，遍插茱萸少一人。"]},
    {"title": "枫桥夜泊", "author": "张继", "dynasty": "唐", "sentences": ["月落乌啼霜满天，江枫渔火对愁眠。", "姑苏城外寒山寺，夜半钟声到客船。"]},
    {"title": "乌衣巷", "author": "刘禹锡", "dynasty": "唐", "sentences": ["朱雀桥边野草花，乌衣巷口夕阳斜。", "旧时王谢堂前燕，飞入寻常百姓家。"]},
    {"title": "江南逢李龟年", "author": "杜甫", "dynasty": "唐", "sentences": ["岐王宅里寻常见，崔九堂前几度闻。", "正是江南好风景，落花时节又逢君。"]},
    {"title": "赠汪伦", "author": "李白", "dynasty": "唐", "sentences": ["李白乘舟将欲行，忽闻岸上踏歌声。", "桃花潭水深千尺，不及汪伦送我情。"]},
    {"title": "早发白帝城", "author": "李白", "dynasty": "唐", "sentences": ["朝辞白帝彩云间，千里江陵一日还。", "两岸猿声啼不住，轻舟已过万重山. 。"]},
    {"title": "望庐山瀑布", "author": "李白", "dynasty": "唐", "sentences": ["日照香炉生紫烟，遥看瀑布挂前川。", "飞流直下三千尺，疑是银河落九天。"]},
    {"title": "望天门山", "author": "李白", "dynasty": "唐", "sentences": ["天门中断楚江开，碧水东流至此回。", "两岸青山相对出，孤帆一片日边来。"]},
    {"title": "黄鹤楼送孟浩然之广陵", "author": "李白", "dynasty": "唐", "sentences": ["故人西辞黄鹤楼，烟花三月下扬州。", "孤帆远影碧空尽，唯见长江天际流。"]},
    {"title": "题西林壁", "author": "苏轼", "dynasty": "宋", "sentences": ["横看成岭侧成峰，远近高低各不同。", "不识庐山真面目，只缘身在此山中。"]},
    {"title": "惠崇春江晚景", "author": "苏轼", "dynasty": "宋", "sentences": ["竹外桃花三两枝，春江水暖鸭先知。", "蒌蒿满地芦芽短，正是河豚欲上时。"]},
    {"title": "饮湖上初晴后雨", "author": "苏轼", "dynasty": "宋", "sentences": ["水光潋滟晴方好，山色空蒙雨亦奇。", "欲把西湖比西子，淡妆浓抹总相宜。"]},
    {"title": "晓出净慈寺送林子方", "author": "杨万里", "dynasty": "宋", "sentences": ["毕竟西湖六月中，风光不与四时同。", "接天莲叶无穷碧，映日荷花别样红。"]},
    {"title": "小池", "author": "杨万里", "dynasty": "宋", "sentences": ["泉眼无声惜细流，树阴照水爱晴柔。", "小荷才露尖尖角，早有蜻蜓立上头。"]},
    {"title": "春日", "author": "朱熹", "dynasty": "宋", "sentences": ["胜日寻芳泗水滨，无边光景一时新。", "等闲识得东风面，万紫千红总是春。"]},
    {"title": "泊船瓜洲", "author": "王安石", "dynasty": "宋", "sentences": ["京口瓜洲一水间，钟山只隔数重山。", "春风又绿江南岸，明月何时照我还。"]},
    {"title": "书湖阴先生壁", "author": "王安石", "dynasty": "宋", "sentences": ["茅檐长扫净无苔，花木成畦手自栽。", "一水护田将绿绕，两山排闼送青来。"]},
    {"title": "元日", "author": "王安石", "dynasty": "宋", "sentences": ["爆竹声中一岁除，春风送暖入屠苏。", "千门万户曈曈日，总把新桃换旧符。"]},
    {"title": "示儿", "author": "陆游", "dynasty": "宋", "sentences": ["死去元知万事空，但悲不见九州同。", "王师北定中原日，家祭无忘告乃翁。"]},
    {"title": "秋夜将晓出篱门迎凉有感", "author": "陆游", "dynasty": "宋", "sentences": ["三万里河东入海，五千仞岳上摩天。", "遗民泪尽胡尘里，南望王师又一年。"]},
    {"title": "过零丁洋", "author": "文天祥", "dynasty": "宋", "sentences": ["辛苦遭逢起一经，干戈寥落四周星。", "山河破碎风飘絮，身世浮沉雨打萍。", "惶恐滩头说惶恐，零丁洋里叹零丁。", "人生自古谁无死？留取丹心照汗青。"]},
    {"title": "钱塘湖春行", "author": "白居易", "dynasty": "唐", "sentences": ["孤山寺北贾亭西，水面初平云脚低。", "几处早莺争暖树，谁家新燕啄春泥。", "乱花渐欲迷人眼，浅草才能没马蹄。", "最爱湖东行不足，绿杨阴里白沙堤。"]},
    {"title": "赋得古原草送别", "author": "白居易", "dynasty": "唐", "sentences": ["离离原上草，一岁一枯荣。", "野火烧不尽，春风吹又生。", "远芳侵古道，晴翠接荒城。", "又送王孙去，萋萋满别情。"]},
    {"title": "从军行七首·其四", "author": "王昌龄", "dynasty": "唐", "sentences": ["青海长云暗雪山，孤城遥望玉门关。", "黄沙百战穿金甲，不破楼兰终不还。"]},
    {"title": "出塞二首·其一", "author": "王昌龄", "dynasty": "唐", "sentences": ["秦时明月汉时关，万里长征人未还。", "单使龙城飞将在，不教胡马度阴山。"]},
    {"title": "芙蓉楼送辛渐", "author": "王昌龄", "dynasty": "唐", "sentences": ["寒雨连江夜入吴，平明送客楚山孤。", "洛阳亲友如相问，一片冰心在玉壶。"]},
    {"title": "鹿柴", "author": "王维", "dynasty": "唐", "sentences": ["空山不见人，但闻人语响。", "返景入深林，复照青苔上。"]},
    {"title": "竹里馆", "author": "王维", "dynasty": "唐", "sentences": ["独坐幽篁里，弹琴复长啸。", "深林人不知，明月来相照。"]},
    {"title": "静夜思", "author": "李白", "dynasty": "唐", "sentences": ["床前明月光，疑是地上霜。", "举头望明月，低头思故乡。"]},
    {"title": "江雪", "author": "柳宗元", "dynasty": "唐", "sentences": ["千山鸟飞绝，万径人踪灭。", "孤舟蓑笠翁，独钓寒江雪。"]}
]

def get_complete_poem():
    """主接口切换为开源优秀的 chinese-poetry-api，并叠加质检与防撞机制"""
    local_titles = {p["title"] for p in POEM_POOL}
    
    try:
        # 使用该开源项目的随机诗词分发端点（这里以最经典的唐诗为例，也可以换成宋诗/诗经等）
        url = "https://chinese-poetry-api.vercel.app/api/poetry/random?type=tang"
        resp = requests.get(url, timeout=6)
        
        if resp.status_code == 200:
            data = resp.json()
            # 该 API 返回的结构一般包含: title, author, paragraphs 等
            title = data.get("title", "无题").strip()
            author = data.get("author", "佚名").strip()
            paragraphs = data.get("paragraphs", [])
            
            # 清洗并过滤无效断行
            sentences = [s.strip() for s in paragraphs if s.strip()]
            
            # 🛡️ 核心测试质检：
            # 1. 必须是结构完整的全诗（句子数 >= 4）
            # 2. 且不能和本地 50 首主打词库发生撞车
            if len(sentences) >= 4 and title not in local_titles:
                print(f"✨ 新接口测试完美通关！成功捕获全新古诗：《{title}》")
                return {
                    "title": title,
                    "author": author,
                    "dynasty": "唐", # 优先抽取的唐诗库
                    "sentences": sentences
                }
            elif title in local_titles:
                print(f"🛑 拦截：新接口返回了词库中已有的名篇《{title}》，放弃使用以保证去重新鲜度。")
            else:
                print(f"⚠️ 拦截：新接口返回的诗句长短不合规（共 {len(sentences)} 句）。")
                
    except Exception as e:
        print(f"❌ chinese-poetry-api 请求或解析异常: {e}。不要慌，准备启动本地大词库摇号。")

    # 任何一步拦截或失败，即刻无缝启动本地 50 首词库摇号
    print("🎲 外部接口未能提供符合标准的新诗，正在从本地大词库随机抽签...")
    return random.choice(POEM_POOL)

def send_telegram_msg(text):
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
    
    intro_msg = f"📜 **《{poem['title']}》**\n— [{poem['dynasty']}] {poem['author']}"
    send_telegram_msg(intro_msg)
    time.sleep(2.0)
    
    for sentence in poem['sentences']:
        print(f"正在推送: {sentence}")
        send_telegram_msg(sentence)
        time.sleep(2.0)
        
    print(f"✅ 瀑布流推送完成")

if __name__ == "__main__":
    print("🤖 chinese-poetry-api 核心驱动版 Bot 已启动...")
    send_poem_stream()  # 热启动测试
    
    last_pushed_date = ""
    while True:
        tz_offset = 8 * 3600
        current_bj_time = datetime.fromtimestamp(time.time() + tz_offset)
        current_date = current_bj_time.strftime("%Y-%m-%d")
        current_hour = current_bj_time.strftime("%H:%M")
        
        if current_hour == "08:00" and last_pushed_date != current_date:
            send_poem_stream()
            last_pushed_date = current_date
            
        time.sleep(30)
