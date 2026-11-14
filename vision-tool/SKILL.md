---
name: vision-tool
description: "本地视觉能力(看图/识别图片/分析截图)。当需要理解图片内容、识别图中文字、对比多张图片、分析截图时使用。连接本机牧羊人(Herdsman AI)部署的 Qwen3.5-9B 多模态模型, 纯标准库 Python 实现, 自动发现服务端点。"
---

# VisionTool - 本地视觉能力

让智能体获得"看图"能力, 连接本机牧羊人(Herdsman AI)运行的本地多模态模型。

## 使用方式

```
python D:\Skills\vision-tool\vision.py <图片路径> [问题]
```

- 一张图: `python D:\Skills\vision-tool\vision.py C:\photo.png "这张图里有什么?"`
- 多图对比: 依次传入多个图片路径, 最后接问题
- 也可用 `-p "问题"` 显式指定问题, `--lang en` 英文回答, `--lang zh` 中文(默认)
- 不传问题时, 默认"请详细描述这张图片的内容。"

## 关键行为

1. **自动发现**: 优先牧羊人网关 `127.0.0.1:8080`, 失败则动态查找 llama-server 监听端口。状态目录优先读取 `AI_SHARED_SKILLS_STATE_DIR`，未设置时使用用户本地应用数据目录；端点缓存于其下的 `vision-tool/vision.json`(服务重启端口变化后自动重新发现)
2. **无需配置**: 只要牧羊人(Herdsman AI)启动并加载了视觉模型, 直接可用; 若未启动则提示"未发现运行中的本地模型服务"
3. **输出**: stdout 为模型回答(UTF-8); 完整回答另存到状态目录的 `vision-tool/last_response.txt`
4. **大图**: >1568px 时若本机有 PIL 会自动缩放, 无 PIL 也正常工作
5. **Windows 控制台乱码**: 若中文乱码, 先设 UTF-8: `[Console]::OutputEncoding = [Text.Encoding]::UTF8; python ...`, 或直接读 `last_response.txt`

## 注意事项

- 仅标准库, 无任何第三方依赖, 任何有 Python 的机器可直接运行
- 生成回答需要时间(本地模型推理), 超时上限 600 秒, 大图较慢属正常
- 模型: Qwen3.5-9B-Q4_K_M(多模态, 由牧羊人 Herdsman AI 部署)
