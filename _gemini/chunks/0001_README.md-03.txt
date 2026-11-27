| 目录 | 用途 |
| --- | --- |
| `codeweave-visual-rebuild-rerun` | CodeWeave 视觉重建复跑（60-cell 矩阵） |
| `headless-cdp-visual-acceptance` | 无头 CDP 视觉验收 |
| `install-github-skill-on-windows-qoder` | 在 Windows Qoder 上安装 GitHub 技能 |
| `localstorage-data-shape-seeding` | 按真实数据形状给 localStorage 播种 |
| `ppt-master` | PPT 母版/批量生成与归属校验（MIT，约 89 MB，字节不可改） |
| `qoder-toolkit` | Qoder 工具箱总入口（本机硬规则 + 路由） |
| `verify-app-security-claims` | 核实应用的安全声明是否属实 |
| `visual-tool-add-section` | 给可视化工具加新板块 |
| `web-taste` | 网页审美/品味评审与改造（MIT） |

## 五、原第二库 QoderToolkit：已并入本库

`D:\QoderToolkit` → `D:\_整理\04-AI工具包\QoderToolkit`（总联接，隔离「另一个 AI 还在搬 D:\_整理」的风险）**不再是独立技能源**：其 9 个技能已于 2026-11-25 字节级迁入本库 `D:\Skills\<同名目录>`，索引、路由一律指向本库。

- **为什么迁**：两个库并存时，同一个技能名会在 `skill-router` 索引里撞车，且改一处忘另一处。
- **唯一保留在原库的**：`web-kimi`（上游 `QvvvvvvQ/skills_leaks` 泄露内容，无使用许可，不得再分发），仍在 `D:\QoderToolkit\web-kimi`，**不进本库、不进 git 远端**。
- **`ppt-master` 特别约定**：目录内任何文件字节不可改动（完整性闸门 `scripts\attribution_guard.py`），迁移是纯复制，闸门在新位置实测通过。
- 原库仍是独立 git 仓库（GitHub `chicatancau-create/qoder-toolkit` + GitCode `zhoumoyukuai/qoder-toolkit`），保留作历史备份。

## 六、规则

1. 新技能放 `D:\Skills\<name>\SKILL.md`，目录名小写字母数字连字符，**与 frontmatter `name` 同名**（已知例外见 `THIRD_PARTY.md`）。
2. `description` 必须说清**什么时候用**（触发词），长度 ≤1024 字符。
3. **运行时缓存 / 输出不得写入技能源目录**，用 `AI_SHARED_SKILLS_STATE_DIR`（本机 = `D:\AI-Tool-State`）。
4. 第三方技能必须留 `PROVENANCE.md`（来源 / commit / 许可）；许可未知的标注清楚。
5. 新增或改动后跑 `python D:\Skills\skill-router\router.py sync` 重建索引。
6. 不把框架 / 运行时 / 数据库 / 安全清单的版本写死；已有项目以仓库配置与锁文件为准。

## 七、日常运维

```powershell
$py = 'C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
& $py D:\Skills\skill-router\ops.py status    # 代理 / 接线 / 窗口 / 12 个技能根
& $py D:\Skills\skill-router\ops.py savings   # headroom 真实省了多少
& $py D:\Skills\skill-router\ops.py guard     # 接线守护
& $py D:\Skills\skill-router\ops.py shield    # 自愈盾
& $py D:\Skills\skill-router\router.py match "这次任务描述"
& $py D:\Skills\skill-router\router.py doctor
```

## 八、从 git 恢复

```powershell
git clone https://github.com/chicatancau-create/ai-skills.git D:\Skills
# 国内：git clone https://gitcode.com/zhoumoyukuai/ai-skills.git D:\Skills
& $py D:\Skills\skill-router\wire_agents.py --apply   # 重建默认窗口与各 Agent 联接
& $py D:\Skills\skill-router\router.py sync
& $py D:\Skills\skill-router\ops.py wire --apply      # 接回 headroom 省 token 链路
```

**注意**：`headroom` 的常驻代理与模型缓存不在本仓库里（`D:\uv\tools\headroom-ai`、`D:\uv\data\huggingface\hub` 那 261 MB），恢复后需重跑 `seed_kompress.py` 与 `headroom install apply`，命令见 `headroom\SKILL.md`。
