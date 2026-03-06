---
name: mikrotik
description: 通过 API 连接和管理 MikroTik RouterOS 设备。支持查看设备状态、防火墙规则、网络配置，执行自定义 RouterOS 命令。
---

# MikroTik RouterOS Skill

通过 API 连接和管理 MikroTik RouterOS 设备。

## 功能

- 查看设备状态（系统信息、CPU、内存、存储）
- 查看防火墙规则（filter、NAT、mangle）
- 查看网络配置（接口、IP 地址、路由、DNS）
- 执行自定义 RouterOS 命令
- 支持多设备连接

## 配置

### 方式一：TOOLS.md（推荐）

在 `~/.openclaw/workspace/TOOLS.md` 中添加设备信息：

```markdown
### MikroTik 设备

- **office**: 192.168.1.1, admin, 空密码
- **home**: 192.168.88.1, admin, yourpassword
- **branch**: 192.168.2.1, admin, complex_password_123
```

**密码格式说明**：
- 空密码：写 `空密码`、`无密码`、`none` 或留空
- 有密码：直接写密码字符串

### 方式二：环境变量

```bash
export MIKROTIK_HOST=192.168.1.1
export MIKROTIK_USER=admin
export MIKROTIK_PASS=        # 空密码
# 或
export MIKROTIK_PASS=yourpassword  # 有密码
```

**优先级**：环境变量 > TOOLS.md > 默认值

## 用法

### 📊 设备状态

```
查看 mikrotik 设备状态
查看 office mikrotik 状态
检查路由器运行情况
```

### 🔥 防火墙

```
查看防火墙规则
mikrotik 防火墙配置
显示 NAT 规则
查看 office 防火墙
```

### 🔌 网络接口

```
查看网络接口
mikrotik 接口列表
显示 IP 地址配置
```

### 📋 DHCP

```
查看 DHCP 配置
显示 DHCP 租约
mikrotik dhcp
```

### 📡 ARP 表

```
查看 ARP 表
mikrotik arp
显示 ARP 缓存
```

### 🔐 WireGuard

```
查看 WireGuard 配置
mikrotik wireguard
显示 VPN 对等体
```

### 👤 用户

```
查看用户配置
mikrotik users
显示 PPP 用户
```

### 📝 日志

```
查看系统日志
mikrotik logs
显示最近日志
```

### 🔧 服务

```
查看系统服务
mikrotik services
显示 API/SSH 端口
```

### 📈 流量统计

```
查看接口流量
mikrotik traffic
显示流量统计
```

### 🔌 接口详情

```
查看接口详细信息
mikrotik interface detail
查看 ether1 接口详情
```

### 🏷️ VLAN

```
查看 VLAN 配置
mikrotik vlan
显示 VLAN 列表
```

### 🌉 桥接

```
查看桥接配置
mikrotik bridge
显示桥接端口
```

### 📊 队列/带宽

```
查看队列配置
mikrotik queue
显示带宽限制
查看限速规则
```

### 🌐 路由

```
查看路由配置
mikrotik route
显示 OSPF 状态
查看 BGP 对等体
```

### 🌡️ 系统健康

```
查看系统健康
mikrotik health
显示温度/电压/风扇
```

### 📅 计划任务

```
查看计划任务
mikrotik scheduler
显示定时任务
```

### 📡 邻居设备

```
查看邻居设备
mikrotik neighbors
显示网络设备发现
```

### 🔗 活动连接

```
查看活动连接
mikrotik connections
显示连接统计
```

### 🏓 Ping 测试

```
ping 8.8.8.8
mikrotik ping 1.1.1.1
```

### 📡 网络扫描

```
扫描局域网
mikrotik scan
扫描 192.168.1.0/24
查找 MikroTik 设备
```

### 🎯 自定义命令

```
在 mikrotik 上执行 /system/resource/print
运行 routeros 命令 /ip/address/print
在 office 设备上执行 /interface/print
```

### 🖥️ 多设备支持

如果配置了多个设备，可以在命令中指定设备名称：

```
查看机房 mikrotik 状态
查看 home 防火墙规则
```

## 依赖

- Python 3.6+
- 设备 API 已启用（默认端口 8728）
- 网络可达

## 文件结构

```
skills/mikrotik/
├── SKILL.md           # 技能说明（本文件）
├── handler.py         # 命令处理器
└── mikrotik-api/      # API 客户端库（复用现有）
    ├── __init__.py
    ├── client.py
    ├── commands.py
    └── cli.py
```

## 示例响应

```
📡 MikroTik RouterOS 设备状态
==================================================
  设备名：OFFICE
  版本：7.21.2 (stable)
  运行时间：1w2d9h9m39s
  CPU: MIPS 1004Kc V2.15 @ 880MHz
  CPU 负载：1%
  内存：61.6MB / 256.0MB
  存储：3.6MB / 16.0MB
==================================================
```

## 注意事项

1. 确保 RouterOS 的 API 服务已启用（`/ip/service/print` 查看）
2. 默认端口 8728，SSL 端口 8729
3. 空密码设备注意安全风险
4. 部分命令需要管理员权限
5. 响应解析已优化，支持多条目返回（接口列表、路由表、ARP 表等）

## 更新日志

### v1.6.0 (2026-03-06)
- 🆕 新增网络扫描功能（类似 Winbox）
- 🆕 支持广播报文监听发现设备
- 🆕 支持邻居发现、ARP 表、网关多来源扫描
- 🆕 显示设备 MAC、IP、型号、版本信息
- 🆕 智能去重（基于 MAC 地址）

### v1.5.0 (2026-03-06) [已推送]
- 🆕 新增高级路由功能查看（OSPF、BGP）
- 🆕 新增系统健康监控（温度、电压、风扇）
- 🆕 新增计划任务查看
- 🆕 新增邻居设备发现
- 🆕 新增活动连接统计
- 🆕 新增 Ping 测试功能
- 🆕 智能温度告警（>70°C🔥, >50°C⚠️）

### v1.4.0 (2026-03-06)
- 🆕 新增队列/带宽限制查看（Simple Queues）
- 🆕 新增队列树配置查看
- 🆕 新增队列类型显示
- 🆕 带宽单位自动转换（Mbps/Gbps）

### v1.3.0 (2026-03-06)
- 🆕 新增接口流量统计（接收/发送字节数、包数、错误/丢弃）
- 🆕 新增接口详细信息查看
- 🆕 新增 VLAN 配置查看
- 🆕 新增桥接配置和端口列表
- 🆕 流量单位自动转换（B/KB/MB/GB）

### v1.2.0 (2026-03-06)
- 🆕 新增 DHCP 配置查看（租约、服务器）
- 🆕 新增 ARP 表查看
- 🆕 新增 WireGuard 对等体状态
- 🆕 新增用户配置（系统用户、PPP 用户）
- 🆕 新增系统日志查看
- 🆕 新增系统服务查看（API、SSH、WWW 等）

### v1.1.0 (2026-03-06)
- ✅ 修复凭证配置：支持 TOOLS.md 和环境变量
- ✅ 修复响应解析：完整支持多条目返回
- ✅ 改进连接可靠性：改用非阻塞模式 + select 超时
- ✅ 增强错误提示：友好的配置缺失提示

### v1.0.0 (2026-03-05)
- 初始版本

## 作者

虾哥 🤖
