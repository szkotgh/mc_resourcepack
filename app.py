import os
import re
import requests
import shutil
import ctypes
import sys

# minecraft resource pack auto updater

TIMEOUT = 5

USER_PATH = os.path.expanduser("~")
RESOURCE_PACK_PATH = os.path.join(USER_PATH, "AppData", "Roaming", ".minecraft", "resourcepacks")
RESOURCE_PACK_NAME = "Geon's_Sound_Modify"

GIT_NAME = 'szkotgh'
GIT_REPO = 'mc_resourcepack'
GIT_BRANCH = 'soundpack'

VERSION_RE = r"<VERSION>([\d.]+)</VERSION>"

def check_os(success_os=['nt']):
    if os.name not in success_os:
        return False
    return True

def is_resource_pack_installed():
    return os.path.exists(os.path.join(RESOURCE_PACK_PATH, RESOURCE_PACK_NAME))

def get_local_version():
    try:
        with open(os.path.join(RESOURCE_PACK_PATH, RESOURCE_PACK_NAME, "version"), "r") as f:
            version_re = re.search(VERSION_RE, f.read())
            version = version_re.group(1)
            return float(version)
    except:
        return None

def get_last_version():
    req_url = f"https://raw.githubusercontent.com/{GIT_NAME}/{GIT_REPO}/{GIT_BRANCH}/version"
    try:
        response = requests.get(req_url, timeout=TIMEOUT)
        response.raise_for_status()
        version_re = re.search(VERSION_RE, response.text)
        version = version_re.group(1)
        return float(version)
    except:
        return None

def remove_local_resource_pack():
    print("Removing ResourcePack . . .")
    
    if is_resource_pack_installed() == False:
        print("! ResourcePack is not installed.")
        return False
    
    try:
        shutil.rmtree(os.path.join(RESOURCE_PACK_PATH, RESOURCE_PACK_NAME))
        return True
    except Exception as e:
        print("! Failed to remove ResourcePack:", e)
        return False

def install_local_resource_pack():
    resource_pack_zip_name = 'resourcepack_temp.zip'
    
    print("Installing ResourcePack . . .")
    
    if is_resource_pack_installed():
        print("! ResourcePack is already installed.")
        return False
    
    # download zip file
    print("- Downloading ResourcePack . . .")
    try:
        req_url = f"https://github.com/{GIT_NAME}/{GIT_REPO}/archive/refs/heads/{GIT_BRANCH}.zip"
        response = requests.get(req_url, timeout=TIMEOUT)
        response.raise_for_status()
        ## write zip file
        with open(f"{resource_pack_zip_name}", "wb") as f:
            f.write(response.content)
    except:
        print("! Failed to download ResourcePack.")
        return False

    print("- Extracting ResourcePack . . .")
    # extract zip file
    try:
        os.system(f"tar -xf {resource_pack_zip_name} -C {RESOURCE_PACK_PATH}")
    except:
        print("! Failed to extract ResourcePack.")
        os.remove(f"{resource_pack_zip_name}")
        os.remove(os.path.join(RESOURCE_PACK_PATH, f"{GIT_REPO}-{GIT_BRANCH}"))
        return False
    
    print("- Renaming ResourcePack . . .")
    # rename folder
    try:
        os.rename(os.path.join(RESOURCE_PACK_PATH, f"{GIT_REPO}-{GIT_BRANCH}"), os.path.join(RESOURCE_PACK_PATH, RESOURCE_PACK_NAME))
        os.remove(f"{resource_pack_zip_name}")
    except:
        print("! Failed to rename ResourcePack.")
        os.remove(os.path.join(RESOURCE_PACK_PATH, f"{GIT_REPO}-{GIT_BRANCH}"))
        os.remove(f"{resource_pack_zip_name}")
        return False
        
    return True

def update_resource_pack():
    print("Updating ResourcePack . . .")
    
    if is_resource_pack_installed() == True:
        print("- Removing old ResourcePack . . .")
        if remove_local_resource_pack() == False:
            return False
    
    print("- Installing new ResourcePack . . .")
    if install_local_resource_pack() == False:
        return False
    
    return True

def print_user_input(question = "> "):
    try:
        return input(question)
    except:
        return None

def print_user_confirm(question):
    print(question, end=" ")
    print("[y/n]")
    user_input = print_user_input()
    if user_input.lower() == 'y':
        return True
    return False

def press_enter_to_continue():
    input("Press [Enter] to continue . . .")

def get_update_str():
    if get_local_version() == None or get_last_version() == None:
        return "Failed to get version info. Check your internet connection . . ."
    
    if get_last_version() > get_local_version():
        return "There is a new version! Press [1] to install it."
    else:
        return "You are using the latest version!"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        print("Requesting admin privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

# check os
if check_os(['nt']) == False:
    print("This program is only available for Windows.")
    press_enter_to_continue()
    os._exit(1)

# request admin privileges
run_as_admin()

# run program
while True:
    os.system("cls")
    print("ResourcePack Auto Updater v0.1")
    print("===================================")
    if is_resource_pack_installed():
        print(f"Local version: {get_local_version()}")
        print(f"Last version: {get_last_version()}")
        print(get_update_str())
    else:
        print("ResourcePack is not installed. Press key [1] to install.")
    print("===================================")
    if is_resource_pack_installed():
        print("1. Update/Re-Install ResourcePack")
    else:
        print("1. Install ResourcePack")
    if is_resource_pack_installed():
        print("2. Remove ResourcePack")
    print("3. Exit")
    user_input = print_user_input()
    
    if user_input == '1':
        if is_resource_pack_installed():
            if print_user_confirm("ResourcePack is already installed. Do you want to update?") == False:
                print("ResourcePack installation canceled.", end="\n\n")
                press_enter_to_continue()
                continue
            
            old_version = get_local_version()
            if update_resource_pack():
                print(f"ResourcePack Update successfully ({old_version}) -> ({get_local_version()}).", end="\n\n")
            else:
                print("ResourcePack Update failed.", end="\n\n")
            press_enter_to_continue()
            
        else:
            if print_user_confirm("Do you want to install the ResourcePack?") == False:
                print("ResourcePack installation canceled.", end="\n\n")
                press_enter_to_continue()
                continue
            
            if install_local_resource_pack():
                print(f"ResourcePack installed successfully ({get_local_version()}).", end="\n\n")
            else:
                print("ResourcePack installation failed.", end="\n\n")
            press_enter_to_continue()
            
    elif user_input == '2':        
        if print_user_confirm("Do you want to remove the ResourcePack?") == False:
            print("ResourcePack removal canceled.", end="\n\n")
            press_enter_to_continue()
            continue
        
        if remove_local_resource_pack():
            print("ResourcePack removed successfully.", end="\n\n")
        else:
            print("ResourcePack removal failed. Did you unload the resource pack?", end="\n\n")
        press_enter_to_continue()
    
    elif user_input == '3':
        print("Program terminated.")
        press_enter_to_continue()
        os._exit(0)
        
    else:
        os.system("cls")