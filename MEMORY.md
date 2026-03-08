# MEMORY.md - 长期记忆

_最后更新：2026-03-06_

---

## 👤 用户信息

- **称呼**: 无可奉告
- **职业**: 网络工程师
- **时区**: Asia/Shanghai (UTC+8)
- **风格偏好**: 直接、简洁、幽默

---

## 🖥️ 工作环境

### 本地设备 (LattePanda 3 Delta)
- **型号**: LattePanda 3 Delta
- **CPU**: Intel Celeron N5105 @ 2.00GHz (4 核)
- **内存**: 7.5GB
- **存储**: 58.2GB eMMC (mmcblk1)
- **IP**: 10.254.252.254/24
- **系统**: Ubuntu 24.04.2 LTS (Kernel 6.8.0-101)

### 网络设备
| 设备 | IP | 账号 | 密码 |
|------|-----|------|------|
| **ap** (MikroTik) | 10.254.252.3 | admin | 空 |
| **office** (MikroTik) | 10.254.252.1 | admin | 空 |
| **firewall** (FortiGate-60D) | 10.254.254.250 | admin | 90-=op[] |

### 本地网络
- **LattePanda**: 10.254.252.254/24 (enp1s0)
- **网段**: 10.254.252.0/24 (办公网)
- **网关**: 10.254.252.1 (office MikroTik)

### 远程服务器
- **NVIDIA DGX**: 10.0.15.204 (itadmin)

### IoT 协处理器
- **芯片**: ATmega32U4 (Arduino Leonardo 兼容)
- **设备路径**: `/dev/ttyACM0`
- **工具**: arduino-cli v1.4.1
- **已测试**: 板载 LED (Pin 13) 控制正常

---

## 📧 邮件配置

- **客户端**: himalaya v1.2.0
- **邮箱**: notice@wukefenggao.top (阿里云企业邮箱)
- **配置路径**: `~/.config/himalaya/config.toml`

---

## 🛠️ 已安装工具

| 工具 | 版本 | 用途 |
|------|------|------|
| arduino-cli | v1.4.1 | IoT 开发 |
| himalaya | v1.2.0 | 邮件客户端 |

---

## 📝 重要项目记录

### 1. MikroTik 设备配置 (2026-03-06)
- 已完成 ap 和 office 两台设备的 API 连接配置
- 设备信息已记录在 TOOLS.md

### 2. LattePanda IoT 项目 (2026-03-05)
- ✅ LED 控制测试完成 (Pin 13 红色 LED)
- ✅ USB 通信正常 (arduino-cli 上传)
- 引脚定义文档已整理

### 3. fortigate-monitor 技能开发 (2026-03-06)
- GitHub 仓库：Nyx1197/fortigate-monitor
- 用途：Fortigate 防火墙监控 OpenClaw 技能
- 状态：代码审查完成，需改进安全性和错误处理

### 4. FortiGate 技能 v6.0 支持 (2026-03-07) ✅
- 为 fortigate skill 添加 v6.0 版本 API 兼容支持
- 修改文件：
  - `commands.py` - 添加版本检测、v6 API 回退逻辑
  - `handler.py` - 更新格式化函数兼容 v6 响应格式
  - `SKILL.md` - 更新版本文档说明
- v6.x 限制：CPU/内存监控 API 不可用，会话统计需 CLI
- 已测试设备：FortiGate-60D v6.0.18 (10.254.254.250)

---

## ⚠️ 已完成/取消事项

- ~~Bitwarden 自部署集成~~ (用户取消)
- ~~LattePanda IoT 项目开发~~ (LED 测试完成，暂无后续需求)

---

## 💡 经验教训

1. **Outlook 漏收邮件** - 网络波动 + IMAP 同步问题常见，优先检查文件夹订阅和 OST 缓存
2. **GitHub 访问** - 国内网络环境下，git clone 可能失败，改用 API 或 raw 链接
3. **天气 API** - Open-Meteo 可用，wttr.in 偶尔超时

---

## 🔐 安全注意事项

- 敏感信息（密码、Token）不直接存储在代码中
- MikroTik 设备当前使用空密码，建议尽快设置
- 定期审查 MEMORY.md，移除过期敏感信息

---

## 📅 待办跟踪

- [ ] 网络设备配置文件整理
- [ ] 常用网络命令模板
- [ ] 监控脚本模板
- [ ] 文档存储结构规划

---

_此文件定期从 daily notes 中提炼更新_
