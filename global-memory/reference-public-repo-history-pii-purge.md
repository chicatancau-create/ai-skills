# 公开仓历史 PII 清洗：filter-repo 镜像克隆法

2026-11-25 验证。公开仓历史里的手机号/邮箱要清干净，四步且不伤工作仓 WIP：

1. mirror 备份 `git clone --mirror <工作仓> <name>-pre.git`。
2. 工作镜像**从远端克隆** `git -c http.proxy=http://127.0.0.1:7890 clone --mirror <GitHubURL> <name>-work.git`。勿从工作仓克隆——工作仓的 refs/remotes/* 陈旧跟踪引用会被 mirror 继承，force-push --mirror 时引发 `cannot lock ref 'refs/heads/main': is at X but expected Y`。
3. `python -m git_filter_repo --replace-text <UTF8无BOM,字面量 旧==>新> --force`（在 work.git 内）。工具用 bundled python `C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe -m pip install git-filter-repo --proxy http://127.0.0.1:7890` 装；Scripts 不在 PATH，用 `python -m git_filter_repo` 而非 `git filter-repo`。验 `git grep -I -l '<PII>' $(git rev-list --all)` 命中 0。
4. `push --force --mirror` 两端（GitHub 挂 7890 重试，GitCode 直连）→ 同步工作仓：干净仓 `fetch origin`+`reset --hard origin/main`；有 WIP 仓 `reset --soft origin/main`（只移指针，未提交改动逐条保留，验 status --porcelain 前后一致）。

关键坑：`D:\Skills\skill-router\wire_guard.py --watch`（常驻 pythonw）技能文件变动后调 git_backup.py 自动 push，与历史重写 force-push 竞态（remote rejected）。重写后必须立刻把本地工作仓 reset 到重写 HEAD，否则守护把旧历史推回。filter-repo 会移除 origin 远端，本流程在独立 work.git 跑、用 URL 直推，工作仓远端不受影响。

本轮成果：fullstack-code 217 提交手机号/邮箱 17 处→0（daf076a→500d573），ai-skills 67 提交第三方邮箱→0（caae70e→0ec3aa3），两端 HEAD 一致，WIP 14 条保留。备份 G:\AIrenwu..\G:\数据备份\历史清洗备份_2026-11-25\。

## 2026-11-26 复洗（上一轮 replace 文件写坏成乱码后的补救，`verified`）

上一轮 replace 文件里目标串被按 GBK 写坏，导致完整第三方邮箱被替成一串乱码占位符（UTF-8 汉字被按 GBK 复读后的产物），但**裸用户名没进 replace 列表，仍留在历史 blob 里**；`git log --all -S '<裸用户名>'` 立刻能查到旧提交。教训两条：

1. **replace 必须同时列「完整邮箱」和「裸用户名」（以及显示名），且长串在前**。filter-repo 的 `apply_replace_text` 是按文件行序依次 `str.replace(literal, new)` 做字面量替换，顺序错了会只替掉邮箱、留下裸用户名，或把邮箱替成 `xxx@gmail.com==>...` 的残渣。
2. **验漏用 pickaxe 而不是 `log -p | grep`**：`git log --all -S '<串>' --oneline` 只要文件里出现过该串就命中，对"被替换成占位符"的提交也有效；这是上一轮漏检的直接手法。
3. **从 pristine 备份重做，不要在坏历史上二次 replace**。坏历史里已有乱码占位符，二次替换既清不掉乱码也会叠更多残渣；正确做法是 `clone --mirror` pristine → 原地 `--force` 跑 filter-repo → cherry-pick 回 post-purge 新提交。
4. **filter-repo 不能加 `--source`**：带 `--source <path>` 会打印新 SHA 但 refs/对象都不落盘（静默回滚）；必须 `cd` 进镜像目录原地跑。
5. **rewrite 后本地 `.git` 仍有不可达 PII 对象**：reset/fetch 只移 ref，旧对象留在 object db 里可达 30 天。收尾必须 `git reflog expire --expire=now --expire-unreachable=now --all` + `git gc --prune=now`，再跑对象级扫描（`git cat-file --batch-all-objects --batch`）确认 0。
6. **force-push 只清 ref 层，清不掉对象层**：GitHub/GitCode 都保留不可达对象，按 SHA 仍可 `GET /git/blobs/<sha>` 或 `GET /contents/<path>?ref=<old-sha>` 读到旧内容。要做到"零残留"必须找平台 Support 强制 GC/回收不可达对象——仅靠 git 操作做不到，这一条必须在对用户报告里明说。

关联手册：G:\AIrenwu\本地AI使用手册\03-通用\03-调试与验证\规则-公开仓历史PII清洗用filter-repo镜像克隆法.md（**注：该文件当前不存在，属断链**）。