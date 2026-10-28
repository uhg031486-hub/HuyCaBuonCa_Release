import sys
import requests
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

url = "http://100.92.145.57:18610/v1/chat/completions"
key = "m2a_c88ad8240c6233938b2a8dfe15685d56fa8a6cb659bdd20f"

prompt = """Hãy tạo file audio đọc (TTS) đoạn văn sau bằng giọng đọc trầm ấm:
"Đêm nay gió lạnh tràn về đỉnh núi, tiếng kiếm ngân vang xé toạc màn sương."
Tạo luôn audio cho mình nhé!"""

data = {
    "model": "muse-spark",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "stream": False
}

try:
    r = requests.post(url, headers={"Authorization": f"Bearer {key}"}, json=data, timeout=60)
    print("Status:", r.status_code)
    res_data = r.json()
    print("Full response:", json.dumps(res_data, ensure_ascii=False, indent=2))
except Exception as e:
    print("Error:", e)
