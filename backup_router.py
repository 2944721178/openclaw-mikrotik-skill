#!/usr/bin/env python3
"""备份 RouterOS 设备配置"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/skills/mikrotik/mikrotik-api')
from client import MikroTikAPI
from datetime import datetime

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

# 生成备份文件名
timestamp = datetime.now().strftime('%Y%m%d-%H%M')
backup_name = f'home-ros-backup-{timestamp}'

print(f"💾 开始备份路由器配置...\n")
print(f"📝 备份文件名：{backup_name}\n")

# 执行备份
print("🔧 执行系统备份...")
result = api.run_command(f'/system/backup/save name={backup_name}')
print(f"   备份结果：{result}")

# 查看备份文件
print("\n📋 查看备份文件...")
files = api.run_command('/file/print')
backup_files = [f for f in files if backup_name in f.get('name', '')]

if backup_files:
    for f in backup_files:
        name = f.get('name', 'N/A')
        size = f.get('size', '0')
        type_ = f.get('type', 'N/A')
        print(f"   ✅ 备份成功!")
        print(f"      文件名：{name}")
        print(f"      类型：{type_}")
        print(f"      大小：{int(size)/1024:.2f} KB")
else:
    # 尝试查找 .backup 文件
    backup_files = [f for f in files if f.get('name', '').endswith('.backup')]
    if backup_files:
        # 找最新的备份
        latest = max(backup_files, key=lambda x: x.get('name', ''))
        print(f"   ✅ 备份成功!")
        print(f"      文件名：{latest.get('name')}")
        print(f"      大小：{int(latest.get('size', 0))/1024:.2f} KB")

# 列出最近的备份
print("\n📦 最近的备份文件:")
all_backups = sorted([f for f in files if f.get('name', '').endswith('.backup')], 
                     key=lambda x: x.get('name', ''), reverse=True)[:5]
for i, b in enumerate(all_backups, 1):
    name = b.get('name', 'N/A')
    size = int(b.get('size', 0))/1024
    print(f"   {i}. {name} ({size:.2f} KB)")

api.disconnect()
print("\n✅ 备份完成!")
