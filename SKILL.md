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

在 `TOOLS.md` 中添加 MikroTik 设备信息：

```markdown
### MikroTik 设备

- **office**: 10.0.5.4, admin, 空密码
- **home**: 192.168.88.1, admin, password=yourpassword
```

## 用法

### 查看设备状态

```
查看 mikrotik 设备状态
mikrotik 10.0.5.4 状态
检查路由器运行情况
```

### 查看防火墙

```
查看防火墙规则
mikrotik 防火墙配置
显示 NAT 规则
```

### 查看网络接口

```
查看网络接口
mikrotik 接口列表
显示 IP 地址配置
```

### 执行命令

```
在 mikrotik 上执行 /system/resource/print
运行 routeros 命令 /ip/address/print
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

## 作者

虾哥 🤖
