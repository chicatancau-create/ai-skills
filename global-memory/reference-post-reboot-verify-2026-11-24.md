# 重启后复核闭环（2026-11-24）

- 开机任务 EmulatorCacheMigrate 于 17:07–17:10 重启时执行成功并自删：`.android` 4.60G / `Android` 4.16G / `Huawei` 5.67G（鸿蒙模拟器）/ `CapCut` 0.14G，共 14.57 GB（小于日间估算 17.9G = 应用退出后缓存收缩）。SYSTEM 开机任务先于用户自启服务，抢赢文件锁（CapCutService 自启时迁移已完成）。
- `.android` 已补进 `D:\DSH-Guard\migrate_guard.py` 的 ALL 巡检列表；守护覆盖 home 26 + local 15 + roaming 13 = **54 个联接**，复跑退出 0、残留零。
- DSH 重启时已自动更新到 0.2.3-alpha.2（与 pending 同版）；冗余安装缓存 574.9 MB 移至 `D:\AI-Tool-State\disk-audit\updater-cache-bak\`（可回滚）——更新器目录空了不是缺更新。
- C 盘剩余 173.2 GB（今日 114.2 → +59.0 GB）。自启应用（QQ/微信/PowerToys/IDM/wetype）与 CapCutService 均经联接正常运行。
