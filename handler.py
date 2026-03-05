#!/usr/bin/env python3
"""
MikroTik RouterOS Skill - 命令处理器
"""

import sys
import os

# 添加 API 库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mikrotik-api'))

from client import MikroTikAPI
from commands import QuickCommands


def get_device_config(device_name=None):
    """获取设备配置（从 TOOLS.md 或环境变量）"""
    # 默认设备配置
    devices = {
        'office': {'host': '10.0.5.4', 'username': 'admin', 'password': ''},
    }
    
    if device_name:
        return devices.get(device_name.lower())
    return devices.get('office')  # 默认返回 office


def format_status(api, quick):
    """格式化设备状态"""
    identity = quick.system.get_identity()
    resource = quick.system.get_resource()
    
    lines = [
        "📡 MikroTik RouterOS 设备状态",
        "=" * 60,
        f"  设备名：{identity.get('name', 'N/A')}",
        f"  版本：{resource.get('version', 'N/A')}",
        f"  运行时间：{resource.get('uptime', 'N/A')}",
        f"  CPU: {resource.get('cpu', 'N/A')} @ {resource.get('cpu-frequency', 'N/A')}MHz",
        f"  CPU 负载：{resource.get('cpu-load', 'N/A')}%",
        f"  内存：{int(resource.get('free-memory', 0))/1024/1024:.1f}MB / "
        f"{int(resource.get('total-memory', 1))/1024/1024:.1f}MB",
        f"  存储：{int(resource.get('free-hdd-space', 0))/1024/1024:.1f}MB / "
        f"{int(resource.get('total-hdd-space', 1))/1024/1024:.1f}MB",
        "=" * 60,
    ]
    
    # 接口状态
    lines.append("\n🔌 网络接口:")
    interfaces = quick.network.get_interfaces()
    for iface in interfaces:
        name = iface.get('name', 'unknown')
        running = iface.get('running', 'false') == 'true'
        status = "✅" if running else "❌"
        lines.append(f"  {status} {name}")
    
    # IP 地址
    lines.append("\n🌐 IP 地址:")
    addresses = quick.network.get_ip_addresses()
    for addr in addresses:
        lines.append(f"  - {addr.get('address', 'N/A')} on {addr.get('interface', 'N/A')}")
    
    # 默认路由
    lines.append("\n🛤️ 默认路由:")
    routes = quick.network.get_routes()
    for route in routes:
        if route.get('dst-address') == '0.0.0.0/0':
            lines.append(f"  - 默认网关：{route.get('gateway', 'N/A')}")
    
    return "\n".join(lines)


def format_firewall(api, quick):
    """格式化防火墙信息"""
    lines = [
        "🔥 MikroTik 防火墙配置",
        "=" * 60,
    ]
    
    # 过滤规则
    lines.append("\n📋 过滤规则:")
    rules = quick.firewall.get_filter_rules()
    if rules:
        for i, rule in enumerate(rules, 1):
            chain = rule.get('chain', 'N/A')
            action = rule.get('action', 'N/A')
            disabled = rule.get('disabled', '') == 'true'
            comment = rule.get('comment', '')
            status = "⏸️" if disabled else "✅"
            lines.append(f"  {status} [{i}] {chain}: {action}" + (f" ({comment})" if comment else ""))
    else:
        lines.append("  (无规则)")
    
    # NAT 规则
    lines.append("\n🔄 NAT 规则:")
    rules = quick.firewall.get_nat_rules()
    if rules:
        for i, rule in enumerate(rules, 1):
            chain = rule.get('chain', 'N/A')
            action = rule.get('action', 'N/A')
            to_addr = rule.get('to-addresses', '')
            comment = rule.get('comment', '')
            line = f"  [{i}] {chain}: {action}"
            if to_addr:
                line += f" → {to_addr}"
            if comment:
                line += f" ({comment})"
            lines.append(line)
    else:
        lines.append("  (无规则)")
    
    # 活动连接
    lines.append("\n🔗 活动连接数：检查中...")
    
    return "\n".join(lines)


def format_interfaces(api, quick):
    """格式化接口信息"""
    lines = [
        "🔌 网络接口",
        "=" * 60,
    ]
    
    interfaces = quick.network.get_interfaces()
    for iface in interfaces:
        name = iface.get('name', 'unknown')
        running = iface.get('running', 'false') == 'true'
        mtu = iface.get('mtu', 'N/A')
        mac = iface.get('mac-address', 'N/A')
        status = "✅" if running else "❌"
        lines.append(f"  {status} {name} (MTU: {mtu}, MAC: {mac})")
    
    return "\n".join(lines)


def execute_command(device, command):
    """执行 MikroTik 命令"""
    config = get_device_config(device)
    if not config:
        return f"❌ 未找到设备配置：{device}"
    
    try:
        api = MikroTikAPI(config['host'], config['username'], config['password'])
        
        if not api.connect():
            return f"❌ 无法连接到 {config['host']}"
        
        if not api.login():
            return "❌ 登录失败"
        
        quick = QuickCommands(api)
        
        # 根据命令类型返回不同格式
        if 'status' in command.lower() or '状态' in command:
            result = format_status(api, quick)
        elif 'firewall' in command.lower() or '防火墙' in command:
            result = format_firewall(api, quick)
        elif 'interface' in command.lower() or '接口' in command:
            result = format_interfaces(api, quick)
        else:
            # 执行自定义命令
            results = api.run_command(command)
            if results:
                result = "命令执行结果:\n"
                for item in results:
                    for key, value in item.items():
                        result += f"  {key}: {value}\n"
            else:
                result = "(无结果)"
        
        api.disconnect()
        return result
    
    except Exception as e:
        return f"❌ 错误：{e}"


def handle_message(message):
    """处理用户消息"""
    message = message.lower().strip()
    
    # 解析命令
    if 'mikrotik' in message or 'routeros' in message or '路由器' in message:
        # 提取设备 IP 或名称
        device = 'office'  # 默认
        
        # 检查命令类型
        if '状态' in message or 'status' in message:
            return execute_command(device, 'status')
        elif '防火墙' in message or 'firewall' in message:
            return execute_command(device, 'firewall')
        elif '接口' in message or 'interface' in message:
            return execute_command(device, 'interfaces')
        elif '执行' in message or '命令' in message:
            # 提取命令路径
            if '/ip/' in message or '/system/' in message:
                cmd_start = message.find('/')
                command = message[cmd_start:].split()[0]
                return execute_command(device, command)
    
    return None  # 不是本 skill 处理的命令


if __name__ == '__main__':
    # 测试
    if len(sys.argv) > 1:
        device = sys.argv[1] if len(sys.argv) > 1 else 'office'
        command = sys.argv[2] if len(sys.argv) > 2 else 'status'
        print(execute_command(device, command))
    else:
        print("用法：python handler.py [设备] [命令]")
        print("示例：python handler.py office status")
