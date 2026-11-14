#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VisionTool - 本地多模态视觉分析工具
连接牧羊人(Herdsman AI)部署的本地视觉模型(llama-server, OpenAI兼容API)

用法:
    python vision.py <图片路径> [图片路径2 ...] [问题]
    python vision.py C:\\photo.png "这张图里有什么?"
    python vision.py C:\\photo.png                    # 使用默认提示词
    python vision.py --endpoint http://127.0.0.1:8080 --model Qwen3.5_9b C:\\photo.png

特性:
    - 自动发现模型服务: 优先牧羊人网关(8080端口), 失败则动态查找 llama-server 监听端口
    - 端点与模型名缓存到 vision.json, 服务重启端口变化后自动重新发现
    - 纯标准库实现, 无需安装任何依赖
"""

import sys
import os
import io
import re
import json
import base64
import socket
import argparse
import subprocess
import urllib.request

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_ROOT = os.environ.get(
    "AI_SHARED_SKILLS_STATE_DIR",
    os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ai-shared-skills"),
)
STATE_DIR = os.path.join(STATE_ROOT, "vision-tool")
CONFIG_PATH = os.path.join(STATE_DIR, "vision.json")
LAST_RESPONSE_PATH = os.path.join(STATE_DIR, "last_response.txt")

DEFAULT_SYSTEM_PROMPT = "你是一个专业的图像分析助手。请用中文详细、准确地回答用户关于图片的问题，除非用户明确要求使用其他语言。"

GATEWAY_ENDPOINT = "http://127.0.0.1:8080"
GATEWAY_FALLBACK_PORTS = [64233]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def http_get_json(url, timeout=3):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_post_json(url, payload, timeout=300):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def probe_endpoint(endpoint):
    """返回 (模型列表) 或 None"""
    try:
        data = http_get_json(endpoint.rstrip("/") + "/v1/models", timeout=3)
    except Exception:
        return None
    models = []
    for m in (data.get("data") or data.get("models") or []):
        mid = m.get("id") or m.get("name") or ""
        if not mid or mid == "edge-tts":
            continue
        caps = set()
        if isinstance(m, dict):
            caps = set(m.get("capabilities") or [])
            meta = m.get("meta") or {}
            if meta.get("format") == "gguf":
                caps.add("multimodal")
        models.append({"id": mid, "capabilities": caps})
    return models if models else None


def find_llama_server_ports():
    """动态查找 llama-server 进程的监听端口"""
    ports = []
    try:
        pids = set()
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq llama-server.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10, shell=False)
        for line in out.stdout.splitlines():
            parts = [p.strip().strip('"') for p in line.split(",")]
            if len(parts) >= 2 and parts[0] == "llama-server.exe":
                try:
                    pids.add(int(parts[1]))
                except ValueError:
                    pass
        if not pids:
            return ports
        out = subprocess.run(["netstat", "-ano", "-p", "tcp"],
                             capture_output=True, text=True, timeout=15, shell=False)
        for line in out.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 5 and parts[0].upper() == "TCP" and parts[3] == "LISTENING":
                pid = parts[-1]
                if pid in pids:
                    local = parts[1]
                    port = local.rsplit(":", 1)[-1]
                    if port.isdigit():
                        ports.append(int(port))
    except Exception as exc:
        eprint("[vision] 查找 llama-server 端口失败: %s" % exc)
    return sorted(set(ports))


def load_cache():
    try:
        with io.open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(cache):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with io.open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        eprint("[vision] 缓存写入失败: %s" % exc)


def pick_model(models):
    """优先多模态模型"""
    for m in models:
        if "multimodal" in m["capabilities"]:
            return m
    return models[0]


def discover(use_cache=True):
    """按顺序尝试: 缓存 -> 牧羊人网关 -> llama-server 动态端口 -> 常见端口"""
    candidates = []

    if use_cache:
        cache = load_cache()
        ep = cache.get("endpoint")
        if ep:
            candidates.append(("cache", ep))

    candidates.append(("gateway", GATEWAY_ENDPOINT))

    for port in find_llama_server_ports():
        candidates.append(("llama-server", "http://127.0.0.1:%d" % port))

    for port in GATEWAY_FALLBACK_PORTS:
        candidates.append(("fallback", "http://127.0.0.1:%d" % port))

    for label, endpoint in candidates:
        models = probe_endpoint(endpoint)
        if models:
            return endpoint, pick_model(models)
    return None, None


def downscale_if_needed(path):
    """图片过大时用 PIL 缩小, 未安装 PIL 则原样返回"""
    try:
        from PIL import Image
    except ImportError:
        return path
    try:
        im = Image.open(path)
        w, h = im.size
        limit = 1568
        if max(w, h) <= limit:
            return path
        scale = limit / float(max(w, h))
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
        tmp = os.path.join(os.environ.get("TEMP", TOOL_DIR), "vision_resized_%d.png" % os.getpid())
        im.save(tmp, "PNG")
        eprint("[vision] 图片已缩放 %dx%d -> %dx%d" % (w, h, im.size[0], im.size[1]))
        return tmp
    except Exception:
        return path


def image_to_data_url(path):
    path = downscale_if_needed(path)
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


def build_messages(image_paths, question, lang):
    content = []
    if lang == "zh":
        content.append({"type": "text", "text": question or "请详细描述这张图片的内容。"})
    else:
        content.append({"type": "text", "text": question or "Please describe this image in detail."})
    for p in image_paths:
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(p)}})
    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT if lang == "zh" else
         "You are a professional image analysis assistant."},
        {"role": "user", "content": content},
    ]
    return messages


def call_model(endpoint, model_id, messages):
    url = endpoint.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": model_id,
        "messages": messages,
        "stream": False,
        "temperature": 0.2,
        "max_tokens": 4096,
    }
    data = http_post_json(url, payload, timeout=600)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError("模型返回格式异常: %s" % json.dumps(data, ensure_ascii=False)[:500])


def main():
    parser = argparse.ArgumentParser(
        description="VisionTool - 本地多模态视觉分析工具(连接牧羊人 Herdsman AI 本地模型)")
    parser.add_argument("images", nargs="*", help="图片文件路径(可多个)")
    parser.add_argument("question", nargs="?", default=None, help="关于图片的问题(可选)")
    parser.add_argument("-p", "--prompt", dest="question_opt", default=None, help="关于图片的问题(可选)")
    parser.add_argument("--endpoint", default=None, help="手动指定 API 端点, 如 http://127.0.0.1:8080")
    parser.add_argument("--model", default=None, help="手动指定模型名")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="回答语言, 默认中文")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存, 强制重新发现服务")
    parser.add_argument("--no-save", action="store_true", help="不保存 last_response.txt")
    args = parser.parse_args()

    if args.question is None and args.question_opt is not None:
        args.question = args.question_opt
    if not args.images:
        eprint("[vision] 错误: 请提供至少一张图片")
        sys.exit(2)
    if args.question is None and len(args.images) > 1:
        last = args.images[-1]
        if not os.path.isfile(last) and os.path.splitext(last)[1].lower() not in IMAGE_EXTENSIONS:
            args.question = args.images.pop()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    for p in args.images:
        if not os.path.isfile(p):
            eprint("[vision] 错误: 文件不存在: %s" % p)
            sys.exit(2)
        if os.path.splitext(p)[1].lower() not in IMAGE_EXTENSIONS:
            eprint("[vision] 警告: 非图片扩展名: %s" % p)

    endpoint, model_id = args.endpoint, args.model
    if not endpoint or not model_id:
        discovered_ep, discovered_model = discover(use_cache=not args.no_cache)
        if endpoint is None:
            endpoint = discovered_ep
        if model_id is None:
            model_id = discovered_model["id"] if discovered_model else None
        if endpoint and model_id:
            save_cache({"endpoint": endpoint, "model": model_id})

    if not endpoint or not model_id:
        eprint("[vision] 未发现运行中的本地模型服务。请先启动牧羊人(Herdsman AI)并加载视觉模型。")
        sys.exit(1)

    eprint("[vision] 端点: %s  模型: %s" % (endpoint, model_id))
    eprint("[vision] 正在分析 %d 张图片..." % len(args.images))

    messages = build_messages(args.images, args.question, args.lang)
    try:
        answer = call_model(endpoint, model_id, messages)
    except Exception as exc:
        if args.endpoint and args.model:
            eprint("[vision] 调用失败: %s" % exc)
            sys.exit(1)
        eprint("[vision] 端点 %s 调用失败(%s), 尝试重新发现服务..." % (endpoint, exc))
        endpoint, model_id = None, None
        discovered_ep, discovered_model = discover(use_cache=False)
        if discovered_ep and discovered_model:
            endpoint, model_id = discovered_ep, discovered_model["id"]
            save_cache({"endpoint": endpoint, "model": model_id})
            eprint("[vision] 已切换到端点: %s  模型: %s" % (endpoint, model_id))
            answer = call_model(endpoint, model_id, messages)
        else:
            eprint("[vision] 未发现可用的本地模型服务。")
            sys.exit(1)

    answer = (answer or "").strip()
    if not answer:
        eprint("[vision] 模型返回为空。")
        sys.exit(1)

    if not args.no_save:
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with io.open(LAST_RESPONSE_PATH, "w", encoding="utf-8") as f:
                f.write(answer)
        except Exception:
            pass

    sys.stdout.write(answer + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
