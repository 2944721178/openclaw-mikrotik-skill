#!/usr/bin/env python3
"""
MikroTik RouterOS API - 常用命令封装
"""

from typing import List, Dict, Optional

# 支持直接运行和包导入两种模式
try:
    from .client import MikroTikAPI
except ImportError:
    from client import MikroTikAPI


class SystemCommands:
    """系统相关命令"""
    
    def __init__(self, api: MikroTikAPI):
        self.api = api
    
    def get_resource(self) -> Dict:
        """获取系统资源信息"""
        results = self.api.run_command('/system/resource/print')
        return results[0] if results else {}
    
    def get_identity(self) -> Dict:
        """获取设备标识"""
        results = self.api.run_command('/system/identity/print')
        return results[0] if results else {}
    
    def get_version(self) -> Dict:
        """获取系统版本"""
        results = self.api.run_command('/system/routerboard/print')
        return results[0] if results else {}
    
    def get_health(self) -> Dict:
        """获取健康状态（温度、电压等）"""
        results = self.api.run_command('/system/health/print')
        return results[0] if results else {}
    
    def reboot(self):
        """重启设备"""
        self.api.run_command('/system/reboot')
    
    def shutdown(self):
        """关闭设备"""
        self.api.run_command('/system/shutdown')


class FirewallCommands:
    """防火墙相关命令"""
    
    def __init__(self, api: MikroTikAPI):
        self.api = api
    
    def get_filter_rules(self) -> List[Dict]:
        """获取过滤规则"""
        return self.api.run_command('/ip/firewall/filter/print')
    
    def get_nat_rules(self) -> List[Dict]:
        """获取 NAT 规则"""
        return self.api.run_command('/ip/firewall/nat/print')
    
    def get_mangle_rules(self) -> List[Dict]:
        """获取 Mangle 规则"""
        return self.api.run_command('/ip/firewall/mangle/print')
    
    def get_active_connections(self, count: int = 100) -> List[Dict]:
        """获取活动连接"""
        return self.api.run_command('/ip/firewall/active/print', 
                                    [f'=.proplist=src-address,dst-address,protocol,src-port,dst-port'])
    
    def get_connection_stats(self) -> Dict:
        """获取连接统计"""
        results = self.api.run_command('/ip/firewall/connection/print', ['=count-only='])
        return {'total': len(results)} if results else {}


class NetworkCommands:
    """网络相关命令"""
    
    def __init__(self, api: MikroTikAPI):
        self.api = api
    
    def get_interfaces(self) -> List[Dict]:
        """获取网络接口列表"""
        return self.api.run_command('/interface/print')
    
    def get_ip_addresses(self) -> List[Dict]:
        """获取 IP 地址配置"""
        return self.api.run_command('/ip/address/print')
    
    def get_routes(self) -> List[Dict]:
        """获取路由表"""
        return self.api.run_command('/ip/route/print')
    
    def get_dns(self) -> List[Dict]:
        """获取 DNS 配置"""
        return self.api.run_command('/ip/dns/print')
    
    def get_dhcp_leases(self) -> List[Dict]:
        """获取 DHCP 租约"""
        return self.api.run_command('/ip/dhcp-server/lease/print')
    
    def get_arp(self) -> List[Dict]:
        """获取 ARP 表"""
        return self.api.run_command('/ip/arp/print')
    
    def get_neighbors(self) -> List[Dict]:
        """获取邻居发现"""
        return self.api.run_command('/ip/neighbor/print')


class QuickCommands:
    """快捷命令集合"""
    
    def __init__(self, api: MikroTikAPI):
        self.api = api
        self.system = SystemCommands(api)
        self.firewall = FirewallCommands(api)
        self.network = NetworkCommands(api)
    
    def status(self) -> Dict:
        """获取设备完整状态"""
        return {
            'identity': self.system.get_identity(),
            'resource': self.system.get_resource(),
            'interfaces': self.network.get_interfaces(),
            'addresses': self.network.get_ip_addresses(),
            'routes': self.network.get_routes(),
        }
    
    def print_status(self):
        """打印设备状态（人类可读）"""
        identity = self.system.get_identity()
        resource = self.system.get_resource()
        
        print("=" * 60)
        print("📡 MikroTik RouterOS 设备状态")
        print("=" * 60)
        print(f"  设备名：{identity.get('name', 'N/A')}")
        print(f"  版本：{resource.get('version', 'N/A')}")
        print(f"  运行时间：{resource.get('uptime', 'N/A')}")
        print(f"  CPU: {resource.get('cpu', 'N/A')} @ {resource.get('cpu-frequency', 'N/A')}MHz")
        print(f"  CPU 负载：{resource.get('cpu-load', 'N/A')}%")
        print(f"  内存：{int(resource.get('free-memory', 0))/1024/1024:.1f}MB / "
              f"{int(resource.get('total-memory', 1))/1024/1024:.1f}MB")
        print(f"  存储：{int(resource.get('free-hdd-space', 0))/1024/1024:.1f}MB / "
              f"{int(resource.get('total-hdd-space', 1))/1024/1024:.1f}MB")
        print("=" * 60)
        
        # 接口状态
        print("\n🔌 网络接口:")
        interfaces = self.network.get_interfaces()
        for iface in interfaces:
            name = iface.get('name', 'unknown')
            running = iface.get('running', 'false') == 'true'
            status = "✅" if running else "❌"
            print(f"  {status} {name}")
        
        # IP 地址
        print("\n🌐 IP 地址:")
        addresses = self.network.get_ip_addresses()
        for addr in addresses:
            print(f"  - {addr.get('address', 'N/A')} on {addr.get('interface', 'N/A')}")
        
        # 默认路由
        print("\n🛤️ 默认路由:")
        routes = self.network.get_routes()
        for route in routes:
            if route.get('dst-address') == '0.0.0.0/0':
                print(f"  - 默认网关：{route.get('gateway', 'N/A')}")
        
        print("=" * 60)
