# 📜 Telegram 每日古诗常驻推送 Bot

一个基于 Python 开发、部署于 Railway.app 的轻量级 Telegram 机器人。每天早上 08:00（北京时间），机器人会以**高能瀑布流（逐句连发）**的形式，为你推送一首完整的唐诗宋词，开启诗意的一天。

## ✨ 特性

- **完整诗词推送**：拒绝零碎的残句，采用高质量 API 确保推送题目、作者及完整的诗句。
- **级联瀑布流体验**：机器人会先发报幕（歌名与作者），随后每隔 2 秒**整行整行**地发送诗句，手机通知连击，仪式感拉满。
- **硬锁北京时区**：代码内部自动计算 GMT+8 时区偏移，不受海外服务器系统时区影响，准时准点。
- **Railway 亲和**：专门配置了后台 `worker` 后台常驻声明，无需暴露无用的 HTTP 端口，完美适配 Railway 挂机环境。

## 🛠️ 部署前准备

在部署之前，你需要准备好以下两个敏感凭证：

1. **TELEGRAM BOT TOKEN**：在 Telegram 中联系 [@BotFather](https://t.me/BotFather)，创建一个新机器人并获取 `API Token`。
2. **CHAT ID**：你想让机器人把古诗发给谁（可以是个人私聊，也可以是群组）。向你的机器人随便发一条消息，然后访问 `https://api.telegram.org/bot<你的TOKEN>/getUpdates`，在返回的 JSON 中找到 `"chat":{"id": XXXXXX}`，这一串数字就是你的 `CHAT_ID`。

## 📦 本地文件结构

你的项目目录应该包含以下三个核心文件：

```text
├── main.py          # 机器人核心 Python 脚本
├── requirements.txt # 依赖配置文件（仅需 requests）
└── Procfile         # 告诉 Railway 启动常驻 worker 的命令
```

### `requirements.txt` 内容：
```text
requests==2.32.3
```

### `Procfile` 内容：
```text
worker: python main.py
```

## 🚀 部署到 Railway.app

1. 将代码（`main.py`、`requirements.txt`、`Procfile`）提交并推送到你的 **GitHub 私有仓库**。
2. 登录 [Railway.app](https://railway.app/)，点击 **+ New Project**。
3. 选择 **Deploy from GitHub repo**，并授权导入你刚才创建的古诗 Bot 仓库。
4. **添加环境变量（最关键的一步）**：
   在 Railway 部署界面进入该项目，点击 **Variables** 标签页，添加以下两个环境变量：
   - `BOT_TOKEN` : 填入你的 Telegram Bot Token
   - `CHAT_ID` : 填入你的 Telegram Chat ID
5. 保存变量后，Railway 会自动触发重新部署（Redeploy）。

## 🧪 如何测试

- **云端热启动测试**：为了方便测试，代码中设计了“启动即触发”机制。每当你向 GitHub 提交代码或者 Railway 重新启动服务时，机器人会**立刻**向你的 Telegram 推送一首完整的古诗。如果你收到连发弹窗，说明配置完全成功！
- **定时验证**：测试通过后，保持 Railway 状态为 `Active`，它就会每天在北京时间早上 `08:00` 准时为你“轰炸”推送古诗。

## 📝 许可证

[MIT License](LICENSE)
```
