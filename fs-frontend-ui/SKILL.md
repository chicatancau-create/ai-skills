---
name: fs-frontend-ui
description: "UI/UX 与无障碍规范(阶段2配合 webapp-building 使用)。设计界面、配色与排版、响应式布局、组件可访问性(ARIA/键盘/焦点)、暗色模式、SEO 元数据时使用。按当前 W3C/WCAG 官方资料和项目约束验收。"
---

# UI/UX 与无障碍规范 (fs-frontend-ui)

## 设计系统基础

- **设计令牌**: 颜色(主色/中性色/语义色)、间距(4px 基数)、字号、圆角、阴影全部定义为 CSS 变量, 集中在全局样式
- **配色**: 主色 1 个 + 语义色(成功/警告/错误/信息); 正文与背景对比度 ≥ 4.5:1, 大字(≥24px 或 19px 加粗)≥ 3:1
- **排版**: 行高正文 1.5-1.7; 段落最大宽度 65-75ch; 层级用字号+字重区分, 不只用颜色
- **暗色模式**: 用 CSS 变量 + `prefers-color-scheme`, 提供手动切换; 两种模式都过对比度检查
- **动效**: 尊重 `prefers-reduced-motion`; 动效时长 150-300ms

## 响应式与布局

- 移动优先: 先写移动端样式, `sm:` `md:` `lg:` 渐进增强
- 断点按内容需要设置, 不为"适配某设备"设断点
- 触控目标 ≥ 44×44px; 间距用 4px 网格体系

## 无障碍清单(按当前 WCAG/WAI-ARIA 官方资料，逐项执行)

### 语义与结构
- [ ] 页面只有一个 `h1`, 标题层级不跳级
- [ ] 语义标签优先: `button`/`nav`/`main`/`section`/`form`, 不用 `div onclick` 冒充按钮
- [ ] 页面有跳转主内容链接(skip link)
- [ ] `lang` 属性正确(如 `zh-CN`)

### 图片与媒体
- [ ] 信息性图片有 `alt`(简洁描述内容), 装饰性图片 `alt=""`
- [ ] `next/image` 用于所有图片(自动优化); 图标是 SVG 时用 `aria-hidden` + 文字标签

### 表单
- [ ] 每个输入有 `<label>` 关联(或用 `aria-label`), 错误信息与输入框关联(`aria-describedby`)
- [ ] 错误提示不只用颜色表示, 附文字+图标
- [ ] 必填项明确标记; 校验错误汇总在表单顶部

### 键盘与焦点
- [ ] 全部交互可键盘完成(Tab 顺序符合视觉顺序)
- [ ] 焦点样式可见(不删 outline, 可用 `focus-visible` 定制)
- [ ] 弹窗/抽屉打开时焦点移入, 关闭时焦点还原; 背景内容 `aria-hidden`
- [ ] 页面切换后焦点管理(如跳转后聚焦标题)

### ARIA 原则
- [ ] **无 ARIA 优于错误 ARIA**: 先尝试原生语义
- [ ] 交互组件(标签页/下拉/提示)参照 WAI-ARIA Authoring Practices 模式: https://www.w3.org/WAI/ARIA/apg/patterns/
- [ ] 状态用 `aria-expanded`/`aria-selected`/`aria-current` 表达

### 其他
- [ ] 颜色对比度全部达标(可用 Lighthouse/axe 检测)
- [ ] 不依赖 hover 才能完成操作
- [ ] 动画尊重 `prefers-reduced-motion`

## SEO 与元数据(Next.js)

- 每页导出 `metadata`(title/description/openGraph), 动态页用 `generateMetadata`
- 站点级配置 `metadataBase`、`openGraph` 默认图、favicon
- 结构化数据(JSON-LD)用于文章/商品/面包屑等富内容
- 语义化 HTML 本身就是 SEO 基础(正确标题层级、`alt`、链接文字可读)

## 验证工具

- Lighthouse(Chrome DevTools)每次页面完成跑一次, Accessibility ≥ 95
- `@axe-core` 或 axe DevTools 检查
- 键盘走查: 只用 Tab/Enter/Space/Esc 完成核心流程

## 完成门禁

- [ ] 移动端(375px)与桌面端布局均正常
- [ ] 键盘可完成核心流程, 焦点无丢失
- [ ] Lighthouse 可访问性 ≥ 95
- [ ] 每页 metadata 齐全
- [ ] 已完成视觉回归或浏览器截图检查，并记录视口与结果
- [ ] 交互设计已覆盖 loading/empty/error/success 和 reduced-motion 状态
