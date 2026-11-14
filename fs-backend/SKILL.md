---
name: fs-backend
description: "后端 API 设计与实现规范(阶段3)。编写 RESTful API、路由、中间件、认证授权、输入校验、错误处理、日志、分页排序过滤、文件上传时使用。优先遵循仓库既有框架和官方当前文档，API 文档优先采用 OpenAPI 3.1。"
---

# 后端 API 设计与实现 (fs-backend)

## API 设计规范(RESTful)

### 资源与路径
- 复数名词表示资源: `/api/users`、`/api/orders`; 嵌套 ≤2 层: `/api/users/{id}/orders`
- 路径只含资源与标识, 动作用 HTTP 方法表达, 不用 `/getUser` 这类动词路径
- 版本策略: `/api/v1/...`(URL 版本)或 `Accept-Version` 头, 根据仓库和客户端兼容策略在项目初始确定
- 用 `{id}` 统一标识符命名, 不用 `{userId}` `{orderId}` 混搭

### HTTP 方法与状态码(严格语义)

| 场景 | 返回 |
| --- | --- |
| 创建成功 | `201` + Location 头 + 资源体 |
| 查询/更新/删除成功 | `200`(更新/删除返回资源或 `204`) |
| 异步任务受理 | `202` |
| 参数校验失败 | `400`(附字段级错误) |
| 未认证 | `401` |
| 已认证但无权限 | `403`(不泄露资源是否存在) |
| 资源不存在 | `404` |
| 冲突(重复数据等) | `409` |
| 限流 | `429`(附 `Retry-After`) |
| 服务端错误 | `500`(不返回堆栈) |

### 请求/响应约定
- 统一响应包裹: `{ "data": ..., "error": { "code", "message", "details" } }`(二选一, 不同时出现)
- 时间一律 ISO 8601 UTC(如 `2026-08-14T10:00:00Z`); 金额用最小单位整数或字符串, 不用浮点
- 分页: `?page=1&pageSize=20` 或 cursor 分页(大数据量), 响应带 `total`/`nextCursor`
- 排序: `?sort=createdAt&order=desc`(白名单校验); 过滤: 字段级 `?status=active` 白名单

## 分层架构

```
route(参数解析/校验/响应) → service(业务逻辑) → repository/ORM(数据访问)
```

- Route 层不做业务逻辑; Service 层不接触 HTTP 概念(方便复用与测试)
- 每层职责单一, 依赖注入方向统一

## 输入校验(重要: 后端永远不信任前端)

- 用 zod(TS)或 pydantic(Python)声明 schema, **与前端共用同一份 schema 源**
- 校验失败返回 `400` + 字段级错误 `details: [{ field, message }]`
- 校验通过后类型是收窄的, 不要二次手写判断

## 认证与授权

- **认证**: 生产用成熟方案(Auth.js/OAuth2/JWT 库), 严禁手写加密; 密码哈希用 argon2id/bcrypt
- **会话**: 服务端会话(cookie + httpOnly + SameSite=Lax/Strict)优先于 localStorage 存 token
- **授权**: 每个受保护接口独立检查权限(中间件/守卫), 不依赖"前端没展示按钮"
- 资源级权限: 查他人资源前必须校验所有权或角色

## 错误处理与日志

- 全局错误处理器: 已知错误→对应状态码; 未知错误→`500` + 内部日志(含 requestId), 响应只含 `requestId` 供排查
- 每个请求打日志: 方法、路径、状态码、耗时、requestId(不打印密码/token/敏感字段)
- 结构化日志(JSON), 便于采集

## 其他要点

- **幂等性**: 支付/下单等接口用幂等键(idempotency key)防止重复提交
- **限流**: 登录/验证码/公开接口必须限流(内存或 Redis)
- **CORS**: 明确允许的来源白名单, 不用 `*` + 凭证同开
- **文件上传**: 限制大小、MIME 白名单、重命名存储、不在 web 根目录保存
- **API 文档**: 用 OpenAPI 3.1 规范, Fastify/NestJS 配 `@fastify/swagger`/`@nestjs/swagger` 自动生成, 每次新增接口同步更新

## 完成门禁

- [ ] 所有输入有 zod/pydantic schema 校验
- [ ] 统一错误格式 + 全局错误处理器就绪
- [ ] 认证/授权按接口逐一检查过
- [ ] OpenAPI 文档可访问且与代码同步
- [ ] 分页/排序/过滤实现且字段白名单
- [ ] 用 curl 或 HTTP 客户端实测每个接口(含错误场景)
- [ ] 前端已按真实契约联调至少一条成功和一条错误路径
