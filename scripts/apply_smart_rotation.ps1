$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    # 1. Cập nhật .env với cấu hình xoay vòng 25 requests
    $envPath = "C:\muse2api\.env"
    $envContent = Get-Content $envPath -Raw -Encoding UTF8
    if ($envContent -notmatch "MUSE2API_ROTATE_REQUESTS") {
        $envContent += "`nMUSE2API_ROTATE_REQUESTS=25`n"
        Set-Content -Path $envPath -Value $envContent -Encoding UTF8
    }

    # 2. Cập nhật config.py
    C:\muse2api\venv\Scripts\python.exe -c "
with open(r'C:\muse2api\config.py', 'r', encoding='utf-8') as f:
    text = f.read()

if 'rotate_requests' not in text:
    old_line = 'max_concurrency: int = field'
    new_code = '''rotate_requests: int = field(default_factory=lambda: int(_env(\"MUSE2API_ROTATE_REQUESTS\", \"25\")))\n    max_concurrency: int = field'''
    text = text.replace(old_line, new_code)
    with open(r'C:\muse2api\config.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Da cap nhat config.py voi rotate_requests=25')
else:
    print('config.py da co rotate_requests')
"

    # 3. Cập nhật store.py với logic: Xoay sau 15-30 requests HOẶC khi hết hạn mức (Quota 100%)
    C:\muse2api\venv\Scripts\python.exe -c "
with open(r'C:\muse2api\store.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Logic mới cho pick_account:
# Kiểm tra quota (weekly_used_pct >= 100) và số lần dùng liên tiếp sticky_n < rotate_requests (15-30)
old_pick_block = '''            if preferred_id and not force_rotate:
                for a in live:
                    if a[\"id\"] == preferred_id and a.get(\"ok\") is not False:
                        sticky_n = getattr(self, \"_sticky_count\", 0) if getattr(self, \"_sticky_id\", None) == preferred_id else 0
                        if not rotate or sticky_n < 15:
                            self._sticky_id = preferred_id
                            self._sticky_count = sticky_n + 1
                            if record_use:
                                a[\"last_used\"] = time.time()
                                a[\"use_count\"] = a.get(\"use_count\", 0) + 1
                                _write(self.cfg.accounts_file, self.accounts)
                            return a'''

new_pick_block = '''            max_sticky = getattr(self.cfg, \"rotate_requests\", 25)
            if preferred_id and not force_rotate:
                for a in live:
                    if a[\"id\"] == preferred_id and a.get(\"ok\") is not False:
                        # Kiem tra quota: neu da het han muc 100% thi lap tuc dao tai khoan khac!
                        quota = a.get(\"quota\") or {}
                        used_pct = quota.get(\"weekly_used_pct\")
                        if used_pct is not None and used_pct >= 100:
                            break
                        sticky_n = getattr(self, \"_sticky_count\", 0) if getattr(self, \"_sticky_id\", None) == preferred_id else 0
                        # Xoay vong sau moi max_sticky (mac dinh 25 requests, tu 15-30)
                        if not rotate or sticky_n < max_sticky:
                            self._sticky_id = preferred_id
                            self._sticky_count = sticky_n + 1
                            if record_use:
                                a[\"last_used\"] = time.time()
                                a[\"use_count\"] = a.get(\"use_count\", 0) + 1
                                _write(self.cfg.accounts_file, self.accounts)
                            return a'''

if old_pick_block in code:
    code = code.replace(old_pick_block, new_pick_block)
    # Lọc candidates ưu tiên tài khoản chưa hết 100% hạn mức
    old_cand = '''            healthy = [a for a in live if a.get(\"ok\") is not False]'''
    new_cand = '''            healthy = [a for a in live if a.get(\"ok\") is not False and (not (a.get(\"quota\") or {}).get(\"weekly_used_pct\") or (a.get(\"quota\") or {}).get(\"weekly_used_pct\", 0) < 100)]'''
    code = code.replace(old_cand, new_cand)
    with open(r'C:\muse2api\store.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print('Da cap nhat store.py voi logic xoay vong 25 requests va dao khi het han muc')
else:
    print('Block code trong store.py da duoc cap nhat hoac khong khop')
"

    # 4. Cập nhật build_chat_prompt trong app.py để tài khoản mới hiểu 100% ngữ cảnh tiếng Việt
    C:\muse2api\venv\Scripts\python.exe -c "
with open(r'C:\muse2api\app.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_format = '''    parts = []
    if system:
        sys_text = \"\\n\\n\".join(system)
        sys_text = sys_text.replace(\"danger-full-access\", \"standard-workspace-access\")
        parts.append(f\"背景与任务设定：\\n{sys_text}\")
    for role, text_part in turns:
        label = \"助手\" if role == \"assistant\" else \"用户\"
        parts.append(f\"{label}：\\n{text_part}\")
    return \"\\n\\n\".join(parts)'''

# Tim doan tuong tu
import re
pattern = r'parts = \[\]\s+if system:.*?parts\.append\(f\"背景与任务设定：\\n\{sys_text\}\"\).*?return \"\\n\\n\"\.join\(parts\)'
new_format = '''parts = []
    if system:
        sys_text = \"\\n\\n\".join(system)
        sys_text = sys_text.replace(\"danger-full-access\", \"standard-workspace-access\")
        parts.append(f\"[CHỈ DẪN HỆ THỐNG / QUY TẮC NHÂN VẬT]:\\n{sys_text}\")
    for role, text_part in turns:
        label = \"Trợ lý (Bản dịch trước)\" if role == \"assistant\" else \"Người dùng\"
        parts.append(f\"[{label}]:\\n{text_part}\")
    return \"\\n\\n\".join(parts)'''

text = re.sub(pattern, new_format, text, flags=re.DOTALL)
with open(r'C:\muse2api\app.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Da cap nhat build_chat_prompt trong app.py sang dinh dang ro rang')
"

    # 5. Khởi động lại dịch vụ Muse2API_Service trên VPS
    Write-Host 'Dang khoi dong lai dich vu Muse2API_Service...'
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Start-ScheduledTask -TaskName "Muse2API_Service"
    Start-Sleep -Seconds 4

    # Kiểm tra cổng 18610
    Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq 18610 } | Select-Object LocalAddress, LocalPort, OwningProcess
}

Remove-PSSession $s
