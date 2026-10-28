import sys
import time
import requests
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Đoạn văn tiếng Trung mẫu (Tiên hiệp / Kiếm hiệp)
CHINESE_TEXT = """那少年一袭白衣，负手而立于孤峰之上。四周狂风呼啸，云海翻腾，却拂不动他半片衣角。
他缓缓拔出腰间长剑，剑身如秋水般澄澈，隐隐泛着冰蓝色的光芒。
“三百年了，这笔恩怨，今日便彻底做个了断吧。”"""

PROMPT_MESSAGES = [
    {
        "role": "system",
        "content": "Bạn là dịch giả tiếng Trung sang tiếng Việt chuyên nghiệp, dịch văn phong tự nhiên, đậm chất tiên hiệp kiếm hiệp."
    },
    {
        "role": "user",
        "content": f"Dịch đoạn văn bản sau sang tiếng Việt:\n{CHINESE_TEXT}"
    }
]

ROUTER_URL = "http://100.92.145.57:20128/v1/chat/completions"
ROUTER_KEY = "sk-03e57ebc0d35b288-sld2yo-498df0af"

MUSE_DIRECT_URL = "http://100.92.145.57:18610/v1/chat/completions"
MUSE_KEY = "m2a_c88ad8240c6233938b2a8dfe15685d56fa8a6cb659bdd20f"

def test_model(name, url, key, model_id):
    print(f"\n==========================================")
    print(f"[*] DANG TEST: {name} (Model: {model_id})")
    print(f"==========================================")
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": PROMPT_MESSAGES,
        "temperature": 0.3,
        "stream": False
    }

    start_time = time.time()
    try:
        res = requests.post(url, json=data, headers=headers, timeout=90)
        elapsed = time.time() - start_time
        
        if res.status_code == 200:
            result_json = res.json()
            content = result_json["choices"][0]["message"]["content"]
            print(f"[+] Thoi gian phan hoi: {elapsed:.2f} giay")
            print(f"[+] Ban dich tieng Viet:\n{content.strip()}\n")
            return elapsed, content
        else:
            print(f"[-] Loi HTTP {res.status_code}: {res.text}")
            return None, None
    except Exception as e:
        print(f"[-] Ngoai le loi: {e}")
        return None, None

if __name__ == "__main__":
    print("BAT DAU SO SANH TOC DO DICH THUAT (TIENG TRUNG -> TIENG VIET)")
    
    # 1. Test Gemini 3.8 Flash qua 9Router
    time_flash, res_flash = test_model("Gemini 3.8 Flash", ROUTER_URL, ROUTER_KEY, "ag/gemini-3.8-flash")
    
    # 2. Test Muse Spark (qua muse2api)
    time_muse, res_muse = test_model("Muse Spark", MUSE_DIRECT_URL, MUSE_KEY, "muse-spark")

    print("\n================ TONG KET SO SANH ================")
    if time_flash and time_muse:
        print(f"Gemini 3.8 Flash : {time_flash:.2f} giay")
        print(f"Muse Spark       : {time_muse:.2f} giay")
        if time_flash < time_muse:
            diff = time_muse / time_flash
            print(f"==> Gemini 3.8 Flash NHANH HON gap {diff:.1f} lan!")
        else:
            diff = time_flash / time_muse
            print(f"==> Muse Spark NHANH HON gap {diff:.1f} lan!")
