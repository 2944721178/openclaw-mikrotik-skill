#!/usr/bin/env python3
"""
MikroTik 设备扫描器 - 类似 Winbox 的扫描功能

从本地主机直接扫描局域网中的 MikroTik 设备
不依赖任何已知的 MikroTik 设备或 API 连接
"""

import socket
import struct
import time
import subprocess
from typing import List, Dict, Optional


class MikroTikScanner:
    """MikroTik 设备扫描器（独立扫描，不依赖 API）"""
    
    # MikroTik 发现协议端口
    WINBOX_PORT = 5678
    BROADCAST_ADDR = '255.255.255.255'
    
    # MikroTik OUI 前缀（用于识别）
    # 这些是 MikroTik 官方的 MAC 地址前缀，用于识别设备品牌
    MIKROTIK_OUIS = [
        '00:0C:42', '4C:5E:0C', 'D4:CA:6D',
        '78:8B:77', '84:D1:54', 'B8:69:F4'
    ]
    
    def __init__(self, timeout: float = 2.0):
        """
        初始化扫描器
        
        Args:
            timeout: 扫描超时（秒）
        """
        self.timeout = timeout
        self.discovered_devices: List[Dict] = []
    
    def get_local_subnets(self) -> List[str]:
        """
        获取本地所有网段
        
        Returns:
            网段列表（如 ['192.168.1.0/24', '10.0.0.0/24']）
        """
        subnets = []
        try:
            result = subprocess.run(['ip', '-o', 'addr', 'show'], 
                                   capture_output=True, text=True, timeout=5)
            
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '/' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if '/' in part and '.' in part:
                            ip, prefix = part.split('/')
                            if int(prefix) == 24:
                                # 排除 lo 和虚拟接口
                                iface = parts[1] if len(parts) > 1 else ''
                                if iface not in ['lo', 'docker0'] and not iface.startswith('br-'):
                                    octets = ip.split('.')
                                    subnet = f"{octets[0]}.{octets[1]}.{octets[2]}.0/{prefix}"
                                    if subnet not in subnets:
                                        subnets.append(subnet)
        except Exception as e:
            print(f"⚠️ 获取本地网段失败：{e}")
        
        return subnets
    
    def get_local_ips(self) -> List[str]:
        """
        获取本机所有 IP 地址
        
        Returns:
            IP 地址列表
        """
        ips = []
        try:
            result = subprocess.run(['hostname', '-I'], 
                                   capture_output=True, text=True, timeout=5)
            ips = result.stdout.strip().split()
        except:
            pass
        return ips
    
    def scan_arp_table(self) -> List[Dict]:
        """
        从本地 ARP 表发现 MikroTik 设备
        
        Returns:
            发现的设备列表
        """
        devices = []
        local_ips = self.get_local_ips()
        
        try:
            result = subprocess.run(['ip', 'neigh'], 
                                   capture_output=True, text=True, timeout=5)
            
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 5:
                    ip = parts[0]
                    
                    # 排除本机 IP
                    if ip in local_ips:
                        continue
                    
                    if parts[1] == 'dev':
                        # 查找 MAC 地址
                        mac = ''
                        for i, part in enumerate(parts):
                            if part == 'lladdr':
                                mac = parts[i+1].upper() if i+1 < len(parts) else ''
                                break
                        
                        if mac and mac != '00:00:00:00:00:00':
                            # 检查是否是 MikroTik OUI
                            is_mikrotik = any(mac.startswith(oui) for oui in self.MIKROTIK_OUIS)
                            
                            if is_mikrotik:
                                device = {
                                    'ip': ip,
                                    'mac': mac,
                                    'identity': 'MikroTik',
                                    'model': 'Unknown',
                                    'version': '',
                                    'source': 'arp'
                                }
                                devices.append(device)
                                print(f"  ✅ 发现：{ip} ({mac})")
        except Exception as e:
            print(f"⚠️ ARP 表扫描失败：{e}")
        
        return devices
    
    def send_discovery_request(self, subnet: str) -> List[Dict]:
        """
        发送 MikroTik 发现请求到指定子网
        
        Args:
            subnet: 子网地址（如 '192.168.1.0/24'）
        
        Returns:
            发现的设备列表
        """
        devices = []
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(1.0)
            
            # 构建发现请求报文
            my_mac = b'\x00\x00\x00\x00\x00\x00'
            proto_type = struct.pack('!H', 0x0001)
            discovery_msg = my_mac + proto_type
            
            # 获取子网中的所有 IP
            ips = self._get_subnet_ips(subnet)
            
            # 发送到每个 IP
            for ip in ips:
                try:
                    sock.sendto(discovery_msg, (ip, self.WINBOX_PORT))
                    time.sleep(0.01)
                except:
                    pass
            
            # 接收响应
            start_time = time.time()
            while time.time() - start_time < 3.0:
                try:
                    data, addr = sock.recvfrom(2048)
                    device = self._parse_discovery_packet(data, addr[0])
                    
                    if device:
                        mac = device.get('mac', '')
                        if mac and not any(d.get('mac') == mac for d in devices):
                            devices.append(device)
                            print(f"  ✅ 发现：{device.get('identity', 'Unknown')} ({addr[0]})")
                except socket.timeout:
                    break
                except:
                    pass
            
            sock.close()
            
        except Exception as e:
            print(f"⚠️ 发送请求失败：{e}")
        
        return devices
    
    def _get_subnet_ips(self, subnet: str) -> List[str]:
        """获取子网中的所有 IP 地址"""
        network, prefix = subnet.split('/')
        prefix = int(prefix)
        
        network_bytes = struct.unpack('!I', socket.inet_aton(network))[0]
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        network_masked = network_bytes & mask
        broadcast = network_masked | (~mask & 0xFFFFFFFF)
        
        start_ip = network_masked + 1
        end_ip = broadcast - 1
        
        ips = []
        for ip_int in range(start_ip, end_ip + 1):
            ips.append(socket.inet_ntoa(struct.pack('!I', ip_int)))
        
        return ips
    
    def _parse_discovery_packet(self, data: bytes, source_ip: str) -> Optional[Dict]:
        """解析 MikroTik 发现协议报文"""
        if len(data) < 8:
            return None
        
        device = {
            'ip': source_ip,
            'source': 'broadcast'
        }
        
        try:
            offset = 6  # 跳过目标 MAC
            proto_type = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            
            # TLV 字段映射
            TLV_IDENTITY = 0x0001
            TLV_MAC = 0x0006
            TLV_PLATFORM = 0x0009
            TLV_VERSION = 0x0008
            TLV_BOARD = 0x000A
            
            while offset < len(data) - 4:
                tlv_type = struct.unpack('!H', data[offset:offset+2])[0]
                offset += 2
                
                tlv_len = struct.unpack('!H', data[offset:offset+2])[0]
                offset += 2
                
                if offset + tlv_len > len(data):
                    break
                
                value = data[offset:offset+tlv_len]
                offset += tlv_len
                
                if tlv_type == TLV_IDENTITY:
                    device['identity'] = value.decode('utf-8', errors='ignore').strip()
                elif tlv_type == TLV_MAC:
                    if len(value) == 6:
                        device['mac'] = ':'.join([f'{b:02X}' for b in value])
                elif tlv_type == TLV_PLATFORM:
                    device['platform'] = value.decode('utf-8', errors='ignore').strip()
                elif tlv_type == TLV_VERSION:
                    device['version'] = value.decode('utf-8', errors='ignore').strip()
                elif tlv_type == TLV_BOARD:
                    device['board'] = value.decode('utf-8', errors='ignore').strip()
            
            # 使用 board 作为型号
            if 'board' in device:
                device['model'] = device['board']
            elif 'platform' in device and device['platform'] != 'MikroTik':
                device['model'] = device['platform']
            else:
                device['model'] = 'Unknown'
            
            if 'mac' in device:
                return device
            
        except Exception as e:
            pass
        
        return None
    
    def scan(self) -> List[Dict]:
        """
        执行完整扫描
        
        Returns:
            发现的设备列表
        """
        all_devices = {}
        
        # 获取本地网段
        subnets = self.get_local_subnets()
        if not subnets:
            print("⚠️ 无法获取本地网段")
            return []
        
        print(f"📡 扫描 {len(subnets)} 个本地网段:")
        for subnet in subnets:
            print(f"   - {subnet}")
        print()
        
        # 方法 1: 扫描 ARP 表
        print("🔍 方法 1: 扫描 ARP 表...")
        arp_devices = self.scan_arp_table()
        for dev in arp_devices:
            mac = dev.get('mac', '')
            if mac:
                all_devices[mac] = dev
        
        # 方法 2: 主动发现请求
        if not arp_devices:
            print("\n🔍 方法 2: 发送发现请求...")
            for subnet in subnets:
                print(f"   扫描：{subnet}")
                devices = self.send_discovery_request(subnet)
                for dev in devices:
                    mac = dev.get('mac', '')
                    if mac and mac not in all_devices:
                        all_devices[mac] = dev
        
        self.discovered_devices = list(all_devices.values())
        return self.discovered_devices
    
    def format_results(self) -> str:
        """格式化扫描结果"""
        if not self.discovered_devices:
            return "  (未发现设备)"
        
        lines = []
        lines.append(f"\n共发现 {len(self.discovered_devices)} 个设备:\n")
        
        for i, device in enumerate(self.discovered_devices, 1):
            identity = device.get('identity', 'Unknown')
            ip = device.get('ip', 'N/A')
            mac = device.get('mac', '')
            model = device.get('model', '')
            version = device.get('version', '')
            source = device.get('source', 'unknown')
            
            lines.append(f"  [{i}] {identity}")
            lines.append(f"      IP: {ip}")
            if mac:
                lines.append(f"      MAC: {mac}")
            if model and model != 'Unknown':
                lines.append(f"      型号：{model}")
            if version:
                lines.append(f"      版本：{version}")
            
            if source == 'arp':
                lines.append(f"      来源：ARP 表")
            elif source == 'broadcast':
                lines.append(f"      来源：广播发现")
            else:
                lines.append(f"      来源：主动发现")
            
            lines.append("")
        
        return "\n".join(lines)


def scan_network() -> str:
    """
    扫描网络中的 MikroTik 设备
    
    Returns:
        格式化的扫描结果
    """
    scanner = MikroTikScanner(timeout=2.0)
    scanner.scan()
    return scanner.format_results()


if __name__ == '__main__':
    print(scan_network())
