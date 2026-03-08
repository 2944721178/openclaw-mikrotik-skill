#!/usr/bin/env python3
"""FortiGate 状态查询脚本"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/skills/fortigate/fortigate-api')
from client import FortiGateAPI
import requests

host = '10.254.254.250'
username = 'admin'
password = '90-=op[]'

api = FortiGateAPI(host, username, password, verify_ssl=False)

print("🔌 正在连接 FortiGate 防火墙...")
if not api.connect():
    print("❌ 连接失败")
    sys.exit(1)

print("✅ 连接成功！\n")

# 获取系统信息
print("📊 获取系统信息...")
try:
    # 系统信息
    status = api.api_get('/api/v2/monitor/system/status')
    if status:
        result = status.get('results', {})
        print("\n🛡️  FortiGate 设备状态")
        print("=" * 60)
        print(f"  主机名：{result.get('hostname', 'N/A')}")
        print(f"  序列号：{result.get('serial', 'N/A')}")
        print(f"  型号：{result.get('model', 'N/A')}")
        print(f"  版本：{result.get('version', 'N/A')}")
        print(f"  运行时间：{result.get('uptime', 'N/A')}")
        print(f"  CPU 使用率：{result.get('cpu_current', 'N/A')}%")
        print(f"  内存使用率：{result.get('memory_current', 'N/A')}%")
        print("=" * 60)
except Exception as e:
    print(f"⚠️ 获取状态失败：{e}")

# 获取接口信息
print("\n📡 获取接口信息...")
try:
    iface = api.api_get('/api/v2/monitor/system/interface')
    if iface and 'results' in iface:
        print("\n🔌 网络接口")
        print("=" * 60)
        for intf in iface['results']:
            name = intf.get('name', 'N/A')
            status = intf.get('status', 'N/A')
            ip = intf.get('ip', 'N/A')
            print(f"  {'✅' if status == 'up' else '❌'} {name}")
            print(f"      状态：{status} | IP: {ip}")
        print("=" * 60)
except Exception as e:
    print(f"⚠️ 获取接口失败：{e}")

# 获取会话统计
print("\n📊 获取会话统计...")
try:
    sessions = api.api_get('/api/v2/monitor/firewall/session')
    if sessions:
        result = sessions.get('results', {})
        print("\n📈 会话统计")
        print("=" * 60)
        print(f"  活动会话：{result.get('count', 'N/A')}")
        print(f"  峰值会话：{result.get('peak', 'N/A')}")
        print(f"  新建速率：{result.get('rate', 'N/A')} 会话/秒")
        print("=" * 60)
except Exception as e:
    print(f"⚠️ 获取会话失败：{e}")

api.disconnect()
print("\n✅ 查询完成")
