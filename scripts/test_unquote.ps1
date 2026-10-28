$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    C:\muse2api\venv\Scripts\python.exe -c "
import json, requests, urllib.parse

with open(r'C:\muse2api\data\accounts.json', 'r', encoding='utf-8') as f:
    accounts = json.load(f)

acc2 = [a for a in accounts if a.get('label') == 'ELLA2'][0]
cookies = acc2['cookies']

# 1. Thu unquote
unquoted_cookies = {k: urllib.parse.unquote(v) for k, v in cookies.items()}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'Origin': 'https://muse.ai',
    'Referer': 'https://muse.ai/thread/new',
    'Cookie': '; '.join(f'{k}={v}' for k, v in unquoted_cookies.items())
}
r1 = requests.get('https://muse.ai/api/session', headers=headers, timeout=10)
print('UNQUOTED STATUS:', r1.status_code, r1.text[:150])

# 2. Thu chi gui hatch_sess va datr
headers2 = dict(headers)
headers2['Cookie'] = f'hatch_sess={cookies[\"hatch_sess\"]}; datr={cookies.get(\"datr\", \"\")}'
r2 = requests.get('https://muse.ai/api/session', headers=headers2, timeout=10)
print('ONLY SESS+DATR STATUS:', r2.status_code, r2.text[:150])
"
}

Remove-PSSession $s
