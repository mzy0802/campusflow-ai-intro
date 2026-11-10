# 畅行长大

校园两轮车停车查询与出行推荐工作台，面向长安大学渭水校区。

打开导航后搜索并确认起点和终点。页面按预计耗时列出可行的出行方式。点击自行车或电动车，可以查看附近停车区、余位和停车后的步行路线。地图交通状态、停车余位和小白班次随演示时间变化。

## 下载项目

准备 Python 3.10 或更新版本以及 Node.js 22.12 或更新版本。建议使用 Python 3.12。可以在 GitHub 点击 **Code → Download ZIP** 后解压，也可以使用 Git 克隆。

```sh
git clone https://github.com/mzy0802/campusflow-ai-intro.git
cd campusflow-ai-intro
```

项目根目录是包含 `run_backend.py` 和 `.env.example` 的那一层。

## 配置畅课里收到的 API

如果收到的是已填好的 `.env` 文件，将它放在项目根目录，文件名保持为 `.env`。

如果收到的是 **API 密钥和对应的接口基础地址**，将 `.env.example` 复制为 `.env`，用文本编辑器填写。以下是使用同一百炼工作空间体验云端指路和语音转写的示例。请把尖括号里的内容换成畅课消息里的值。

```dotenv
NAV_AI_MODEL=qwen-flash
NAV_AI_API_KEY=<API 密钥>
NAV_AI_BASE_URL=<OpenAI 兼容接口基础地址>

NAV_ASR_MODEL=qwen-audio-3.1-asr-flash
NAV_ASR_API_KEY=<API 密钥>
NAV_ASR_BASE_URL=<对应的百炼接口基础地址>
```

如果畅课消息给的是同一工作空间的兼容接口基础地址，以上两个 `BASE_URL` 可以填同一个值。语音模块会从这个地址取出域名，调用该工作空间的 DashScope 接口。基础地址通常以 `/compatible-mode/v1` 结尾。填写时去掉末尾的 `/chat/completions`。修改配置后，重启后端再刷新网页。

体验图像识别时，还需填写以下三项。畅课提供的密钥和地址若已开通视觉模型，可以填入同一组值。

```dotenv
QWEN_VISION_MODEL=qwen3-vl-plus
DASHSCOPE_API_KEY=<已开通视觉模型的 API 密钥>
QWEN_VISION_BASE_URL=<对应的 OpenAI 兼容接口基础地址>
```

没有 `.env` 时，仍可体验地图、路线规划、停车推荐和内置规则指路。

## 启动前后端

在项目根目录打开终端，执行与系统对应的命令。

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe run_backend.py
```

**macOS / Linux**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python run_backend.py
```

保持后端窗口运行。另开一个终端，从项目根目录启动前端。

```sh
cd frontend
npm ci
npm run dev -- --port 5174
```

在浏览器打开 [工作台](http://127.0.0.1:5174/)。[后端健康接口](http://127.0.0.1:8000/api/health) 返回 `"status":"ok"` 时，说明后端已启动。

### Mac 解压后从哪里开始

1. 在 Finder 中找到解压后的项目文件夹。打开「终端」，输入 `cd `（末尾留一个空格），把文件夹拖进终端，再按回车。运行 `ls -a`，确认能看到 `run_backend.py`、`backend` 和 `frontend`。
2. 如果从畅课收到了 `.env`，把它放在这一层。以点开头的文件在 Finder 里默认隐藏，可以按 **Command + Shift + .** 显示。也可以用 `ls -a` 确认文件名是 `.env`。先运行 `python3 --version` 和 `node --version`，确认所用版本满足上面的要求。
3. 在第一个终端执行上面的 macOS 后端命令，打开[后端健康接口](http://127.0.0.1:8000/api/health)确认返回 `"status":"ok"`。再开一个终端标签页，重新进入项目根目录，执行前端命令。浏览器打开前端终端打印的 **Local** 地址，通常是 `http://127.0.0.1:5174/`。

## 体验与检查

1. **路线规划**。选择起点“鸿翔园6号公寓”和终点“明远教学楼A栋”，点击“查找路线”。选中电动车或自行车后，可切换停车区并查看地图路线。
2. **云端 AI 指路**。点击“AI 指路”，输入“从鸿翔园6号公寓到明远教学楼A栋”。配置齐全时，后端可调用 `qwen-flash` 处理出行请求。未配置时，页面使用内置规则生成候选。
3. **云端语音转写**。在“AI 指路”中点击麦克风并允许访问，说完后再点一次停止。确认转写文本后点击发送。[语音配置接口](http://127.0.0.1:8000/api/navigation/asr) 中 `"ready":true` 表示后端已读取云端语音配置。
4. **图像识别**。配置视觉服务后，打开 [调试页](http://127.0.0.1:5174/debug)，点击“人车识别测试”，上传一张图片查看计数。[视觉配置接口](http://127.0.0.1:8000/api/vision/health) 可检查视觉配置与依赖状态。

如果工作台打不开，先确认两个终端都在运行。云端功能报错时，检查文件是否误存为 `.env.txt`，以及密钥、接口地址与模型权限是否属于同一工作空间。

## 数据和代码

- `frontend/src` 包含地图、地点搜索、候选卡片及交通演示。
- `backend/app` 包含地点解析、路线计算、停车推荐和公交时刻接口。
- `data` 包含 OpenStreetMap 校园空间数据、停车区和演示公交配置。底图使用时保留 OpenStreetMap 署名。
- `frontend/public/fonts` 包含字体及许可。依赖与版本见项目的 requirements 文件和 npm 锁文件。

预计耗时由道路、配置速度和演示交通状态计算。停车查询读取当前状态，停车占用按演示时间变化。
