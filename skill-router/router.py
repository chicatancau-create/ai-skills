#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""skill-router: 本机技能总路由。

默认只有 skill-router + headroom 两个技能被 Agent 加载。
本脚本负责「这次任务该用哪些技能」的判定与按需取用。

用法（任何解释器都行，纯标准库）：
  python router.py sync                 重建 catalog.json / CATALOG.md
  python router.py list                 打印紧凑索引（name | 一句话触发）
  python router.py match "任务描述"      按相关度给出候选技能 + SKILL.md 绝对路径
  python router.py show <name>          打印该技能 SKILL.md 的绝对路径
  python router.py cat <name>           直接打印该技能 SKILL.md 全文
  python router.py status               当前默认开启窗口（D:\\Skills-active）
  python router.py pin <name> [...]     把技能常驻到默认窗口（建 Junction）
  python router.py unpin <name> [...]   取消常驻
  python router.py doctor               体检：库/窗口/联接/目录名与 name 一致性
"""
import os, sys, json, re, subprocess, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = r"D:\Skills"
ACTIVE = r"D:\Skills-active"
DISABLED = r"D:\Skills-disabled"
EXTRA_LIBS = [
    (r"D:\QoderToolkit", "qoder"),          # Junction -> D:\_整理\04-AI工具包\QoderToolkit
    (r"C:\Users\Admin\.cc-switch\skills", "cc-switch"),
]
ALWAYS_ON = ["skill-router", "headroom"]
CATALOG_JSON = os.path.join(HERE, "catalog.json")
CATALOG_MD = os.path.join(HERE, "CATALOG.md")

# 人工 curated 触发词：比从 description 里机械切词准得多。
# key = frontmatter name（不是目录名）。value = (一句话用途, [触发词...])
TRIGGERS = {
    "skill-router": ("技能总路由：判定本次任务该开哪些技能", ["技能", "路由", "skill", "该用哪个"]),
    "headroom": ("省 token：压缩送进 LLM 的工具输出/日志/JSON", ["省token", "压缩", "token", "上下文", "headroom", "context", "日志太长"]),
    # --- 全栈流水线 ---
    "fs-fullstack": ("全栈项目总控（新项目/重构/加模块，第一个加载）", ["全栈", "做个网站", "做个应用", "新项目", "从零", "fullstack", "重构项目"]),
    "fs-plan": ("阶段0 需求分析与技术选型", ["需求分析", "技术选型", "选型", "架构设计", "里程碑", "需求文档"]),
    "fs-scaffold": ("阶段1 脚手架与工程化初始化", ["脚手架", "初始化项目", "scaffold", "eslint", "prettier", "工程化", "ci"]),
    "fs-frontend": ("阶段2 前端页面/组件/hooks 实现", ["前端", "组件", "react", "next.js", "hooks", "页面", "typescript", "vue"]),
    "fs-frontend-ui": ("阶段2 UI/UX 与无障碍规范", ["ui", "ux", "配色", "排版", "响应式", "无障碍", "aria", "暗色", "seo", "wcag"]),
    "fs-backend": ("阶段3 后端 API 设计与实现", ["后端", "api", "restful", "路由", "中间件", "认证", "授权", "openapi", "接口"]),
    "fs-database": ("阶段4 数据库设计与数据层", ["数据库", "表结构", "索引", "迁移", "orm", "sql", "事务", "n+1", "建表"]),
    "fs-testing": ("阶段5 测试规范", ["测试", "单元测试", "e2e", "覆盖率", "test", "vitest", "pytest", "jest"]),
    "fs-security": ("阶段6 安全审查与加固", ["安全", "漏洞", "xss", "csrf", "注入", "owasp", "密钥", "加固", "隐私"]),
    "fs-code-review": ("阶段6后 代码审查与质量门禁", ["代码审查", "review", "pr", "lint", "typecheck", "重构", "提交规范", "门禁"]),
    "fs-performance": ("阶段7 性能优化", ["性能", "优化", "加载慢", "core web vitals", "bundle", "缓存", "响应时间", "卡顿"]),
    "fs-deploy": ("阶段8 部署与运维", ["部署", "上线", "docker", "dockerfile", "ci/cd", "域名", "https", "回滚", "监控", "运维"]),
    "fs-docs": ("文档编写规范（README/API/ADR/CHANGELOG）", ["文档", "readme", "adr", "changelog", "注释", "api文档"]),
    # --- 前端设计 ---
    "webapp-building": ("Kimi 前端设计与实现默认入口（复杂 UI/状态）", ["前端设计", "kimi", "webapp", "界面设计", "交互设计", "设计系统"]),
    "impeccable": ("高质量前端界面/海报/落地页，避免 AI 通用感", ["海报", "落地页", "landing", "设计感", "好看", "artifact", "网页设计", "ppt视觉"]),
    "frontend-slides": ("HTML 演示文稿（可由 PPT 转换）", ["html演示", "幻灯片", "slides", "演示文稿", "网页ppt", "动画演示"]),
    "web-taste": ("网页审美/品味评审与改造", ["审美", "品味", "taste", "网页评审", "视觉改造"]),
    "landing-page-design": ("落地页/营销页完整系统：结构+转化文案+视觉令牌+动效（滚动揭示、逐词点亮）",
                            ["落地页", "landing", "营销页", "官网首页", "动态网页", "动效", "动画",
                             "滚动动画", "滚动揭示", "逐词", "hero", "首屏", "转化", "cta",
                             "标题文案", "字体刻度", "间距", "圆角", "暗色", "intersectionobserver",
                             "framer", "prefers-reduced-motion", "网页设计"]),
    "figma-designer": ("在 Figma 里按真实结构做设计（变量/文本样式/自动布局/组件全状态），需 Figma MCP",
                       ["figma", "设计稿", "组件库", "自动布局", "autolayout", "设计变量",
                        "文本样式", "design token", "设计系统", "mockup", "原型稿"]),
    # --- 文档 / 办公 ---
    "docx": ("Word 文档 .docx/.dotx 读写编辑", ["word", "docx", "dotx", "文档", "公文", "合同", "页眉", "目录页码"]),
    "xlsx": ("Excel/CSV/TSV 表格读写与公式", ["excel", "xlsx", "csv", "tsv", "表格", "公式", "透视", "报表"]),
    "pptx": ("PowerPoint .pptx/.potx 读写编辑", ["ppt", "pptx", "potx", "幻灯片", "演示", "deck", "课件"]),
    "pdf": ("PDF 读取/提取/合并/拆分/表单/OCR", ["pdf", "扫描件", "ocr", "合并pdf", "提取表格", "pdf表单"]),
    "ppt-master": ("PPT 母版/批量生成与归属校验（Qoder 工具箱）", ["ppt母版", "批量ppt", "ppt生成", "attribution_guard"]),
    # --- 平台 / 外部服务 ---
    "dws": ("钉钉全套能力（表格/日程/通讯录/审批/文档/云盘/邮箱）", ["钉钉", "dingtalk", "审批", "考勤", "日报", "周报", "通讯录", "钉钉文档", "云盘", "听记"]),
    "github": ("用 gh CLI 操作 GitHub（issue/PR/CI/api）", ["github", "gh ", "issue", "pull request", "pr", "ci运行", "仓库"]),
    "web-search": ("Brave 网页搜索（排名结果+摘要）", ["搜索", "查一下", "网上", "search", "brave", "最新资料"]),
    "tavily-search": ("Tavily LLM 优化网页搜索", ["tavily", "联网搜索", "查新闻", "检索资料"]),
    "find-skills": ("发现/安装可复用技能", ["有没有技能", "找个skill", "安装技能", "能力扩展"]),
    # --- 本机运维 / 环境 ---
    "local-ai-handbook": ("本机《AI本地使用手册》检索入口（报错/乱码/超时先查）", ["手册", "报错", "乱码", "超时", "编码", "bom", "踩坑", "本机经验", "提权", "路由", "插件"]),
    "windows-gui-control": ("操控 Windows GUI（截图/点按钮/快捷键），不抢用户前台", ["操控", "gui", "截图", "点按钮", "快捷键", "打开软件", "界面操作", "前台"]),
    "diagnose-windows-sandbox-acl": ("DSH 沙箱意外拒绝访问时，一条命令查路径及所有父目录并当场修好权限", ["拒绝访问", "access denied", "winerror 5", "权限", "acl", "沙箱", "sandbox", "读不到", "写不了", "workspace"]),
    "xd-authoring": ("生成/修改 Adobe XD .xd 文件与交互", ["xd", "adobe xd", "原型", "画板", "交互跳转", "课件xd"]),
    "vision-tool": ("本地视觉：看图/识字/对比图/分析截图（牧羊人 Qwen3.5-9B）", ["看图", "识别图片", "图中文字", "分析截图", "对比图片", "视觉", "识图"]),
    "obsidian-vault-validation": ("Obsidian 学习库结构/路由改动后校验", ["obsidian", "vault", "学习库", "分册", "readme链接", "ocr路由"]),
    "darwin-skill": ("技能自动优化与 8 维评分（达尔文）", ["优化skill", "skill评分", "达尔文", "darwin", "skill质量", "改改skill"]),
    "skill-creator": ("创建/更新技能的规范指南", ["写个skill", "新建技能", "创建skill", "技能规范"]),
    "self-improving-agent": ("记录错误/纠正/经验，持续改进", ["记下来", "经验", "纠正", "复盘", "学习记录", "别再犯"]),
    "requirement-translator": ("把模糊口语需求转成结构化可执行规格", ["需求转译", "需求不清", "细化需求", "明确需求", "分析这个需求"]),
    "checkpoint": ("把当前进度存进 memory-keeper 防丢", ["存进度", "checkpoint", "断点", "防丢", "保存进度"]),
    # --- 逆向（仅授权目标）---
    "spider-king": ("【仅授权目标】纯 Web 协议逆向 → 无浏览器 Python 采集器", ["逆向", "爬虫", "协议", "加密参数", "指纹", "js逆向", "采集器", "风控"]),
    "wechat-miniapp-reverse": ("【仅授权目标】微信小程序/WMPF 逆向调试", ["小程序", "微信小程序", "wmpf", "wechatappex", "appservice", "小程序调试"]),
    # --- Qoder 取证方法论 ---
    "qoder-toolkit": ("Qoder 工具箱总入口（本机硬规则 + 路由）", ["qoder", "工具箱"]),
    "headless-cdp-visual-acceptance": ("无头 CDP 视觉验收", ["无头", "cdp", "视觉验收", "截图对比", "headless"]),
    "verify-app-security-claims": ("核实应用的安全声明是否属实", ["安全声明", "核实", "宣称", "安全审计"]),
    "visual-tool-add-section": ("给可视化工具加新板块", ["加板块", "加section", "可视化工具"]),
    "codeweave-visual-rebuild-rerun": ("CodeWeave 视觉重建复跑（60-cell 矩阵）", ["codeweave", "视觉重建", "复跑", "60-cell"]),
    "localstorage-data-shape-seeding": ("按真实数据形状给 localStorage 播种", ["localstorage", "播种", "造数据", "数据形状"]),
    "install-github-skill-on-windows-qoder": ("在 Windows Qoder 上安装 GitHub 技能", ["安装github技能", "qoder装技能"]),
    # --- 其他 ---
    "fullstack-dev": ("全栈后端架构与前后端联调指南", ["后端架构", "联调", "express", "crud", "实时应用", "服务层"]),
    "ios-application-dev": ("iOS 开发（UIKit/SnapKit/SwiftUI/HIG）", ["ios", "swift", "swiftui", "uikit", "snapkit", "iphone", "苹果"]),
    "life-decision-guide": ("人生决策指南（Obsidian 上游库）", ["人生决策", "选择", "决策指南"]),
}


def reparse(p):
    try:
        return getattr(os.lstat(p), "st_reparse_tag", 0)
    except OSError:
        return -1


def is_link(p):
    return reparse(p) > 0


def parse_fm(path):
    """Return (name, description) from SKILL.md frontmatter. Pure stdlib."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
    except OSError:
        return None, None
    if not txt.startswith("---"):
        return None, None
    end = txt.find("\n---", 3)
    if end < 0:
        return None, None
    fm = txt[3:end]
    name = desc = None
    key = None
    buf = []
    for line in fm.splitlines():
        m = re.match(r"^(name|description)\s*:\s*(.*)$", line)
        if m:
            if key == "description":
                desc = " ".join(buf).strip()
            key = m.group(1)
            val = m.group(2).strip()
            if key == "name":
                name = val.strip("'\"")
                key = None
            else:
                buf = [] if val in ("|", ">", "|-", ">-", "") else [val]
        elif key == "description" and line.startswith((" ", "\t")):
            buf.append(line.strip())
    if key == "description":
        desc = " ".join(buf).strip()
    if desc:
        desc = desc.strip("'\"")
    return name, desc


