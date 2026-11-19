---
name: reference-qemu-cloud-init-windows
description: 在本机用 QEMU + Ubuntu cloud image 跑 Docker/K3s 的可用配方与坑（无 WSL/不提权），含 cloud-init 被禁用、串口 TCP 一次性会话、guest 代理、镜像导入、rollout/undo、两节点 K3s 与 3 容器 RabbitMQ 集群
metadata:
  type: reference
---

2026-11-08 在本机（无 WSL、非提权）用 QEMU 跑出真实 Docker/Compose/K3s 证据的路径：

- **安装**：`winget install --id SoftwareFreedomConservancy.QEMU -e --silent` 可装到
  `C:\Program Files\qemu`（无需手动 UAC）；`qemu-system-x86_64.exe` / `qemu-img.exe` 直接用。
- **镜像/磁盘**：Ubuntu 24.04 minimal cloud image 放 `D:\QEMU`；`qemu-img create -f qcow2 -F qcow2
  -b ubuntu.img k8s-lab.qcow2 12G` 生成覆盖盘，失败后删覆盖盘重来，不动基础镜像。
- **cloud-init seed**：用 pycdlib 生成卷标 `cidata` 的 ISO，需 `rock_ridge='1.09'`；ISO9660 文件名只能
  A-Z0-9_，`user-data` 写成 `/USERDATA.;1` + `rr_name='user-data'`；NoCloud 从 `/dev/sr0` 读取。
- **YAML 陷阱**：runcmd 里用多行 `printf '...\n...'` 写文件会破坏 YAML（报 `Invalid format at line ...`，
  cloud-init 变成 empty config，串口只剩登录提示）。要写多行配置一律放 `write_files`。
- **cloud-init 可能整体被禁用**：复用 cloud image 时 `cloud-init status --long` 可能回
  `disabled-by-generator`（即使换了 instance-id），此时 seed 的 runcmd 不会执行，串口只剩登录提示。
  先登录确认状态，别把“runcmd 没输出”当成 YAML 语法问题。
- **SSH 可能只允许 publickey**：`ssh_pwauth: true` 不保证 sshd 开密码；本机实测只回
  `allowed types: ['publickey']`。最省事的交互通路是串口 TCP：
  `-serial tcp:127.0.0.1:4444,server,nowait`，用 Node `net` 连上后先发一个换行触发登录提示，
  再 `ubuntu/ubuntu` 登录、`sudo -s`；不需要 sshpass/paramiko。
- **Traefik Ingress**：K3s 默认 Traefik Helm job 可能先显示 Error 但 chart 已 `deployed`；
  等 `traefik-*` 与 `svclb-traefik-*` Running 后，用 `curl -H 'Host: web.local' http://127.0.0.1/`
  验证，不要只 curl ClusterIP。2026-11-08 单节点 `web.local -> nginx` 已验证。
- **guest 出网**：QEMU user net 的 host 是 `10.0.2.2`；Docker Hub 被重置时给 dockerd 配
  `HTTP_PROXY/HTTPS_PROXY=http://10.0.2.2:7897`（host 的 Clash）；**K3s 安装脚本也要**
  `curl … | HTTPS_PROXY=http://10.0.2.2:7897 sh -`，否则 GitHub 下载随机 `Recv failure`/`Download failed`。
- **TCG 慢**：镜像拉取/容器启动按分钟计；rollout 超时不要立刻判失败，先看 Pod 状态与后续轮次。
- **K3s 本地镜像**：`docker save nginx:1.27-alpine -o /tmp/nginx.tar` 后
  `k3s ctr -n k8s.io images import --platform linux/amd64 /tmp/nginx.tar`；单平台导入后 Pod 才能快速 Running。
- **滚动/回滚**：同镜像 `kubectl rollout restart deployment/web` 会产生 revision，随后
  `kubectl rollout undo deployment/web` 才能真正成功；直接 set 同一个镜像不会产生 history。
- **启动/日志**：`-accel tcg,thread=multi -m 3072 -smp 2 -drive file=…,if=virtio -drive file=seed.iso,media=cdrom
  -netdev user,id=n0 -device virtio-net-pci,netdev=n0 -nographic -no-reboot`；串口即证据，脚本末尾 `poweroff`；
  QEMU 任务停止后可能仍占覆盖盘，删盘前先确认进程退出。
- **边界**：TCG 软件模拟；2026-11-08 已做到两节点（server + agent 容器，同一 VM）与单节点 Ingress，但仍无多机/HA/公网；证据只能写“隔离 VM 演练”，不能写成生产集群。

## 多节点/多容器（2026-11-08）

- **串口 TCP 是一次性会话**：`-serial tcp:127.0.0.1:4444,server,nowait` 在客户端断开后监听可能消失，
  后续连接只回换行、收不到提示符。要把一组命令放进**同一个 Node 会话**；否则重启 QEMU。
  登录循环别用整个缓冲区判断 `login:`（登录后旧文本还在，会重复发 username），用 `sentUser/sentPass` 标志。
- **K3s agent 容器**：`docker run -d --privileged -v k3s-agent-data:/var/lib/rancher/k3s \
  -e K3S_URL=https://172.17.0.1:6443 -e K3S_TOKEN=… rancher/k3s:v1.37.2-k3s1 agent --node-name agent-1`。
  容器内不能走 `10.0.2.15`，要用 Docker 网关 `172.17.0.1`；server 访问 agent 的 `172.17.0.2:10250`。
- **agent 缺 pause 镜像**：Pod 会卡 `ContainerCreating`。从 server `k3s ctr images export /tmp/pause.tar
  docker.io/rancher/mirrored-pause:3.10.2`，`docker cp` 进 agent，再
  `docker exec k3s-agent /bin/ctr -n k8s.io images import /tmp/pause.tar`；Pod 镜像直接用
  `docker.io/rancher/mirrored-pause:3.10.2`（本地已有），不要用 `registry.k8s.io/pause` 触发外网拉取。
- **RabbitMQ 3 容器集群**：同一 docker network、固定 `--hostname rmqN`、相同 `RABBITMQ_ERLANG_COOKIE`；
  `rabbitmqctl stop_app/reset/join_cluster rabbit@rmq1/start_app`。VM 重启后容器会 start 但 app 不一定 running，
  要再 `start_app`；`docker update --restart=always rmq1 rmq2 rmq3` 保持容器。
- **分区演练**：`docker network disconnect rmq-net rmq3` 后 `cluster_status` 只剩 2 个 Running Nodes，
  `docker network connect` 后恢复 3 个；这是容器网络分区，不是多机网络故障。

## WHPX：RabbitMQ 健康检查能否通过的关键（2026-11-08）

- 本机 QEMU 支持 **WHPX**：`qemu-system-x86_64 -accel help` 会列出 `whpx`。
- TCG（默认软件模拟）下 Erlang/RabbitMQ 极慢：`rabbitmq-diagnostics -q ping` 单次超过 2 分钟，
  compose 的 `timeout: 5s` 健康检查连续失败（FailingStreak 14+），`app` 永远停在 Created。
- 改用 `-accel whpx -m 4096 -smp 4` 后，P03 的 db/mq 立即 healthy，app 正常启动；同一 qcow2 的镜像、
  构建缓存与数据都保留，重启后直接 `docker compose up -d` 即可。
- 关 VM 前先 `docker stop` 所有容器，再串口 `poweroff`；别在构建中途断电。
- 结论：在这台机器上做 Docker/RabbitMQ 证据，**优先 WHPX**，不要拿 TCG 的超时当应用故障。

Related: [[reference-local-test-services]], [[reference-git-push-needs-local-proxy]]
