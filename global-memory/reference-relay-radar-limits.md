---
name: reference-relay-radar-limits
description: relay-radar(AetherCore-Dev) 未发布到 npm，只能克隆后跑 packages/cli/bin/relay-radar.mjs；它的判定有三个硬限制——LLMmap 只有 non-claude-unknown 桶、远端 profiles.json 已 404、未知 gpt 别名会被 resolveProfileKey 映射到 gpt-5.4 基线
metadata:
  type: reference
---

用 `npx relay-radar` 一定失败：npm 上那个名字是占位空壳（唯一版本 `0.0.1-security`，描述
`Reserved name placeholder. No functionality.`，无 `bin`，维护者不是该 GitHub 组织）。仓库根
`package.json` 是 `"private": true` 的 workspaces 单体且**根上没有 bin**，所以
`npx github:owner/repo` 同样报 `could not determine executable to run`。
可用跑法（2026-10-06 实测）：克隆后 `node packages/cli/bin/relay-radar.mjs <命令>`，
CLI 零外部依赖，**不需要 npm install**（因此不触发第三方安装脚本）。Key 用配置里的
`${ENV_VAR}` 引用（`config.mjs` 的 `resolveApiKey` 支持 `${VAR}`/`$VAR`），不落盘。

**读它的结论前必须知道的三个限制**：

1. `verifier/llmmap/classifier.mjs` 的**唯一非 Claude 标签是 `non-claude-unknown`** —— 分类宇宙只有
   Claude 家族。任何 GPT/Gemini 端点都会掉进这个默认桶，于是 `verify` 报
   `❌ fake … 综合置信度93%`。**这不是欺诈证据，是"我认不出这是哪个 Claude"**。
2. `verifier/behavioral/profile-loader.mjs` 的远端基线
   `https://AetherCore-Dev.github.io/relay-radar/data/profiles.json` **返回 404**（GitHub 404 页），
   所以 `monitor` 输出里的「画像来源: 内置默认」= 用的是 `profiles.mjs` 里注释为
   *hardcoded estimates* 的估计值，不是实测分布。
3. `monitor.mjs:279 resolveProfileKey()` 是子串匹配：`gpt-6-astra` 只含 `gpt` → 落到 **`gpt-5.4`**
   基线，于是最终结果里「声称模型」显示成 `gpt-5.4`、「匹配声称: ❌ 否」是**它自己换错了参照物**，
   不是中转站说谎。别名里含 `opus`/`sonnet`/`haiku` 才会对上家族基线。

**How to apply:** 判"中转站有没有偷换模型"时，只把 `monitor` 的**模型距离表相对排序**当信号
（例：gpt 系 0.41–0.8 vs claude 系 1.54–2.12 ⇒ 确实不是 Claude），别引用它的 `fake`/`匹配声称` 字样；
置信度低于 ~60% 或显示「数据不足以判断」时按未证实处理。它只发 `/v1/messages` 和
`/v1/chat/completions`，**没有 `/v1/responses`**，所以 Codex 的 responses 线路测的是同站的另一条通道。

Related: [[reference-codex-desktop-and-ccswitch]], [[reference-git-push-needs-local-proxy]], [[feedback-rigor-audit]]
