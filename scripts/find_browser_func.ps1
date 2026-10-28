$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
with open(r'C:\muse2api\engine.py', 'r', encoding='utf-8') as f:
    text = f.read()
import re
for m in re.finditer(r'def [a-zA-Z0-9_]*browser[a-zA-Z0-9_]*', text, re.IGNORECASE):
    print(m.group(0))
for m in re.finditer(r'cdp_port', text):
    start = max(0, m.start() - 100)
    end = min(len(text), m.end() + 200)
    print(text[start:end])
    print('='*40)
"
}

Remove-PSSession $s