def scan():
    """All skills across the library + extra libs. Returns list of dicts."""
    out = []
    seen = {}
    roots = [(LIB, "library")] + EXTRA_LIBS
    for root, tag in roots:
        if not os.path.isdir(root):
            continue
        for n in sorted(os.listdir(root)):
            p = os.path.join(root, n)
            if not os.path.isdir(p):
                continue
            sm = os.path.join(p, "SKILL.md")
            if not os.path.isfile(sm):
                continue
            name, desc = parse_fm(sm)
            name = name or n
            rec = {
                "name": name, "dir": n, "root": root, "source": tag,
                "skill_md": sm, "description": desc or "",
                "link": is_link(p),
            }
            if name in seen:
                # library wins over extra libs; keep first, record duplicates
                seen[name].setdefault("duplicates", []).append(sm)
                continue
            seen[name] = rec
            out.append(rec)
    for rec in out:
        t = TRIGGERS.get(rec["name"])
        rec["brief"] = t[0] if t else (rec["description"][:60] or rec["name"])
        rec["triggers"] = t[1] if t else []
    return out


def cmd_sync():
    recs = scan()
    with open(CATALOG_JSON, "w", encoding="utf-8") as f:
        json.dump({"generated_by": "skill-router", "library": LIB,
                   "active_window": ACTIVE, "always_on": ALWAYS_ON,
                   "skills": recs}, f, ensure_ascii=False, indent=1)
    lines = ["# 技能总索引（由 router.py sync 生成，勿手改）", "",
             f"共 {len(recs)} 个技能。默认只加载 `skill-router` + `headroom`。",
             "需要哪个就 **直接 read 它的 SKILL.md**，不要试图把它当工具调用。", "",
             "| name | 用途 | SKILL.md |", "|---|---|---|"]
    for r in sorted(recs, key=lambda x: x["name"]):
        lines.append(f"| `{r['name']}` | {r['brief']} | `{r['skill_md']}` |")
    with open(CATALOG_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"synced {len(recs)} skills -> {CATALOG_JSON}")
    print(f"                        -> {CATALOG_MD}")
    missing = [r["name"] for r in recs if r["name"] not in TRIGGERS]
    if missing:
        print(f"NOTE: {len(missing)} skill(s) have no curated triggers: {', '.join(missing)}")


