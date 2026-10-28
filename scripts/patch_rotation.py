import os
import re

base_dir = r"C:\muse2api"

# 1. Cập nhật .env
env_file = os.path.join(base_dir, ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        env_content = f.read()
    if "MUSE2API_ROTATE_REQUESTS" not in env_content:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write("\nMUSE2API_ROTATE_REQUESTS=25\n")
        print("[+] Da them MUSE2API_ROTATE_REQUESTS=25 vao .env")

# 2. Cập nhật config.py
cfg_file = os.path.join(base_dir, "config.py")
with open(cfg_file, "r", encoding="utf-8") as f:
    cfg_code = f.read()
if "rotate_requests" not in cfg_code:
    old_target = "max_concurrency: int = field"
    new_addition = 'rotate_requests: int = field(default_factory=lambda: int(_env("MUSE2API_ROTATE_REQUESTS", "25")))\n    max_concurrency: int = field'
    cfg_code = cfg_code.replace(old_target, new_addition)
    with open(cfg_file, "w", encoding="utf-8") as f:
        f.write(cfg_code)
    print("[+] Da cap nhat config.py")

# 3. Cập nhật store.py
store_file = os.path.join(base_dir, "store.py")
with open(store_file, "r", encoding="utf-8") as f:
    store_code = f.read()

old_pick = """                        if not rotate or sticky_n < 15:
                            self._sticky_id = preferred_id
                            self._sticky_count = sticky_n + 1"""

new_pick = """                        # Kiem tra quota: neu da dung het 100% thi lap tuc dao tai khoan khac!
                        quota = a.get("quota") or {}
                        used_pct = quota.get("weekly_used_pct")
                        if used_pct is not None and used_pct >= 100:
                            break
                        max_sticky = getattr(self.cfg, "rotate_requests", 25)
                        # Xoay vong sau moi 25 requests (tu 15-30 request) de chong Meta soi
                        if not rotate or sticky_n < max_sticky:
                            self._sticky_id = preferred_id
                            self._sticky_count = sticky_n + 1"""

if old_pick in store_code:
    store_code = store_code.replace(old_pick, new_pick)
    # Bo sung loc tai khoan chua het quota vao healthy candidates
    old_cand = 'healthy = [a for a in live if a.get("ok") is not False]'
    new_cand = 'healthy = [a for a in live if a.get("ok") is not False and (not (a.get("quota") or {}).get("weekly_used_pct") or (a.get("quota") or {}).get("weekly_used_pct", 0) < 100)]'
    store_code = store_code.replace(old_cand, new_cand)
    with open(store_file, "w", encoding="utf-8") as f:
        f.write(store_code)
    print("[+] Da cap nhat store.py: Xoay sau 25 requests hoac khi het 100% quota")

# 4. Cập nhật app.py: chuyển nhãn tiếng Trung sang định dạng rõ ràng
app_file = os.path.join(base_dir, "app.py")
with open(app_file, "r", encoding="utf-8") as f:
    app_code = f.read()

app_code = app_code.replace('parts.append(f"背景与任务设定：\\n{sys_text}")', 'parts.append(f"[QUY TAC HE THONG & BANG NHAN VAT]:\\n{sys_text}")')
app_code = app_code.replace('label = "助手" if role == "assistant" else "用户"', 'label = "Ban dich truoc" if role == "assistant" else "Nguoi dung"')
app_code = app_code.replace('parts.append(f"{label}：\\n{text}")', 'parts.append(f"[{label}]:\\n{text}")')

with open(app_file, "w", encoding="utf-8") as f:
    f.write(app_code)
print("[+] Da cap nhat app.py: Ban giao ngu canh ro rang khi dao tai khoan")

print("HOAN TAT TOAN BO PATCH!")
