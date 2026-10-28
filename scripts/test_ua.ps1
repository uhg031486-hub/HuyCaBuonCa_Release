$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    C:\muse2api\venv\Scripts\python.exe -c "
import json
import requests

with open(r'C:\muse2api\data\accounts.json', 'r', encoding='utf-8') as f:
    accounts = json.load(f)

# Lấy ELLA2
acc2 = [a for a in accounts if a.get('label') == 'ELLA2'][0]
cookies = acc2['cookies']

uas = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
]

for ua in uas:
    headers = {
        'User-Agent': ua,
        'Origin': 'https://muse.ai',
        'Referer': 'https://muse.ai/thread/new',
        'Cookie': '; '.join(f'{k}={v}' for k, v in cookies.items() if v)
    }
    r = requests.get('https://muse.ai/api/session', headers=headers, timeout=10)
    print('UA:', ua[:30], '-> STATUS:', r.status_code, r.text[:150])
"
}

Remove-PSSession $s
