$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
import base64
with open(r'C:\muse2api\store.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
# In đoạn pick_account từ dòng 147 đến 215
chunk = ''.join(lines[146:215])
print(base64.b64encode(chunk.encode('utf-8')).decode('ascii'))
"
}

Remove-PSSession $s
