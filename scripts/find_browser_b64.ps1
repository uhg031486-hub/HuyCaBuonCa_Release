$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
import base64
with open(r'C:\muse2api\engine.py', 'r', encoding='utf-8') as f:
    text = f.read()
import re
res = []
for m in re.finditer(r'cdp_port', text):
    start = max(0, m.start() - 100)
    end = min(len(text), m.end() + 200)
    res.append(text[start:end])
out = '\n=====\n'.join(res[:3])
print(base64.b64encode(out.encode('utf-8')).decode('ascii'))
"
}

Remove-PSSession $s
