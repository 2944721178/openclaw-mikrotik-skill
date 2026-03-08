#!/usr/bin/env python3
"""查看 RouterOS 内存使用情况"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/skills/mikrotik/mikrotik-api')
from client import MikroTikAPI

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

print("🔍 查询内存使用情况...\n")

# 1. 查看运行的容器
print("📦 运行中的容器:")
containers = api.run_command('/container/print')
running = [c for c in containers if c.get('stopped') != 'true']
print(f"   总容器数：{len(containers)}")
print(f"   运行中：{len(running)}")
for c in containers:
    status = "🟢" if c.get('stopped') != 'true' else "⏸️"
    print(f"   {status} {c.get('name', 'N/A')}")

# 2. 查看进程
print("\n💻 系统进程 (按 CPU 排序):")
processes = api.run_command('/process/print')
if processes:
    # 按 CPU 使用率排序
    processes_sorted = sorted(processes, key=lambda x: float(x.get('cpu', 0) or 0), reverse=True)[:10]
    for p in processes_sorted:
        cpu = p.get('cpu', '0')
        mem = p.get('memory', 'N/A')
        name = p.get('name', 'N/A')
        print(f"   CPU: {cpu}% | MEM: {mem}KB | {name}")

# 3. 查看磁盘使用
print("\n💾 磁盘使用:")
disks = api.run_command('/disk/print')
for d in disks:
    name = d.get('name', 'N/A')
    total = d.get('total', 'N/A')
    used = d.get('used', 'N/A')
    free = d.get('free', 'N/A')
    print(f"   {name}: 总计 {total} | 已用 {used} | 剩余 {free}")

# 4. 查看 USB 存储
print("\n🔌 USB 存储:")
usb = api.run_command('/store/print')
for s in usb:
    name = s.get('name', 'N/A')
    type_ = s.get('type', 'N/A')
    total = s.get('total', 'N/A')
    used = s.get('used', 'N/A')
    print(f"   {name} ({type_}): 总计 {total} | 已用 {used}")

api.disconnect()
print("\n✅ 完成")
