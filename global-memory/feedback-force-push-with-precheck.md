---
name: feedback-force-push-with-precheck
description: 用户明示「本地为最终版本、可以强推」时不要再次反问，但强推前必须先体检本地与远端差异：干净就直接推，发现较大差异或明显错误则停下交给用户核对
metadata:
  type: feedback
---

用户授权强推时，正确流程是**先体检、再决定**，而不是一上来就推、也不是每次都回头求确认：

1. 体检（只读）：`git fetch` 相关远端 → 比 SHA 与内容 → `git rev-list --left-right --count <remote>/<branch>...<branch>`、`git diff --stat <本地> <远端>`、必要时 `git ls-remote --heads` 看分支集合。
2. **没发现异常** → 直接强推，不再追问。
3. **发现较大差异或明显错误**（远端有本地没有的实际内容改动、两边树不一致、疑似别人的工作会被抹掉、分支缺失/多余得出乎意料）→ 停手，把具体差异列出来交用户核对，由他拍板。

**Why:** 用户 2026-11-04 明确说过「我并不是要你每次问我」——他给的是条件式授权：本地确认为最终版本时就推，但强推不可逆，他要一道自动的差异体检兜底，避免误吞另一台机器或网页端的提交。

**How to apply:** 适用于所有远端与所有分支。体检用只读命令，别用 `git push --dry-run` 判断认证可用性（失败会删 GCM 凭据）。推完用 `git ls-remote` 回读实际远端 SHA 作为成功证据，不凭本地 tracking ref 宣称已同步。仓库侧的两端镜像要求见 [[feedback-push-both-remotes]]。相关：[[feedback-never-git-add-dirs-in-codeweave]]、[[reference-git-credential-manager-windows]]。