def load_catalog():
    if not os.path.isfile(CATALOG_JSON):
        cmd_sync()
    with open(CATALOG_JSON, "r", encoding="utf-8") as f:
        return json.load(f)["skills"]


def cmd_list():
    for r in sorted(load_catalog(), key=lambda x: x["name"]):
        mark = "*" if r["name"] in ALWAYS_ON else " "
        print(f"{mark} {r['name']:34s} {r['brief']}")


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return s


def tokens(s):
    """ASCII words + CJK bigrams/unigrams."""
    s = norm(s)
    ascii_words = re.findall(r"[a-z0-9][a-z0-9_.+#/-]*", s)
    cjk = re.findall(r"[\u4e00-\u9fff]+", s)
    grams = []
    for run in cjk:
        if len(run) == 1:
            grams.append(run)
        else:
            grams.extend(run[i:i + 2] for i in range(len(run) - 1))
            grams.append(run)
    return set(ascii_words) | set(grams)


def cmd_match(task):
    recs = load_catalog()
    qt = tokens(task)
    scored = []
    for r in recs:
        if r["name"] in ALWAYS_ON:
            continue
        hay = norm(r["name"] + " " + r["brief"] + " " + " ".join(r["triggers"]) + " " + r["description"])
        score = 0.0
        hits = []
        for trig in r["triggers"]:
            tn = norm(trig)
            if tn and tn in norm(task):
                score += 3.0 + min(len(tn), 6) * 0.3
                hits.append(trig)
        if norm(r["name"]) in norm(task):
            score += 6.0
            hits.append(r["name"])
        for t in qt:
            if len(t) >= 2 and t in hay:
                score += 0.35
        if score > 0:
            scored.append((score, r, hits))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("没有命中任何技能。按通用能力直接做，不要强行套技能。")
        return
    # 噪声闸：低于 2.0 分的多半是单字偶然命中，不要塞给模型。
    strong = [s for s in scored if s[0] >= 2.0]
    show = strong[:6] if strong else scored[:2]
    print(f"任务: {task}\n")
    print("候选（按相关度，只读你真正需要的那几个）:")
    for score, r, hits in show:
        print(f"  {score:5.1f}  {r['name']:32s} {r['brief']}")
        print(f"         read: {r['skill_md']}")
        if hits:
            print(f"         命中: {', '.join(hits[:8])}")
    if not strong:
        print("\n（相关度都很低，可能本次任务不需要任何技能。）")
    print("\n下一步：用文件读取工具打开上面需要的 SKILL.md，按它执行。")
    print("不要 pin，除非用户明确要求某技能长期常驻。")


