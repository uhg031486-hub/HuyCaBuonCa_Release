$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
import base64
with open(r'C:\muse2api\store.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Tìm đoạn pick_account
idx = text.find('def pick_account')
print(base64.b64encode(text[idx:idx+2500].encode('utf-8')).decode('ascii'))
"
}

Remove-PSSession $s
