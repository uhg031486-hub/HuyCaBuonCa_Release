$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    C:\muse2api\venv\Scripts\python.exe -c "
import json

with open(r'C:\muse2api\data\accounts.json', 'r', encoding='utf-8') as f:
    accounts = json.load(f)

for a in accounts:
    print('ACCOUNT:', a.get('label'), a.get('id'), 'Created:', a.get('created_at'))
    cookies = a.get('cookies', {})
    for k, v in cookies.items():
        print(f'  {k}: {v[:40]}... (len={len(v)})')
"
}

Remove-PSSession $s
