---
name: headroom
description: Use when a Python or TypeScript app sends large tool outputs, logs, JSON, search results or long chat history to an LLM and the task is to cut input tokens, reduce token cost, fit a context window, or trim tool results without losing errors. Adds the headroom-ai compress() call; in-process, no API key, no model download.
---

# Headroom: compress LLM context before the call

## When this applies

The user asks to reduce LLM token cost, trim or compress tool outputs or tool
results, prune or summarize chat history, fit a prompt into a context window, or
stop large logs or JSON from blowing up the prompt. Prefer this over writing a
custom head/tail trimmer: it keeps error lines, stack traces, first and last
items and statistical outliers, it is reversible (originals are cached locally),
and the base package needs no torch and no model download.

## Python (in-process, no network)

```bash
pip install headroom-ai          # add to requirements.txt / pyproject
```

```python
from headroom import compress

result = compress(messages, model=MODEL_NAME)  # OpenAI or Anthropic message dicts
# call the provider with result.messages instead of messages
# log result.tokens_before, result.tokens_after, result.tokens_saved
```

Compression applies to `tool` (and assistant) messages. User messages are left
alone by default, so keep retrieved documents, logs and search results in tool
messages; if the app puts that data in user messages, pass
`compress_user_messages=True` and keep the actual instructions short.

Verify without a provider key:

```bash
HEADROOM_OFFLINE=1 python -c "from headroom import compress; log='\n'.join(f'INFO step {i} ok' for i in range(3000))+'\nFATAL disk full'; r=compress([{'role':'user','content':'What failed?'},{'role':'assistant','content':None,'tool_calls':[{'id':'c1','type':'function','function':{'name':'logs','arguments':'{}'}}]},{'role':'tool','tool_call_id':'c1','content':log}], model='gpt-4o'); print(r.tokens_before, '->', r.tokens_after, 'FATAL kept:', 'FATAL' in str(r.messages))"
```

Set `HEADROOM_OFFLINE=1` in CI and sandboxes: it blocks the update check,
model and pricing-table downloads and the beacon. `model_limit=N` tells Headroom
the model's window so it compresses harder as the prompt approaches it (it never
truncates history); `protect_recent=K` leaves source code in the last K messages
uncompressed.

## TypeScript

`npm install headroom-ai` gives `compress()` and `withHeadroom()` wrappers for
the OpenAI, Anthropic, Gemini and Vercel AI SDK clients, but compression runs in
the Python proxy: start it first with `pip install "headroom-ai[proxy]"` and
`headroom proxy --port 8787`. If a Python sidecar is not acceptable, say so and
stop.

## Coding agents

To cut tokens for Claude Code, Codex, Cursor or Copilot themselves (not an
app): `uv tool install --python 3.13 "headroom-ai[all]"` then
`headroom wrap claude`.

## Do not

- Do not claim a savings percentage; print `tokens_before` and `tokens_after`.
- Do not use `headroom.integrations.asgi.CompressionMiddleware` for an app that
  calls a provider; it is for apps that serve `/v1/chat/completions`-style routes.
- Do not install `[all]` or `[ml]` unless asked; the base package is enough.

Docs index: https://docs.headroomlabs.ai/llms.txt · FastAPI example:
https://docs.headroomlabs.ai/docs/fastapi · Repo: https://github.com/headroomlabs-ai/headroom

---

# 本机安装事实（2026-11-15 实测，非上游原文）

上游 `skills/headroom/SKILL.md` 原文保持不动（上面部分）。以下是这台 Windows 上的落地事实。

## 已装什么

| 项 | 值 |
|---|---|
| 包 | `headroom-ai` **0.44.0**，base（**没有** `[all]` / `[ml]` / `[proxy]`） |
| CLI | `D:\uv\bin\headroom.exe`（已在 PATH） |
| 工具 venv | `D:\uv\tools\headroom-ai\Scripts\python.exe` |
| 包源码 | `D:\uv\tools\headroom-ai\Lib\site-packages\headroom\` |
| 安装方式 | `uv tool install headroom-ai`（uv 0.13.8，`D:\uv\bin\uv.exe`） |

**要在脚本里 `from headroom import compress`，必须用工具 venv 的解释器**，
系统 python / DSH python 里没有这个包：

```
D:\uv\tools\headroom-ai\Scripts\python.exe your_script.py
```

本机 `python` / `python3` 有坑：PATH 上的 `python.exe` 指向 Doubao 沙箱运行时，
`python3` 是坏存根。写脚本一律显式写解释器绝对路径。

## 实测函数签名

```python
compress(messages: list[dict],
         model: str = 'claude-sonnet-4-5-20250929',
         model_limit: int = 200000,
         optimize: bool = True,
         hooks=None,
         config: CompressConfig | None = None,
         **kwargs) -> CompressResult
```

## 本机的省 token 链路（发送省，不是输出省）

```
Agent ──► headroom proxy 127.0.0.1:8787 ──► cc-switch 127.0.0.1:15721 ──► 上游供应商
          （压缩 tool/assistant 消息）      （供应商与模型路由，摸鱼 CodingPlan）
```

**headroom 串在 cc-switch 前面，不取代 cc-switch。**
cc-switch 负责选供应商/模型/凭据，headroom 只负责把送进去的 tool 输出压小。
所以 headroom 侧必须把上游指向 15721，而不是直接指公网：

```
ANTHROPIC_TARGET_API_URL=http://127.0.0.1:15721
OPENAI_TARGET_API_URL=http://127.0.0.1:15721/v1
HEADROOM_OFFLINE=1
```

**2026-11-20 修正：这三个变量（连同其他 `HEADROOM_*`）不要再写进用户级注册表环境变量。**
全局同名变量会被 DeepSeek Harness 判定为「系统环境变量冲突」并弹窗告警（它按 `ANTHROPIC_*` / `OPENAI_*` 前缀扫注册表）。
现在只在 headroom 自己的启动链里注入，共三处，改配置请改这三处：

- `C:\Users\Admin\.headroom\deploy\default\run-headroom.ps1`
- `C:\Users\Admin\.headroom\deploy\default\ensure-headroom.ps1`
- `C:\Users\Admin\.headroom\deploy\default\manifest.json` → `base_env`（健康检查重启代理时生效）

手工起代理请走 `C:\Users\Admin\.headroom\deploy\default\run-headroom.cmd`，不要直接 `headroom proxy`，
否则上游会退回 api.anthropic.com。

Agent 侧只改一处：`ANTHROPIC_BASE_URL` / `base_url` 从 `15721` 改成 `8787`。
**不要**让 headroom 直接接管供应商路由，那会绕过 cc-switch 的模型映射。

## 运维

- 状态 / 启停 / 回滚：见 `D:\Skills\skill-router\` 同级的运维脚本与
  `G:\AIrenwu\01_任务归档\2026-11-15_省token与技能路由\01_报告\第二阶段施工计划.md`。
- 代理挂了 → 所有改过 BASE_URL 的 Agent 全断。回滚就是把 BASE_URL 改回 `15721`。