def find(name):
    for r in load_catalog():
        if r["name"] == name or r["dir"] == name:
            return r
    return None


def cmd_show(name):
    r = find(name)
    if not r:
        print(f"NOT FOUND: {name}")
        sys.exit(2)
    print(r["skill_md"])


def cmd_cat(name):
    r = find(name)
    if not r:
        print(f"NOT FOUND: {name}")
        sys.exit(2)
    with open(r["skill_md"], "r", encoding="utf-8", errors="replace") as f:
        sys.stdout.write(f.read())


def junction(src, dst):
    r = subprocess.run(["cmd", "/c", "mklink", "/J", src, dst],
                       capture_output=True, text=True, encoding="gbk", errors="replace",
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return r.returncode == 0, (r.stdout or "") + (r.stderr or "")


def cmd_status():
    print(f"库      : {LIB}  exists={os.path.isdir(LIB)}")
    print(f"默认窗口: {ACTIVE}  exists={os.path.isdir(ACTIVE)}")
    if os.path.isdir(ACTIVE):
        for n in sorted(os.listdir(ACTIVE)):
            p = os.path.join(ACTIVE, n)
            if not os.path.isdir(p):
                continue          # app state files (WorkBuddy *_migration.json)
            tgt = os.readlink(p) if is_link(p) else "(real dir)"
            ok = os.path.isfile(os.path.join(p, "SKILL.md"))
            print(f"  {'OK ' if ok else 'BAD'} {n:34s} -> {tgt}")
    print(f"停用区  : {DISABLED}  exists={os.path.isdir(DISABLED)}")


def cmd_pin(names):
    os.makedirs(ACTIVE, exist_ok=True)
    for name in names:
        r = find(name)
        if not r:
            print(f"NOT FOUND: {name}")
            continue
        dst = os.path.join(ACTIVE, r["dir"])
        if os.path.exists(dst):
            print(f"already pinned: {name}")
            continue
        ok, msg = junction(dst, os.path.dirname(r["skill_md"]))
        print(f"{'PINNED' if ok else 'FAIL'} {name} -> {os.path.dirname(r['skill_md'])} {msg.strip()}")


def cmd_unpin(names):
    for name in names:
        r = find(name)
        d = r["dir"] if r else name
        p = os.path.join(ACTIVE, d)
        if not os.path.exists(p):
            print(f"not pinned: {name}")
            continue
        if name in ALWAYS_ON:
            print(f"REFUSE: {name} 是默认必开技能，不能 unpin")
            continue
        try:
            if is_link(p):
                os.rmdir(p)
            else:
                print(f"REFUSE: {p} 不是联接，不敢删")
                continue
            print(f"UNPINNED {name}")
        except OSError as e:
            print(f"FAIL {name}: {e}")


def cmd_doctor():
    problems = []
    recs = load_catalog()
    print(f"catalog: {len(recs)} skills")
    for r in recs:
        if not os.path.isfile(r["skill_md"]):
            problems.append(f"SKILL.md 缺失: {r['skill_md']}")
        if r["dir"] != r["name"] and r["source"] == "library":
            known = {"reverse-trace": "spider-king", "reverse-wechat-miniapp": "wechat-miniapp-reverse",
                     "sickn33-frontend-slides": "frontend-slides",
                     "barry-liu-888-requirement-translator": "requirement-translator",
                     "barnhardt-enterprises-inc-checkpoint": "checkpoint",
                     "brave-web-search": "web-search"}
            if known.get(r["dir"]) != r["name"]:
                problems.append(f"目录名与 name 不一致: {r['dir']} vs {r['name']}")
    for root, tag in EXTRA_LIBS:
        if not os.path.isdir(root):
            problems.append(f"额外库不可达: {root}")
    if not os.path.isdir(ACTIVE):
        problems.append(f"默认窗口不存在: {ACTIVE}")
    else:
        # Only directories are skills.  WorkBuddy drops *_migration.json state
        # files into whatever its skills root points at; they are not entries.
        have = {n for n in os.listdir(ACTIVE)
                if os.path.isdir(os.path.join(ACTIVE, n))}
        for n in ALWAYS_ON:
            if n not in have:
                problems.append(f"默认窗口缺少必开技能: {n}")
        for n in sorted(have):
            if not os.path.isfile(os.path.join(ACTIVE, n, "SKILL.md")):
                problems.append(f"默认窗口条目失效: {n}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("\nOK: 库/窗口/联接/命名全部正常")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "sync":
        cmd_sync()
    elif cmd == "list":
        cmd_list()
    elif cmd == "match":
        cmd_match(" ".join(args))
    elif cmd == "show":
        cmd_show(args[0])
    elif cmd == "cat":
        cmd_cat(args[0])
    elif cmd == "status":
        cmd_status()
    elif cmd == "pin":
        cmd_pin(args)
    elif cmd == "unpin":
        cmd_unpin(args)
    elif cmd == "doctor":
        cmd_doctor()
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
