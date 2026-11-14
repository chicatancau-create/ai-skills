---
name: fs-deploy
description: "部署与运维(阶段8)。准备生产部署、编写 Dockerfile/docker-compose、管理生产环境变量、CI/CD 流水线、域名与 HTTPS、健康检查、备份与回滚、监控日志时使用。目标: 一键部署, 可回滚, 可观测。"
---

# 部署与运维 (fs-deploy)

## 部署前检查清单(硬性)

- [ ] 已过 fs-security 安全审查
- [ ] 测试全绿, CI 通过
- [ ] `.env.example` 与生产环境变量一一对应, 密钥由部署平台注入
- [ ] 数据库迁移脚本就绪且已演练
- [ ] 无 debug 模式、无测试账号、无示例数据残留

## 部署目标选择

| 场景 | 推荐 | 说明 |
| --- | --- | --- |
| 快速上线/学习项目 | Vercel / 云平台 | 零运维, 自动 CI/CD + 预览环境 |
| 自有服务器/需自定义 | Docker + 自托管 | 可控性强, 见下方规范 |
| 数据库 | 云数据库托管 | 自动备份/高可用, 不自行裸部署 |

### Docker 规范

- **多阶段构建**: build 阶段装依赖编译, 运行阶段只留产物；基础镜像按项目运行时的当前官方支持标签选择并记录核对依据
- **非 root 运行**: 创建专用用户运行应用
- **最小镜像**: 用 `.dockerignore` 排除 node_modules/.git/.env; 缓存层合理排序(先装依赖后复制代码)
- **健康检查**: Dockerfile 配 `HEALTHCHECK`
- **docker-compose 模板**: app + postgres + (可选 redis), 数据卷持久化, 网络隔离, 不把数据库端口暴露公网

## 环境变量管理

- 开发: `.env.local`(不入库); 生产: 平台密钥管理(Vercel Env / GitHub Secrets / 服务器 systemd env)
- 启动时校验必需变量(缺失即报错退出, 不带默认值硬跑)
- 密钥轮换有流程记录; 不打印环境变量

## CI/CD(GitHub Actions 模板要点)

```
push main → install → lint → typecheck → test → build → deploy
push PR   → install → lint → typecheck → test(预览部署可选)
```

- 部署步骤用平台官方 action(如 vercel-action), 配 production/preview 环境
- 数据库迁移作为独立部署步骤, 先备份再迁移
- 部署失败自动停止并通知

## HTTPS 与域名

- 强制 HTTPS: 平台自动(Let's Encrypt); 自托管用 Caddy(自动证书)或 nginx+certbot
- HSTS 开启; www 与非 www 统一跳转
- 子域名策略: 生产 `app.example.com`, 预览 `*.preview.example.com`

## 备份、回滚与监控

- **备份**: 数据库每日自动备份 + 保留期(≥7 天), 恢复演练过一次
- **回滚**: 部署平台保留历史版本, 一键回滚; 数据库回滚按迁移策略执行
- **监控**: 错误追踪(Sentry 等)+ 可用性监控(探活)+ 关键业务指标
- **日志**: 结构化日志集中收集, 保留期与脱敏策略明确

## 上线后必做

1. 全站走查核心流程(冒烟测试)
2. 检查 HTTPS/证书、安全头、环境变量生效
3. 观察 24 小时: 错误率、性能指标、资源占用
4. 记录发布日志(版本、变更、时间)

## 完成门禁

- [ ] 一键部署脚本/流水线可用且演示通过
- [ ] HTTPS 生效, 安全头配置正确
- [ ] 健康检查与告警配置
- [ ] 备份与回滚演练完成
- [ ] 与 fs-docs 衔接: README 含部署说明
