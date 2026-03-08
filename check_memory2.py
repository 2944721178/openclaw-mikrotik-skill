#!/usr/bin/env python3
"""查看 RouterOS 内存使用详情"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/skills/mikrotik/mikrotik-api')
from client import MikroTikAPI
import json

host = '10.254.254.1'
username = 'admin'
password = '90-=op[]'

api = MikroTikAPI(host, username, password, port=8728)
if not api.connect():
    print("❌ 连接失败")
    sys.exit(1)

if not api.login():
    print("❌ 登录失败")
    api.disconnect()
    sys.exit(1)

print("🔍 详细查询内存使用情况...\n")

# 1. 系统资源
print("📊 系统资源:")
resource = api.run_command('/system/resource/print')
for r in resource:
    print(f"   内存使用：{r.get('memory-usage', 'N/A')}%")
    print(f"   总内存：{r.get('total-memory', 'N/A')}")
    print(f"   已用内存：{r.get('used-memory', 'N/A')}")
    print(f"   CPU 负载：{r.get('cpu', 'N/A')}%")
    print(f"   运行时间：{r.get('uptime', 'N/A')}")

# 2. 容器详情
print("\n📦 容器详情:")
containers = api.run_command('/container/print')
print(f"   总容器数：{len(containers)}")
for c in containers:
    name = c.get('name', 'N/A')
    stopped = c.get('stopped', 'false')
    status = "⏸️ 已停止" if stopped == 'true' else "🟢 运行中"
    image = c.get('remote-image', 'N/A')[:50]
    print(f"\n   {status} {name}")
    print(f"      镜像：{image}")
    print(f"      接口：{c.get('interface', 'N/A')}")
    print(f"      CPU 使用：{c.get('cpu-usage', '0')}%")
    print(f"      内存限制：{c.get('memory-high', 'unlimited')}")

# 3. 查看桥接和无线
print("\n📡 网络接口:")
interfaces = api.run_command('/interface/print')
lan_count = sum(1 for i in interfaces if 'lan' in i.get('name', '').lower() and i.get('running') == 'true')
wifi_count = sum(1 for i in interfaces if 'wifi' in i.get('name', '').lower() and i.get('running') == 'true')
print(f"   LAN 口活跃：{lan_count}")
print(f"   WiFi 活跃：{wifi_count}")

# 4. 查看路由
print("\n🛤️ 路由表:")
routes = api.run_command('/ip/route/print')
for r in routes[:5]:
    dst = r.get('dst-address', 'N/A')
    gw = r.get('gateway', 'N/A')
    dist = r.get('distance', 'N/A')
    print(f"   {dst} via {gw} (distance: {dist})")

# 5. 查看 ARP 表 (连接的设备)
print("\n📱 连接的设备 (ARP):")
arp = api.run_command('/ip/arp/print')
print(f"   已连接设备数：{len(arp)}")
if arp:
    for a in arp[:10]:
        ip = a.get('address', 'N/A')
        mac = a.get('mac-address', 'N/A')
        iface = a.get('interface', 'N/A')
        print(f"     - {ip} ({mac}) on {iface}")

api.disconnect()
print("\n✅ 完成")
