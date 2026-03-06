#!/usr/bin/env python3
"""
MikroTik RouterOS Skill - 命令处理器
"""

import sys
import os
import re

# 添加 API 库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mikrotik-api'))

from client import MikroTikAPI
from commands import QuickCommands


def get_device_config(device_name=None):
    """
    获取设备配置（从 TOOLS.md 或环境变量）
    
    优先级：环境变量 > TOOLS.md > 默认值
    
    支持空密码和有密码两种情况
    """
    devices = {}
    
    # 1. 首先尝试从环境变量读取（最高优先级）
    env_host = os.environ.get('MIKROTIK_HOST')
    env_user = os.environ.get('MIKROTIK_USER', 'admin')
    env_pass = os.environ.get('MIKROTIK_PASS', '')  # 空密码是允许的
    
    if env_host:
        devices['default'] = {
            'host': env_host,
            'username': env_user,
            'password': env_pass  # 支持空字符串
        }
    
    # 2. 从 TOOLS.md 读取配置
    tools_md_path = os.path.expanduser('~/.openclaw/workspace/TOOLS.md')
    if os.path.exists(tools_md_path):
        try:
            with open(tools_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 MikroTik 设备配置
            # 格式：- **名称**：IP, 用户名，密码 (可选)
            # 示例：- **工位**：10.0.5.4, admin, 空密码
            # 示例：- **home**：192.168.88.1, admin, mypassword123
            mikrotik_section = re.search(r'###\s*MikroTik 设备\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL | re.IGNORECASE)
            if mikrotik_section:
                section_text = mikrotik_section.group(1)
                
                # 提取每个设备配置
                device_pattern = r'-\s*\*\*([^*]+)\*\*[:：]\s*([^,\n]+),\s*([^,\n]+),\s*(.+?)\s*$'
                matches = re.findall(device_pattern, section_text, re.MULTILINE)
                
                for name, host, username, password in matches:
                    device_key = name.strip().lower()
                    # 处理"空密码"的情况
                    pwd = password.strip()
                    if pwd.lower() in ['空密码', '无密码', 'none', 'null', '']:
                        pwd = ''
                    
                    devices[device_key] = {
                        'host': host.strip(),
                        'username': username.strip(),
                        'password': pwd
                    }
        except Exception as e:
            print(f"⚠️ 读取 TOOLS.md 失败：{e}")
    
    # 3. 返回请求的设备配置
    if device_name:
        # 优先返回环境变量配置的 default
        if device_name.lower() in ['default', '默认'] and 'default' in devices:
            return devices['default']
        return devices.get(device_name.lower())
    
    # 没有指定设备时，返回第一个可用的
    if 'default' in devices:
        return devices['default']
    if devices:
        return list(devices.values())[0]
    
    return None


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
    """
    执行 MikroTik 命令
    
    支持空密码和有密码两种情况
    """
    config = get_device_config(device)
    
    if not config:
        # 提供友好的错误提示
        error_msg = "❌ 未找到设备配置\n\n"
        error_msg += "请在 TOOLS.md 中添加 MikroTik 设备配置:\n"
        error_msg += "```markdown\n"
        error_msg += "### MikroTik 设备\n"
        error_msg += "- **工位**：10.0.5.4, admin, 空密码\n"
        error_msg += "- **home**：192.168.88.1, admin, yourpassword\n"
        error_msg += "```\n"
        error_msg += "\n或使用环境变量:\n"
        error_msg += "- `MIKROTIK_HOST`: 设备 IP\n"
        error_msg += "- `MIKROTIK_USER`: 用户名 (可选，默认 admin)\n"
        error_msg += "- `MIKROTIK_PASS`: 密码 (可选，支持空密码)"
        return error_msg
    
    try:
        # 显示连接信息（调试用，生产环境可移除）
        pwd_display = "(空密码)" if config['password'] == '' else "(已配置密码)"
        print(f"🔌 连接设备：{config['host']} [{config['username']}] {pwd_display}")
        
        api = MikroTikAPI(
            config['host'], 
            config['username'], 
            config['password'],
            timeout=10  # 增加超时时间
        )
        
        if not api.connect():
            return f"❌ 无法连接到 {config['host']}\n\n请检查:\n1. 设备 IP 是否正确\n2. 网络是否可达\n3. API 服务是否启用（默认端口 8728）"
        
        if not api.login():
            pwd_hint = "空密码" if config['password'] == '' else "密码可能错误"
            return f"❌ 登录失败 ({pwd_hint})\n\n请检查:\n1. 用户名/密码是否正确\n2. 用户是否有 API 访问权限"
        
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
    
    except ConnectionRefusedError:
        return f"❌ 连接被拒绝：{config['host']}\n\n可能原因:\n1. API 服务未启用\n2. 防火墙阻止了 8728 端口\n3. 设备离线"
    except TimeoutError:
        return f"❌ 连接超时：{config['host']}\n\n请检查网络连通性"
    except Exception as e:
        return f"❌ 错误：{type(e).__name__}: {e}"


def handle_message(message):
    """处理用户消息"""
    original_message = message
    message = message.lower().strip()
    
    # 解析命令
    if 'mikrotik' in message or 'routeros' in message or '路由器' in message:
        # 提取设备名称（支持中文和英文）
        device = None
        
        # 尝试从 TOOLS.md 中匹配已配置的设备名称
        tools_md_path = os.path.expanduser('~/.openclaw/workspace/TOOLS.md')
        if os.path.exists(tools_md_path):
            try:
                with open(tools_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取所有已配置的设备名称
                mikrotik_section = re.search(r'###\s*MikroTik 设备\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL | re.IGNORECASE)
                if mikrotik_section:
                    section_text = mikrotik_section.group(1)
                    device_names = re.findall(r'\*\*([^*]+)\*\*', section_text)
                    
                    # 检查消息中是否包含已配置的设备名称
                    for name in device_names:
                        if name.strip().lower() in message or name.strip() in original_message:
                            device = name.strip().lower()
                            break
            except:
                pass
        
        # 如果没有匹配到设备名称，使用默认值
        if not device:
            device = 'default'  # 使用默认设备
        
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
