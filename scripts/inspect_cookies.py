import os
import json
import base64
import sqlite3
import shutil
import win32crypt
from Crypto.Cipher import AES

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def inspect():
    key = get_encryption_key()
    user_data = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data")
    
    profiles = ["Default"]
    for item in os.listdir(user_data):
        if item.startswith("Profile "):
            profiles.append(item)
            
    for prof in profiles:
        cookie_path = os.path.join(user_data, prof, "Network", "Cookies")
        if not os.path.exists(cookie_path):
            continue
        temp_db = os.path.join(os.environ["TEMP"], f"test_{prof}.db")
        shutil.copyfile(cookie_path, temp_db)
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT DISTINCT host_key FROM cookies WHERE host_key LIKE '%meta%' OR host_key LIKE '%fb%'")
        rows = c.fetchall()
        print(f"Profile: {prof}, Matching hosts: {rows}")
        conn.close()
        os.remove(temp_db)

if __name__ == "__main__":
    inspect()
