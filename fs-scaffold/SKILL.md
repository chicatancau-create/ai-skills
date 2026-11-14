---
name: fs-scaffold
description: "项目脚手架与工程化初始化(阶段1)。技术栈确定后初始化项目、配置 TypeScript、ESLint、Prettier、Git 规范、环境变量、目录结构、CI 基础流水线时使用。产出一个 lint/typecheck/test/build 全绿的工程骨架。"
---

# 项目脚手架与工程化 (fs-scaffold)

## 执行流程

### 1. 初始化项目

**全栈一体化(常用起点)**:
```
根据 `fs-plan` 的技术决策和官方当前脚手架文档执行对应初始化命令；不要复制过期的固定版本或假设某一框架永远适用。
```

**前端/后端分离时**: 分别按选定框架的当前官方脚手架文档初始化，独立目录或 monorepo 结构由项目约束决定。

初始化后先跑通项目实际的 `dev`、`build` 脚本再继续。

### 2. 基础工程化配置(按最新标准)

| 项 | 要求 |
| --- | --- |
| 包管理器 | 遵循仓库已有包管理器和锁文件；新项目根据团队/平台约束选择并只提交一个锁文件 |
| TypeScript | `tsconfig.json` 开启 `strict: true`、`noUncheckedIndexedAccess`、`verbatimModuleSyntax`、`noImplicitOverride` |
| ESLint | 使用当前官方推荐配置（flat config 或项目兼容方案），新建/升级时核对 typescript-eslint 与框架插件兼容性 |
| 格式化 | Prettier + `prettier-plugin-tailwindcss`, 提交前自动执行 |
| Git hooks | husky: `pre-commit` 跑 lint-staged(lint+format), `commit-msg` 跑 commitlint(Conventional Commits) |
| 编辑器 | 提交 `.editorconfig`, 确保 2 空格缩进、LF 换行、UTF-8 |

### 3. 目录结构规范

```
src/
├── app/            # Next.js 路由(App Router), 按路由组织
├── components/     # 通用 UI 组件(ui/ + 业务通用)
├── features/       # 按业务域组织的功能模块(页面私有组件放这里)
├── lib/            # 工具函数、API 客户端、无副作用逻辑
├── hooks/          # 全局共享 hooks
├── server/         # 服务端专属: db、service、数据访问(仅服务端代码)
└── types/          # 全局类型定义
```

原则: 组件就近放置, 被 2 处以上使用再提升到共享目录。

### 4. 环境变量规范

- 提交 `.env.example`(含所有变量名+注释, 值留空), `.env.local` 进 `.gitignore`
- 客户端变量必须 `NEXT_PUBLIC_` 前缀, 其余只在服务端使用
- 密钥严禁写入任何前端代码或提交历史

### 5. CI 基础流水线(GitHub Actions)

最小流水线 `ci.yml`: 触发 push/PR → 使用仓库声明的包管理器安装依赖 → `lint` → `typecheck` → `test` → `build`。缓存对应包管理器依赖。

### 6. Git 提交规范

- Conventional Commits: `feat:` `fix:` `docs:` `refactor:` `test:` `chore:`
- 初始化提交: `chore: project scaffold`
- `.gitignore`: 按框架默认 + `.env*`(保留 `.env.example`)

## 完成门禁

- [ ] 项目实际 `dev` 正常启动, `build` 成功
- [ ] 项目实际 `lint`、`typecheck`、`test` 全绿(测试为空则先放一个冒烟测试)
- [ ] `.env.example`、`.gitignore`、`.editorconfig` 齐全
- [ ] husky + commitlint 生效(模拟一次不规范提交被拦截)
- [ ] CI 配置文件存在且语法正确
- [ ] 记录验证结果；无关键阻塞时继续进入阶段 2
