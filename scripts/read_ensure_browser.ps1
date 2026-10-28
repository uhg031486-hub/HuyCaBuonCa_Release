$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
with open(r'C:\muse2api\engine.py', 'r', encoding='utf-8') as f:
    text = f.read()
import re
idx = text.find('def ensure_browser')
if idx != -1:
    print(text[idx:idx+800])
"
}

Remove-PSSession $s
