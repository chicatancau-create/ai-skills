# Web-Taste Skill

> **Anti-slop web frontend skill cho AI coding agents** (Claude Code / Cursor / Codex / Gemini CLI / Kimi CLI / Hermes / OpenCode).
> Auto-trigger MỌI web task. Force ship **Kimi/Lovable-tier** quality bằng deterministic guardrails + ready-to-paste blueprints.
> Distilled từ 8 nguồn: [open-design](https://github.com/nexu-io/open-design), [taste-skill](https://github.com/Leonxlnx/taste-skill), [impeccable.style](https://impeccable.style/), [getdesign.md](https://getdesign.md/), [designmd.ai](https://designmd.ai/), [refero.design](https://styles.refero.design/), [kimi.com](https://kimi.com/), [lovable.dev](https://lovable.dev/).

**Triết lý:** AI không freestyle. Lock brief bằng Discovery Form → pick deterministic Direction → execute với 27 anti-pattern guardrails + 5-dim critique + 26-aspect tier scoring → ship 1 artifact.

## Auto-trigger

Skill kích hoạt **TỰ ĐỘNG** khi:
- Chạm file: `.tsx`, `.jsx`, `.ts`, `.vue`, `.svelte`, `.astro`, `.html`, `.css`, `.scss`
- Chạm thư mục: `components/`, `pages/`, `app/`, `src/`
- User nói: build/sửa/render/design/tạo + page/landing/UI/component/storefront/admin/site
- User mention: "design như Kimi/Lovable/Linear/Stripe/Apple/Monocle/Vercel"

**Scale theo task size:** big task → full Discovery Form workflow · medium → skip form apply directions · small → quick anti-slop checklist.

---

## Cài đặt

### Cách 1: Symlink global cho mọi project Claude Code

```bash
ln -s "$(pwd)/skills/web-taste" ~/.claude/skills/web-taste
```

Sau khi symlink, mọi project mở Claude Code đều thấy skill `web-taste`. Trigger bằng cách nói "build landing", "render UI mới", "design web page", "tạo trang", v.v.

### Cách 2: Copy vào project local

```bash
cp -r skills/web-taste <your-project>/.claude/skills/
```

### Cách 3: Dùng `npx skills add` (tương thích Vercel agent-skills convention)

```bash
# Local
npx skills add /Volumes/hai/web-taste-skill

# Hoặc khi đã push lên GitHub
npx skills add https://github.com/<your-org>/web-taste-skill
```

---

## Cấu trúc

```
web-taste-skill/
├── README.md                          # File này
├── LICENSE                            # MIT
└── skills/
    └── web-taste/
        ├── SKILL.md                   # Entry — 3 luật cứng + workflow + bias rules
        ├── references/
        │   ├── directions.md          # 5 visual directions deterministic (OKLch palette)
        │   ├── discovery-form.md      # Discovery Form pattern + JSON schema
        │   ├── anti-slop.md           # 27 deterministic anti-patterns (impeccable.style)
        │   ├── critique.md            # 5-dim self-critique framework
        │   └── design-md-format.md    # DESIGN.md spec (Google Stitch compatible)
        └── design-systems/             # Starter DESIGN.md examples
            ├── linear.md
            ├── stripe.md
            ├── apple.md
            ├── monocle-editorial.md
            └── brutalist-arena.md
```

---

## Khi nào dùng

```
DÙNG khi:
  ✓ Build landing/marketing page mới từ scratch
  ✓ Render UI prototype/dashboard/editorial từ brief
  ✓ Có Figma/screenshot, ask "build cái này thành web"
  ✓ Project mới, chưa có DESIGN.md / theme

KHÔNG dùng khi:
  ✗ Sửa component nhỏ trong app có sẵn → dùng skill khác
  ✗ Mobile app (Flutter/iOS/Android/RN) → skill mobile-design
  ✗ Backend / API / DB → skill backend
  ✗ Bug fix nhanh → fix trực tiếp
```

---

## Nguồn (credit)

| Nguồn | Đóng góp |
|-------|----------|
| [nexu-io/open-design](https://github.com/nexu-io/open-design) | Discovery Form pattern, 5 directions deterministic, 5-dim critique |
| [leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | Bias correction rules, dial config (variance/motion/density), AI Tells |
| [impeccable.style](https://impeccable.style/) | 27 anti-patterns, brand vs product mode, design fluency 7 areas |
| [getdesign.md](https://getdesign.md/) | DESIGN.md collection format, integration pattern |
| [designmd.ai](https://designmd.ai/) | "Drop DESIGN.md in project root" workflow |
| [styles.refero.design](https://styles.refero.design/) | DESIGN.md extraction từ real websites |
| [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | Junior-Designer workflow, 5 schools × 20 philosophies, anti-AI-slop |
| [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) | Pre-flight asset reads, P0 self-check, theme rhythm |

---

## License

MIT — tự do dùng/fork/sửa.
