#!/usr/bin/env python3
"""扫描 10.254.254.0/24 网段找 FortiGate 防火墙"""
import socket
import concurrent.futures

def check_host(ip):
    """检查主机是否在线并探测 FortiGate 特征端口"""
    result = {'ip': ip, 'online': False, 'ports': [], 'is_fortigate': False}
    
    # 先 ping 检查（用 ICMP echo，需要 root）或者尝试连接常见端口
    # 尝试连接常见端口来判断是否在线
    ports_to_check = [22, 80, 443, 2443, 514, 10443]
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock_result = sock.connect_ex((ip, port))
            sock.close()
            if sock_result == 0:
                result['online'] = True
                result['ports'].append(port)
                # FortiGate 特征端口
                if port in [2443, 10443]:
                    result['is_fortigate'] = True
        except:
            pass
    
    return result

def scan_subnet():
    """扫描整个子网"""
    print("🔍 开始扫描 10.254.254.0/24 网段...\n")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for i in range(1, 255):
            ip = f"10.254.254.{i}"
            futures.append(executor.submit(check_host, ip))
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result['online']:
                results.append(result)
    
    # 显示结果
    print(f"✅ 发现 {len(results)} 个活跃主机:\n")
    
    fortigates = [r for r in results if r['is_fortigate']]
    others = [r for r in results if not r['is_fortigate']]
    
    if fortigates:
        print("🛡️  **可能的 FortiGate 防火墙:**")
        for fg in fortigates:
            print(f"   - {fg['ip']}  端口：{fg['ports']}")
        print()
    
    if others:
        print("💻  **其他设备:**")
        for dev in others:
            print(f"   - {dev['ip']}  端口：{dev['ports']}")
    
    if not results:
        print("❌ 未发现活跃主机，可能网络不可达或防火墙阻止了扫描")

if __name__ == "__main__":
    scan_subnet()
