import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def search_text(pattern):
    print(f"=== SEARCH: {pattern} ===")
    matches = []
    for root, dirs, files in os.walk('.'):
        if any(x in root for x in ['.git', 'node_modules', '.gradle', 'build', '.gemini']):
            continue
        for f in files:
            if f.endswith(('.js', '.html', '.kt', '.xml', '.json', '.css')):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                        c = file.read()
                        if pattern.lower() in c.lower():
                            matches.append(fp)
                except Exception:
                    pass
    for m in matches:
        print(f"  -> {m}")

search_text("Nhắc Tôi")
search_text("4 Server")
search_text("Lịch Thi Đấu & Bóng Đá")
search_text("FootballMatch")
