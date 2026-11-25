# 公开仓历史 PII 清洗：filter-repo 镜像克隆法

2026-11-25 验证。公开仓历史里的手机号/邮箱要清干净，四步且不伤工作仓 WIP：

1. mirror 备份 `git clone --mirror <工作仓> <name>-pre.git`。
2. 工作镜像**从远端克隆** `git -c http.proxy=http://127.0.0.1:7890 clone --mirror <GitHubURL> <name>-work.git`。勿从工作仓克隆——工作仓的 refs/remotes/* 陈旧跟踪引用会被 mirror 继承，force-push --mirror 时引发 `cannot lock ref 'refs/heads/main': is at X but expected Y`。
3. `python -m git_filter_repo --replace-text <UTF8无BOM,字面量 旧==>新> --force`（在 work.git 内）。工具用 bundled python `C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe -m pip install git-filter-repo --proxy http://127.0.0.1:7890` 装；Scripts 不在 PATH，用 `python -m git_filter_repo` 而非 `git filter-repo`。验 `git grep -I -l '<PII>' $(git rev-list --all)` 命中 0。
4. `push --force --mirror` 两端（GitHub 挂 7890 重试，GitCode 直连）→ 同步工作仓：干净仓 `fetch origin`+`reset --hard origin/main`；有 WIP 仓 `reset --soft origin/main`（只移指针，未提交改动逐条保留，验 status --porcelain 前后一致）。

关键坑：`D:\Skills\skill-router\wire_guard.py --watch`（常驻 pythonw）技能文件变动后调 git_backup.py 自动 push，与历史重写 force-push 竞态（remote rejected）。重写后必须立刻把本地工作仓 reset 到重写 HEAD，否则守护把旧历史推回。filter-repo 会移除 origin 远端，本流程在独立 work.git 跑、用 URL 直推，工作仓远端不受影响。

本轮成果：fullstack-code 217 提交手机号/邮箱 17 处→0（daf076a→500d573），ai-skills 67 提交第三方邮箱→0（caae70e→0ec3aa3），两端 HEAD 一致，WIP 14 条保留。备份 G:\AIrenwu..\G:\数据备份\历史清洗备份_2026-11-25\。

关联手册：G:\AIrenwu\本地AI使用手册\03-通用\03-调试与验证\规则-公开仓历史PII清洗用filter-repo镜像克隆法.md。