#!/usr/bin/env python3
"""清理路由器存储空间"""
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

print("🧹 开始清理路由器存储空间...\n")

# 1. 查看当前存储使用
print("📊 当前存储使用:")
disks = api.run_command('/disk/print')
for d in disks:
    name = d.get('name', 'N/A')
    total = d.get('total-sectors', 0)
    free = d.get('free-sectors', 0)
    if total and free:
        used = total - free
        percent = (used / total) * 100
        print(f"   {name}: 已用 {percent:.1f}%")

# 2. 列出所有文件
print("\n📁 文件系统内容:")
files = api.run_command('/file/print')
print(f"   总文件数：{len(files)}")

# 3. 查找旧日志和备份
to_delete = []
for f in files:
    name = f.get('name', '')
    type_ = f.get('type', '')
    
    # 旧备份文件 (保留最近的)
    if '.backup' in name and '2025' in name:
        to_delete.append(('旧备份', name))
    
    # 旧日志
    if name.endswith('.txt') and 'log' in name.lower():
        to_delete.append(('日志文件', name))

print("\n🗑️  可清理的文件:")
if to_delete:
    for reason, name in to_delete:
        print(f"   [{reason}] {name}")
else:
    print("   (没有发现可清理的文件)")

# 4. 清理旧备份 (2025 年的)
print("\n🔧 执行清理...")
deleted_count = 0
for reason, name in to_delete:
    if reason == '旧备份':
        print(f"   删除：{name}")
        result = api.run_command(f'/file/remove numbers="{name}"')
        if result or result == []:
            deleted_count += 1
            print(f"      ✅ 已删除")
        else:
            print(f"      ❌ 失败")

# 5. 查看清理后的状态
print("\n📊 清理后存储使用:")
files_after = api.run_command('/file/print')
print(f"   剩余文件数：{len(files_after)}")

api.disconnect()
print(f"\n✅ 清理完成！共删除 {deleted_count} 个文件")
