import sys
import os
import json
import requests
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\scripts\zh_phrases.json', 'r', encoding='utf-8') as f:
    phrases = json.load(f)

print(f"Tong so cum tu can dich: {len(phrases)}")

URL = "http://100.92.145.57:20128/v1/chat/completions"
KEY = "sk-03e57ebc0d35b288-sld2yo-498df0af"
MODEL = "ag/gemini-3.8-flash"

mapping_file = r'c:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\scripts\zh_vi_mapping.json'
if os.path.exists(mapping_file):
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
else:
    mapping = {}

batch_size = 50
todo = [p for p in phrases if p not in mapping]
print(f"So cum tu con lai can dich: {len(todo)}")

for i in range(0, len(todo), batch_size):
    batch = todo[i:i+batch_size]
    print(f"Dang dich batch {i // batch_size + 1} / {(len(todo) + batch_size - 1) // batch_size} ({len(batch)} cum tu)...")
    
    prompt = """Bạn là chuyên gia dịch thuật UI phần mềm/web dashboard kỹ thuật từ tiếng Trung sang tiếng Việt.
Yêu cầu:
- Dịch chuẩn ngữ cảnh CNTT, giao diện quản trị Admin Panel.
- Các thuật ngữ kỹ thuật như Cookie, Session, Token, API, Key, Model, Header, CDP, Keepalive, WebSocket, URL, HTTP, v.v. giữ nguyên hoặc dịch tự nhiên (ví dụ Keepalive: Duy trì kết nối / Giữ phiên; Cookies giữ là Cookie; Quota: Hạn mức; Account: Tài khoản).
- Trả về DUY NHẤT một JSON object có dạng {"chuỗi tiếng Trung gốc": "bản dịch tiếng Việt"}. Không thêm markdown backticks hay bất kỳ text nào khác ngoài JSON.

Danh sách các chuỗi cần dịch:
""" + json.dumps(batch, ensure_ascii=False)

    try:
        res = requests.post(
            URL,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "stream": False
            },
            timeout=60
        )
        if res.status_code == 200:
            content = res.json()["choices"][0]["message"]["content"].strip()
            # Clean markdown code block if present
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith("json"):
                    content = content[4:].strip()
            batch_result = json.loads(content)
            mapping.update(batch_result)
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
            print(f" -> Da luu {len(batch_result)} cum tu vao mapping.")
        else:
            print(f" -> Loi HTTP {res.status_code}: {res.text[:100]}")
    except Exception as e:
        print(f" -> Ngoai le: {e}")
    time.sleep(0.5)

print(f"Hoan tat dich! Tong mapping: {len(mapping)} cum tu.")
