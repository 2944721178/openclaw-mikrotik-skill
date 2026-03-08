#!/usr/bin/env python3
"""查看 Docker 容器存储位置"""
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

print("🔍 查询 Docker 容器存储位置...\n")

# 1. 容器配置
print("📦 容器配置:")
config = api.run_command('/container/config/print')
for c in config:
    print(f"   镜像仓库：{c.get('registry-url', 'N/A')}")
    print(f"   layer-dir: {c.get('layer-dir', '(默认)')}")
    print(f"   tmpdir: {c.get('tmpdir', '(默认)')}")
    print(f"   内存使用：{int(c.get('memory-current', 0))/1024/1024:.1f}MB")
    print(f"   内存限制：{c.get('memory-high', 'unlimited')}")

# 2. 容器详情
print("\n📋 容器存储路径:")
containers = api.run_command('/container/print')
for c in containers:
    name = c.get('name', 'N/A')
    root_dir = c.get('root-dir', '(默认)')
    layer_dir = c.get('layer-dir', '(默认)')
    mount = c.get('mount', '')
    print(f"\n   📌 {name}")
    print(f"      root-dir: {root_dir}")
    print(f"      layer-dir: {layer_dir}")
    if mount:
        print(f"      挂载：{mount}")

# 3. 查看 USB/存储设备
print("\n💾 存储设备:")
disks = api.run_command('/disk/print')
for d in disks:
    name = d.get('name', 'N/A')
    type_ = d.get('type', 'N/A')
    total = d.get('total-sectors', 'N/A')
    print(f"   {name} ({type_}): {total} 扇区")

# 4. 查看文件系统
print("\n📁 文件系统:")
filesystems = api.run_command('/file/print')
for f in filesystems[:20]:
    name = f.get('name', 'N/A')
    type_ = f.get('type', 'N/A')
    size = f.get('size', '0')
    print(f"   {name} ({type_}) - {size} 字节")

api.disconnect()
print("\n✅ 完成")
