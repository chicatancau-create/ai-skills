---
name: fs-frontend
description: "前端开发规范(阶段2)。在 webapp-building 完成结构、视觉、状态和交互设计后，编写仓库实际使用的 React/Next.js/TypeScript 或其他前端页面、组件、hooks、数据获取、表单、状态管理、错误与加载态。"
---

# 前端开发规范 (fs-frontend)

## 核心原则

1. **默认服务端渲染优先**: 能用 Server Component 就不用 Client Component, `"use client"` 是例外不是默认
2. **类型安全无 any**: 全部显式类型, 禁止 `any` 除非注释说明理由
3. **组件小而专一**: 单组件 ≤200 行, 超过即拆分
4. **数据流单向**: 父传子 props, 跨层用 context/Zustand, 避免层层透传

## 组件规范

- **文件命名**: `kebab-case.tsx`(文件) / `PascalCase`(组件名); 页面 `page.tsx`、布局 `layout.tsx` 等保留字除外
- **组件结构顺序**: 类型定义 → hooks → 派生数据 → 事件处理 → JSX; 导出用 `export function Xxx()`, 默认导出仅用于 Next.js 特殊文件
- **Props 类型**: 每个组件定义 `Props` interface 并导出; 事件 props 用 `onXxx` 命名; 布尔 props 用 `isXxx`/`hasXxx`
- **解构与默认值**: 默认值写在解构处, 不用 `defaultProps`

### Server/Client 组件边界

- Server Component: 数据获取、直接访问数据库/文件系统、无需交互的渲染
- Client Component: `useState`/`useEffect`/事件处理/浏览器 API 必须; 在文件顶部 `"use client"`
- **Client 组件只接收可序列化 props**(函数只能从 Server 用 Server Actions 传递)
- 数据尽量在 Server Component 获取后传 props, 少用客户端 fetch

### 数据获取(Next.js App Router)

- 服务端: 直接调用 server 层(如 Prisma), 页面顶层 `await`, 利用自动缓存
- 列表页用 `searchParams` 管理分页/筛选(而非客户端状态), 配 `<Suspense>` 包裹
- 动态数据加 `loading.tsx`(整页骨架)和细粒度 `<Suspense fallback={...}>`
- 变更操作用 Server Actions 或 Route Handlers, 用 `revalidatePath`/`revalidateTag` 更新缓存

### 错误处理

- 每个路由段配 `error.tsx`(必须 `"use client"`, 提供重置按钮)
- `not-found.tsx` 处理 404; 数据缺失抛出 `notFound()`
- 可预期错误显示 toast/内联提示, 不裸抛堆栈

## 状态管理与表单

- **状态分类**: URL 状态(searchParams) > 服务端状态(TanStack Query) > 局部 UI 状态(useState) > 全局状态(Zustand/Context)
- 服务端缓存数据用 TanStack Query, 不手写 `useEffect + fetch`
- **表单**: `react-hook-form` + `zod`(与后端共用 schema), Server Actions 提交; 必填校验前后端都要有(前端是体验, 后端是安全)
- 派生状态用 `useMemo` 别乱用; 跨组件同步用 `useReducer` 处理复杂状态机

## 样式规范

- 遵循仓库已有样式系统；新建或升级 Tailwind 等依赖时先核对官方当前文档，不把某个大版本写成永久前提
- 设计令牌集中在 CSS 变量(`@theme`), 颜色不散落硬编码
- 条件类名用 `clsx`/`cn()`, 不用模板字符串拼接
- 响应式: 移动优先, `md:` `lg:` 渐进增强

## Hooks 规则

- 自定义 hook 以 `use` 开头, 一个 hook 只做一件事
- 依赖数组必须正确填写, 打开 `react-hooks` exhaustive-deps 规则
- 清理副作用(定时器/订阅)必须返回 cleanup
- 避免在 `useEffect` 里同步派生状态(用 `useMemo`/直接计算)

## 完成门禁

- [ ] lint + typecheck 全绿, 无 `any`
- [ ] 每个数据获取页面有 loading 态, 每个路由段有 error.tsx
- [ ] 表单前后端共用 zod schema
- [ ] 组件均 ≤200 行, 无明显重复代码
- [ ] 本地 dev 模式过一遍核心交互, 无控制台报错
- [ ] 已按 `webapp-building` 记录视觉结构、组件状态、响应式行为和交互验收点
- [ ] 前端表单、加载态、错误态与后端 API 契约已联调
