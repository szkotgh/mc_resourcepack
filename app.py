import os
import re
import requests
import shutil
import ctypes
import sys

# minecraft resource pack auto updater
PROGRAM_VERSION = "0.3"
PROGRAM_NAME = f"[ RAU v{PROGRAM_VERSION} ]"

GIT_NAME = 'szkotgh'
GIT_REPO = 'mc_resourcepack'
GIT_BRANCH = 'soundpack'
TIMEOUT = 5

USER_PATH = os.path.expanduser("~")
RESOURCE_PACK_PATH = os.path.join(USER_PATH, "AppData", "Roaming", ".minecraft", "resourcepacks")
RESOURCE_PACK_NAME = "Geon's_Sound_Modify"

VERSION_RE = r"<VERSION>([\d.]+)</VERSION>"
VERSION_DESC_RE = r"<VERSION_DESC>(.*?)</VERSION_DESC>"

def check_os(success_os=['nt']):
    if os.name not in success_os:
        return False
    return True

def is_resource_pack_installed():
    return os.path.exists(os.path.join(RESOURCE_PACK_PATH, RESOURCE_PACK_NAME))

def find_version_in_str(string):
    version = None
    try:
        version = float(re.search(VERSION_RE, string).group(1))
    except:
        pass
    return version

def find_version_desc_in_str(string):
    version_desc = None
    try:
        version_desc = re.search(VERSION_DESC_RE, string).group(1)
    except:
        version_desc = str("No description")
    return version_desc

def get_local_version_info():
    # get version from local file
    try:
        with open(os.path.join(RESOURCE_PACK_PATH, RESOURCE_PACK_NAME, "version"), "r", encoding='utf-8') as f:
            local_file = f.read()
    except Exception as e:
        return None, None
    
    version = find_version_in_str(local_file)
    version_desc = find_version_desc_in_str(local_file)
    
    return float(version), str(version_desc)

def get_last_version_info():
    # get version from github
    req_url = f"https://raw.githubusercontent.com/{GIT_NAME}/{GIT_REPO}/{GIT_BRANCH}/version"
    try:
        response = requests.get(req_url, timeout=TIMEOUT)
        response.raise_for_status()
        
    except:
        return None, None
    
    version = find_version_in_str(response.text)
    version_desc = find_version_desc_in_str(response.text)
    
    return float(version), str(version_desc)

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
    except Exception as e:
        print(f"! Failed to download ResourcePack: {e}")
        return False

    print("- Extracting ResourcePack . . .")
    # extract zip file
    try:
        if not os.path.exists(RESOURCE_PACK_PATH):
            os.makedirs(RESOURCE_PACK_PATH)
        os.system(f"tar -xf {resource_pack_zip_name} -C {RESOURCE_PACK_PATH}")
    except Exception as e:
        print(f"! Failed to extract ResourcePack: {e}")
        os.remove(f"{resource_pack_zip_name}")
        os.remove(os.path.join(RESOURCE_PACK_PATH, f"{GIT_REPO}-{GIT_BRANCH}"))
        return False
    
    print("- Renaming ResourcePack . . .")
    # rename folder
    try:
        os.rename(os.path.join(RESOURCE_PACK_PATH, f"{GIT_REPO}-{GIT_BRANCH}"), os.path.join(RESOURCE_PACK_PATH, RESOURCE_PACK_NAME))
        os.remove(f"{resource_pack_zip_name}")
    except Exception as e:
        print(f"! Failed to rename ResourcePack: {e}")
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
    if get_local_version_info()[0] == None or get_last_version_info()[0] == None:
        return "Failed to get version info. Check your internet connection . . ."
    
    if get_last_version_info()[0] > get_local_version_info()[0]:
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
    
os.system(f"title {PROGRAM_NAME}")
if __name__ == "__main__":
    # request admin privileges
    # run_as_admin()

    # run program
    while True:
        os.system("cls")
        print(f"{PROGRAM_NAME}")
        print("==========================================================")
        if is_resource_pack_installed():
            if get_local_version_info() != None:
                print(f" Local version | v{get_local_version_info()[0]} - {get_local_version_info()[1]}")
            else:
                print(f" Local version | Failed to get local version info.")
            
            if get_last_version_info() != None:
                print(f"  Last version | v{get_last_version_info()[0]} - {get_last_version_info()[1]}")
            else:
                print(f"  Last version | Failed to get last version info.")

            if get_update_str() != None:
                print(f" {get_update_str()}")
        else:
            print(" ResourcePack is not installed. Press key [1] to install.")
        print("==========================================================")
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
                if print_user_confirm("Do you want to update the ResourcePack?") == False:
                    print("ResourcePack installation canceled.", end="\n\n")
                    press_enter_to_continue()
                    continue
                
                old_version = get_local_version_info()
                if update_resource_pack():
                    print(f"ResourcePack Update successfully (v{old_version[0]}) -> (v{get_local_version_info()[0]}).", end="\n\n")
                else:
                    print("ResourcePack Update failed.", end="\n\n")
                press_enter_to_continue()
                
            else:
                if print_user_confirm("Do you want to install the ResourcePack?") == False:
                    print("ResourcePack installation canceled.", end="\n\n")
                    press_enter_to_continue()
                    continue
                
                if install_local_resource_pack():
                    print(f"ResourcePack installed successfully (v{get_local_version_info()[0]}).", end="\n\n")
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