# 规则：AI 模型统一存放并使用 D:\Models

- 来源：用户 2026-11-22 原话（m01482）：「D:\Models把所有的模型全部放进我发给你的这个文件夹当中，这个文件夹是我专门用于放模型的地方。以后所有的模型都放里面，用模型也从里面用」。
- 规则：一切 AI 模型权重（vosk / faster-whisper / gguf / onnx 等）**只放 D:\Models、只从 D:\Models 加载**；不得散落在任务目录、工具目录或 C 盘缓存。模型安装包/zip 归档放 `D:\Models\_archives\`。
- 现状清单（2026-11-22 迁入后）：`faster-whisper-large-v3\`（model.bin 3.09GB）、`vosk-model-cn-0.22\`（1.26GB 大模型）、`vosk-model-small-cn-0.22\`（42MB）、用户自有 `Ternary-Bonsai-2-27B-gguf\`、`qwen2.5-0.5b-instruct-q4_k_m.gguf`、`_archives\`（3 个 zip；其中 vosk-model-cn-0.22.zip 383MB 是直连失败的不完整下载，可删）。
- 已落地：`G:\AIrenwu\01_任务归档\2026-11-20_平静vlog剪辑\03_工具脚本\asr_to_srt.py` 默认 `VOSK_MODEL=D:\Models\vosk-model-small-cn-0.22`；`fw_transcribe.py` 的 `MODEL=D:\Models\faster-whisper-large-v3`；迁移后两脚本加载验证通过（vosk 10 词 / whisper 整句正确）。
- 操作提示：D 盘内迁移用 Move-Item（同卷瞬时改名，不复制）；迁完 grep 全库旧路径改引用；新下载模型直接落 D:\Models，别再进 D:\AI-Tool-State。
- 关联：手册 `03-通用/04-工程规范与安全/规则-AI模型统一存放D盘Models目录.md`；全局记忆「软件只装 D 盘」条。