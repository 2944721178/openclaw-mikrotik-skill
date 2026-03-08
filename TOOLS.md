# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 网络工程师工作配置（2026-03-05 更新）

### 设备信息
- **系统**: Ubuntu 24.04.2 LTS (Noble Numbat) - Kernel 6.8.0-101
- **主机名**: lattepanda
- **CPU**: Intel Celeron N5105
- **内存**: 7.5GB
- **存储**: 58.2GB eMMC (mmcblk1)
- **有线网卡**: Intel I211 Gigabit Network Connection (enp1s0)
- **无线网卡**: Intel Wi-Fi 6 AX201 160MHz
- **IP 地址**: 10.254.252.254/24

### 网络相关工具
- **SSH**: 已配置，支持多个连接
- **网络监控**: 支持 ss/netstat 命令
- **文件传输**: 无图形界面，需要命令行工具

### 限制
- 无图形浏览器界面
- 无法截图网页内容
- **天气 API**: ✅ Open-Meteo 可用（wttr.in 超时）
- **网络状态**: ✅ 国内网络正常，部分国外服务不稳定

### MikroTik 设备（2026-03-06 配置）
- **ap**: 10.254.252.3, admin, 空密码
- **office**: 10.254.252.1, admin, 空密码

### FortiGate 设备（2026-03-07 配置）
- **firewall**: 10.254.254.250, admin, 90-=op[]
  - 型号：FortiGate-60D
  - 版本：v6.0.18
  - 序列号：FGT60D4Q16069776

### 待配置项目
- [ ] 网络设备配置文件
- [ ] 常用网络命令模板
- [ ] 监控脚本模板
- [ ] 文档存储结构

---

## 重要配置记录 (2026-03-03)

### 本地设备 (LattePanda 3 Delta)
- **型号**: LattePanda 3 Delta
- **CPU**: Intel Celeron N5105 @ 2.00GHz (4 核)
- **内存**: 7.5GB
- **存储**: 58.2GB eMMC (mmcblk1)
- **有线网卡**: Intel I211 Gigabit Network Connection
- **无线网卡**: Intel Wi-Fi 6 AX201 160MHz
- **IP**: 10.0.15.254/24
- **时区**: Asia/Shanghai (CST/UTC+8)
- **IoT 协处理器**: ATmega32U4 (Arduino Leonardo) - `/dev/ttyACM0`

### 已安装工具
- **arduino-cli**: v1.4.1
  - 路径：`/root/.openclaw/workspace/bin/arduino-cli`
  - 核心：arduino:avr@1.8.7
- **himalaya**: v1.2.0 (邮件客户端)
  - 配置：`~/.config/himalaya/config.toml`
  - 邮箱：notice@wukefenggao.top (阿里云企业邮箱)

### 已完成事项 (2026-03-05)
- ~~Bitwarden 自部署集成~~ (用户取消)
- ~~LattePanda IoT 项目开发~~ (LED 控制测试完成)

---

## LattePanda 3 Delta - ATmega32U4 协处理器引脚定义

### 基本信息
- **芯片型号**: ATmega32U4 (Arduino Leonardo 兼容)
- **设备路径**: `/dev/ttyACM0`
- **板载 LED**: Pin 13 (红色，已测试确认)
- **通信接口**: USB Serial (CDC ACM)

### GPIO 引脚
```
数字引脚: D0-D13
- D0  (RX)  : UART 接收
- D1  (TX)  : UART 发送
- D2        : 外部中断
- D3        : PWM 输出
- D4        : 通用 IO
- D5        : PWM 输出
- D6        : PWM 输出
- D7        : 通用 IO
- D8        : 通用 IO
- D9        : PWM 输出
- D10 (SS)  : SPI 片选
- D11 (MOSI): SPI 数据输出
- D12 (MISO): SPI 数据输入
- D13 (SCK) : SPI 时钟 + 板载 LED

模拟引脚: A0-A5
- A0-A5     : 10 位 ADC 输入 (0-5V)
- A6-A7     : 仅 ADC，无数字功能
```

### 通信接口
- **UART**: D0(RX) / D1(TX)
- **SPI**: D10(SS) / D11(MOSI) / D12(MISO) / D13(SCK)
- **I2C**: SDA(D2) / SCL(D3)
- **TWI**: 与 I2C 兼容

### 特殊功能引脚
- **风扇控制**: 三线风扇（具体引脚待确认）
- **5V 输出**: 多个引脚可提供 5V/400mA
- **3.3V 输出**: 50mA 最大

### 已测试功能
- ✅ LED 控制 (Pin 13) - 常亮/闪烁/关闭
- ✅ USB 通信 - arduino-cli 正常上传
- ✅ 板载 LED 颜色：红色

### 注意事项
- 引脚电压：5V 逻辑电平
- 最大电流：单引脚 40mA，总电流不超过 200mA
- 静电防护：接触前需释放静电

---

Add whatever helps you do your job. This is your cheat sheet.
