$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
import base64
with open(r'C:\muse2api\app.py', 'r', encoding='utf-8') as f:
    text = f.read()
import re
for m in re.finditer(r'pick_account', text):
    start = max(0, m.start() - 200)
    end = min(len(text), m.end() + 300)
    print('--- MATCH ---')
    print(text[start:end])
"
}

Remove-PSSession $s
