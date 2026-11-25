# 两端仓库对齐写操作要点（2026-11-25 清理对齐实测）

> 候选经验，须用当前事实复核。读清单前篇见 reference-gitcode-atomgit-merged-scan.md。
> 完整手册：G:\AIrenwu\本地AI使用手册\03-通用\03-调试与验证\规则-两端仓库对齐写操作GitCode增删改UTF8字节body与gh改公开删仓scope.md

## 背景
用户要求 GitHub(chicatancau-create) 与 GitCode(zhoumoyukuai) 两端仓库完全对齐 + 全部公开 + 删 4 旧仓 + QoderToolkit 技能迁 D:\Skills + 学习资料库/CodeWeave 更新双推。

## 可复用事实
- GitCode 写 API（代理 7890 + private-token 头）：建仓 POST /api/v5/user/repos；改简介+可见性 PATCH /api/v5/repos/zhoumoyukuai/{repo}（200）；删仓 DELETE 同端点（204）。body 必须 UTF8.GetBytes + ContentType charset=utf-8，传字符串中文永久变 ?；读回 RawContentStream.ToArray()→UTF8.GetString（默认 latin1 显示 mojibake 但存储正确）。
- gh 改公开必须加 --accept-visibility-change-consequences；gh 删仓需 delete_repo scope，默认 gho_ 令牌（gist/read:org/repo/workflow）没有，非交互无法自授 → 需 gh auth refresh -h github.com -s delete_repo 浏览器授权或 web UI 删（属缺权限，写进总结）。
- gh repo list --jq 在 PS 里被拆参报 accepts at most 1 arg → 改 --json + ConvertFrom-Json。
- GitHub git clone/push 直连不稳（curl 56/18、Recv failure Connection was reset）→ git -c http.proxy=http://127.0.0.1:7890 -c http.postBuffer=524288000；ls-remote 直连与代理均通；GitCode git 直连正常。
- 多分支仓对齐验默认分支 HEAD（ls-remote --symref HEAD），不是已推的 feature 分支；merge-base --is-ancestor 判快进。CodeWeave 默认分支 main 曾 GitHub 落后 GitCode 70 提交，push origin main 快进对齐。
- PS 5.1 Out-File -Encoding utf8 写 BOM 污染 commit message → UTF8Encoding($false)。仓库级 git 身份缺失传 -c user.name/email 不改全局。ai-skills 自动备份守护 git_backup.py MIN_INTERVAL=600 每 10 分钟 git add -A 抢提交，push 前 amend 未推送本地提交修正。

## 本轮结果（历史快照）
- 7 保留仓两端全公开 + HEAD 全对齐：ai-skills/ai-renwu/cc-hud/CodeWeave/fullstack-code/fullstack-study-library/folia-major(fork)。
- GitCode qoder-toolkit 已删；GitHub 4 待删仓（mediacrawler-intel-workbench/qoder-toolkit/super-productivity/learning-blog-demo）已 mirror 备份到 G:\数据备份\仓库删除备份_2026-11-25\，因缺 delete_repo 未删，待用户授权。
- QoderToolkit 9 技能字节级迁 D:\Skills（web-kimi 许可泄露排除留原库），router sync 53 技能；web-taste 验 MIT 成立入库。
- 隐私：fullstack-code register.vue + ai-skills gemini 多配置文件当前 HEAD 已脱敏；历史残留（演示手机号/第三方邮箱，非密钥）未 rewrite，flag 用户可选 history purge。