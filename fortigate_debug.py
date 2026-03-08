#!/usr/bin/env python3
"""FortiGate 状态查询脚本 - 调试版"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/skills/fortigate/fortigate-api')
from client import FortiGateAPI
import requests
import json

host = '10.254.254.250'
username = 'admin'
password = '90-=op[]'

api = FortiGateAPI(host, username, password, verify_ssl=False)

print("🔌 正在连接 FortiGate 防火墙...")
if not api.connect():
    print("❌ 连接失败")
    sys.exit(1)

print("✅ 连接成功！\n")

# 尝试不同的 API 端点
endpoints = [
    '/api/v2/monitor/system/status',
    '/api/v2/monitor/system/resource',
    '/api/v2/monitor/system/interface',
    '/api/v2/cmdb/system/interface',
    '/api/v2/monitor/vpn/ipsec',
]

for endpoint in endpoints:
    print(f"\n📍 测试端点：{endpoint}")
    try:
        result = api.api_get(endpoint)
        if result:
            print(f"✅ 成功 - 响应类型：{type(result)}")
            # 打印简化版响应
            if isinstance(result, dict):
                keys = list(result.keys())[:10]
                print(f"   顶层键：{keys}")
                if 'results' in result:
                    if isinstance(result['results'], dict):
                        print(f"   results 键：{list(result['results'].keys())[:5]}")
                    elif isinstance(result['results'], list):
                        print(f"   results 是列表，长度：{len(result['results'])}")
                        if len(result['results']) > 0 and isinstance(result['results'][0], dict):
                            print(f"   第一个项目键：{list(result['results'][0].keys())[:5]}")
            print(f"   完整响应 (前 500 字符):\n{json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
        else:
            print(f"❌ 无响应")
    except Exception as e:
        print(f"❌ 错误：{e}")

api.disconnect()
