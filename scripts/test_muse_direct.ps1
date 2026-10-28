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

for a in accounts:
    print('ACCOUNT:', a.get('label'), a.get('id'))
    cookies = a.get('cookies', {})
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items() if v)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Origin': 'https://muse.ai',
        'Referer': 'https://muse.ai/thread/new',
        'Cookie': cookie_str
    }
    try:
        r = requests.get('https://muse.ai/api/session', headers=headers, timeout=10)
        print('Status code:', r.status_code)
        print('Response text:', r.text[:200])
    except Exception as e:
        print('Error:', e)
    print('='*50)
"
}

Remove-PSSession $s
