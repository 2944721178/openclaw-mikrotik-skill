#!/usr/bin/env python3
"""
MikroTik RouterOS API Client - 核心连接模块
"""

import socket
import select
from typing import List, Dict, Optional, Any


class MikroTikAPI:
    """MikroTik RouterOS API 客户端"""
    
    def __init__(self, host: str, username: str = 'admin', password: str = '', 
                 port: int = 8728, timeout: int = 5):
        """
        初始化 API 客户端
        
        Args:
            host: RouterOS 设备 IP 地址
            username: 用户名 (默认：admin)
            password: 密码 (默认：空)
            port: API 端口 (默认：8728, SSL 用 8729)
            timeout: 连接超时 (秒)
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None
        self.connected = False
    
    def connect(self) -> bool:
        """建立连接到 RouterOS"""
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self.sock.setblocking(0)  # 非阻塞模式
            self.connected = True
            return True
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.connected = False
    
    def _send_word(self, word: str) -> None:
        """发送一个 API 命令字"""
        if not self.sock:
            raise ConnectionError("未连接到 RouterOS")
        
        data = word.encode('utf-8')
        length = len(data)
        
        # 编码长度前缀
        if length < 0x80:
            header = bytes([length])
        elif length < 0x4000:
            header = bytes([0x80 | (length >> 8), length & 0xFF])
        elif length < 0x200000:
            header = bytes([0xC0 | (length >> 16), (length >> 8) & 0xFF, length & 0xFF])
        elif length < 0x10000000:
            header = bytes([0xE0 | (length >> 24), (length >> 16) & 0xFF, 
                           (length >> 8) & 0xFF, length & 0xFF])
        else:
            header = bytes([0xF0, (length >> 24) & 0xFF, (length >> 16) & 0xFF,
                           (length >> 8) & 0xFF, length & 0xFF])
        
        self.sock.sendall(header + data)
    
    def _recv_all(self, timeout: float = 3.0) -> bytes:
        """接收所有可用数据"""
        if not self.sock:
            return b''
        
        try:
            data = b''
            while True:
                ready = select.select([self.sock], [], [], timeout)
                if not ready[0]:
                    break
                chunk = self.sock.recv(65535)
                if not chunk:
                    break
                data += chunk
                # 如果收到的数据小于缓冲区，说明可能已经接收完成
                if len(chunk) < 65535:
                    # 再等一下看有没有更多数据
                    more_ready = select.select([self.sock], [], [], 0.5)
                    if not more_ready[0]:
                        break
            return data
        except Exception as e:
            print(f"⚠️ 接收异常：{e}")
            return data if 'data' in locals() else b''
    
    def _parse_response(self, data: bytes) -> List[Dict[str, str]]:
        """解析 API 响应数据"""
        import re
        text = data.decode('utf-8', errors='ignore')
        
        # 提取所有 =key=value 格式的数据（值只包含 printable 字符）
        matches = re.findall(r'=([a-zA-Z0-9_-]+)=([0-9a-zA-Z./() :_-]+)', text)
        
        if not matches:
            return []
        
        # 转换成字典
        result = {}
        for key, value in matches:
            result[key] = value.strip()
        
        return [result] if result else []
    
    def login(self) -> bool:
        """登录到 RouterOS"""
        if not self.sock:
            return False
        
        try:
            # 发送登录命令
            self._send_word('/login')
            self._send_word(f'=name={self.username}')
            self._send_word(f'=password={self.password}')
            self._send_word('')  # 结束标记
            
            # 等待响应
            data = self._recv_all(2)
            return b'!done' in data
        except Exception as e:
            print(f"❌ 登录失败：{e}")
            return False
    
    def run_command(self, command: str, args: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        执行 API 命令
        
        Args:
            command: 命令路径 (如 '/system/resource/print')
            args: 额外参数列表 (如 ['=detail=', '=active='])
        
        Returns:
            解析后的响应数据列表
        """
        if not self.connected:
            raise ConnectionError("未连接到 RouterOS")
        
        try:
            # 发送命令
            self._send_word(command)
            if args:
                for arg in args:
                    self._send_word(arg)
            self._send_word('')  # 结束标记
            
            # 接收响应
            data = self._recv_all(3)
            return self._parse_response(data)
        except Exception as e:
            print(f"❌ 命令执行失败：{e}")
            return []
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
