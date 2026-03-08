#!/usr/bin/env python3
"""FortiGate 状态查询脚本 - 完整版"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/skills/fortigate/fortigate-api')
from client import FortiGateAPI
import json

host = '10.254.254.250'
username = 'admin'
password = '90-=op[]'

api = FortiGateAPI(host, username, password, verify_ssl=False)

print("🔌 正在连接 FortiGate 防火墙...\n")
if not api.connect():
    print("❌ 连接失败")
    sys.exit(1)

print("✅ 连接成功！\n")

# 获取系统状态
status = api.api_get('/api/v2/monitor/system/status')
if status:
    print("🛡️  FortiGate 设备状态")
    print("=" * 60)
    print(f"  序列号：{status.get('serial', 'N/A')}")
    print(f"  型号：FortiGate-60D")
    print(f"  版本：{status.get('version', 'N/A')}")
    print(f"  Build: {status.get('build', 'N/A')}")
    print("=" * 60)

# 获取接口信息
iface = api.api_get('/api/v2/monitor/system/interface')
if iface and 'results' in iface:
    print("\n🔌 网络接口")
    print("=" * 60)
    for name, info in iface['results'].items():
        link_status = 'up' if info.get('link', False) else 'down'
        ip = info.get('ip', 'N/A')
        mask = info.get('mask', 'N/A')
        if ip != 'N/A':
            ip = f"{ip}/{mask}"
        link_icon = '✅' if link_status == 'up' else '❌'
        print(f"  {link_icon} {name}")
        print(f"      状态：{link_status} | IP: {ip}")
        if info.get('tx_packets', 0) > 0 or info.get('rx_packets', 0) > 0:
            tx = info.get('tx_packets', 0)
            rx = info.get('rx_packets', 0)
            print(f"      流量：TX {tx:,} pkts | RX {rx:,} pkts")
    print("=" * 60)

# 获取 CPU/内存资源（从 status 里找）
print("\n📊 系统资源")
print("=" * 60)
# 尝试获取 CPU 使用率
cpu_result = api.api_get('/api/v2/monitor/system/cpu')
if cpu_result and 'results' in cpu_result:
    cpu_info = cpu_result['results']
    if isinstance(cpu_info, dict):
        cpu_usage = cpu_info.get('current', 'N/A')
        print(f"  CPU 使用率：{cpu_usage}%")

# 尝试获取内存使用率  
mem_result = api.api_get('/api/v2/monitor/system/memory')
if mem_result and 'results' in mem_result:
    mem_info = mem_result['results']
    if isinstance(mem_info, dict):
        total = mem_info.get('total', 0)
        used = mem_info.get('used', 0)
        if total > 0:
            usage_percent = round((used / total) * 100, 1)
            print(f"  内存使用率：{usage_percent}% ({used}/{total} MB)")
print("=" * 60)

# 获取会话数
print("\n📈 会话统计")
print("=" * 60)
# 尝试不同的会话 API
for endpoint in ['/api/v2/monitor/firewall/session', '/api/v2/monitor/system/session']:
    sessions = api.api_get(endpoint)
    if sessions and 'results' in sessions:
        result = sessions['results']
        if isinstance(result, dict):
            count = result.get('count', result.get('active', 'N/A'))
            print(f"  活动会话：{count}")
            break
        elif isinstance(result, list):
            print(f"  活动会话：{len(result)}")
            break
else:
    print("  活动会话：N/A (API 不可用)")
print("=" * 60)

# 获取防火墙策略
print("\n🔥 防火墙策略")
print("=" * 60)
policy = api.api_get('/api/v2/cmdb/firewall/policy')
if policy and 'results' in policy:
    policies = policy['results']
    total = len(policies)
    enabled = sum(1 for p in policies if p.get('status') == 'enable')
    disabled = total - enabled
    print(f"  总策略数：{total}")
    print(f"  已启用：{enabled}")
    print(f"  已禁用：{disabled}")
print("=" * 60)

# VPN 状态
print("\n🔐 VPN 状态")
print("=" * 60)
ipsec = api.api_get('/api/v2/monitor/vpn/ipsec')
if ipsec and 'results' in ipsec:
    tunnels = ipsec['results']
    if isinstance(tunnels, list) and len(tunnels) > 0:
        print(f"  IPsec 隧道：{len(tunnels)} 个")
        for tunnel in tunnels[:5]:
            name = tunnel.get('name', 'N/A')
            status = tunnel.get('status', 'N/A')
            print(f"    - {name}: {status}")
    else:
        print("  IPsec 隧道：无配置")
else:
    print("  IPsec 隧道：N/A")
print("=" * 60)

api.disconnect()
print("\n✅ 查询完成")
