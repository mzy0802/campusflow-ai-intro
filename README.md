# 畅行长大

校园两轮车停车查询与出行推荐工作台，面向长安大学渭水校区。

打开导航后搜索并确认起点和终点。页面按预计耗时列出可行的出行方式。点击自行车或电动车，可以查看附近停车区、余位和停车后的步行路线。地图交通状态、停车余位和小白班次随演示时间变化。

## 本机运行

准备 Python 3.10 或更新版本以及 Node.js 22.12 或更新版本。建议使用 Python 3.12。

在项目根目录启动后端。

```text
python -m pip install -r backend/requirements.txt
python run_backend.py
```

另开终端启动前端。

```text
cd frontend
npm ci
npm run dev -- --port 5174
```

打开 [工作台](http://127.0.0.1:5174/)。后端检查地址为 [健康接口](http://127.0.0.1:8000/api/health)。

可用“鸿翔园6号公寓”至“明远教学楼A栋”体验地点搜索和路线规划。基本查询使用本地路网和演示数据。启动时会为新的本地数据库载入演示公交线路。

## 云端导航和语音配置

将 `.env.example` 复制为项目根目录下的 `.env`，填写对应的密钥和服务地址。

| 功能 | 配置模板中的模型 | 需要填写 |
| --- | --- | --- |
| AI 指路 | `qwen-flash` | `NAV_AI_API_KEY` 和 `NAV_AI_BASE_URL`。填写 OpenAI 兼容接口的基础地址。 |
| 语音转写 | `qwen-audio-3.1-asr-flash` | `NAV_ASR_API_KEY` 和 `NAV_ASR_BASE_URL`。填写支持该模型的 DashScope 地址，应用会传入校园地名热词。 |
| 图像识别 | `qwen3-vl-plus` | `DASHSCOPE_API_KEY` 和 `QWEN_VISION_BASE_URL`。 |

完整的云端配置由后端读取。教师需要体验云端功能时，可以在本机通过单独提供的 `.env` 启用。

## 数据和代码

- `frontend/src` 包含地图、地点搜索、候选卡片及交通演示。
- `backend/app` 包含地点解析、路线计算、停车推荐和公交时刻接口。
- `data` 包含 OpenStreetMap 校园空间数据、停车区和演示公交配置。底图使用时保留 OpenStreetMap 署名。
- `frontend/public/fonts` 包含字体及许可。依赖与版本见项目的 requirements 文件和 npm 锁文件。

预计耗时由道路、配置速度和演示交通状态计算。停车查询读取当前状态，停车占用按演示时间变化。
