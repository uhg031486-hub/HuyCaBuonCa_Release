$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
import base64
with open(r'C:\muse2api\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'def chat_completions' in l or 'async def chat_completions' in l:
        chunk = ''.join(lines[i:i+60])
        print(base64.b64encode(chunk.encode('utf-8')).decode('ascii'))
        break
"
}

Remove-PSSession $s
