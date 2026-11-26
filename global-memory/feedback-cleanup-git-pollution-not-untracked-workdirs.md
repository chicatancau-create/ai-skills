# 清理 git 污染勿删白名单外真实未跟踪工作目录（2026-11-26 事故教训）

- ai-renwu（G:\AIrenwu）.gitignore 首行 `/*` 白名单只放行 脚本库/02_项目代码/本地AI使用手册 → 其它任务产出目录、根 AGENTS.md、.agent-teams 长期未跟踪。
- 污染判定只能用 `git diff --name-only <远端正确SHA>..<本地污染SHA>` 的 additions（被错误历史 TRACKED 的外来文件）；untracked/ignored 一律不是污染、不动。
- 修污染分支用 `reset --mixed <远端SHA>` 保工作树；勿 reset --hard 覆盖未提交真实改动；删除前备份/查副本；junction 查 LinkType 防删穿。
- 事故：2026-11-26 误用「磁盘 minus 跟踪树」删 59 项，混删真实未跟踪目录 10_视频广告/鸿蒙歌单数据/OpenRevo插件整理/disk_reports/.agent-teams/01_浠诲姟掓。(乱码副本)，无副本可恢复；根 AGENTS.md 已重建。ai-skills 污染副本 489MB 删除正确。
- 另发现：ai-renwu 本地 main 曾被 ai-skills 历史污染（本地 HEAD 不含远端正确 SHA），已 reset --mixed 到远端 + 外科式提交修复；两端 HEAD 重新对齐。
- 手册正文：G:\AIrenwu\本地AI使用手册\03-通用\04-工程规范与安全\规则-清理git污染勿删白名单外真实未跟踪工作目录.md