---
name: reference-windows-archive-tools
description: 本机解压/打包能力边界：只有 WinRAR 7.22（D:\RAR），无 7-Zip；git-bash 是 GNU tar，读不了 RAR5；GNU tar 的 -f 遇到 C:\ 路径要加 --force-local。
metadata:
  type: reference
---

要解 `.rar`（含 RAR5）时，本机唯一可用的是 **WinRAR 7.22 64 位，装在 `D:\RAR`**，命令行 `"/d/RAR/UnRAR.exe" x -y -o+ <file.rar> <outdir>/`（不存在时退回 `Rar.exe x -y`），退出码 0 即解出。

**Why:** 2026-11-01 为解课程服务端包摸过一遍：机器上**没有** 7-Zip / Bandizip / PeaZip；git-bash 里的 `tar --version` 是 **GNU tar 1.35**，对 RAR5 只报 `This does not look like a tar archive`；PowerShell `Expand-Archive` 不认 rar；Python `rarfile` 也需要 unrar 后端。

**从网络下载的 `.rar` 可能不是压缩包**：2026-11-01 学习通一个 2,248 字节的 `xxx.rar` 头 16 字节是 `<!DOCTYPE html>`——是 403 错误页。先看魔数（真 RAR5 `Rar!\x1a\x07\x01\x00`）与大小，别急着判材料缺失。列目录三个坑：**UnRAR 7.22 不支持 `-ba`**；**`l -inul` 会把 stdout 吞空**；输出是 **GBK**，用 python 按行正则解析。

**校验下载完整性比字节数**，别信课件给的 `crc`（那常是包内校验值，不是容器哈希）。

**GNU tar 的 Windows 路径坑（2026-11-08）**：`tar -czf "C:\Users\...\x.tgz" ...` 会报
`Cannot connect to C: resolve failed`——GNU tar 把冒号当成 `host:path` 远端语法。加 `--force-local`：
`tar --force-local -czf "$LOCALAPPDATA/Temp/x.tgz" ...`。git-bash 里用 `C:/...` 或 `/c/...` 也建议一并加，避免同类误判。

Related: [[reference-large-file-download-on-this-box]], [[reference-windows-python-encoding]]
