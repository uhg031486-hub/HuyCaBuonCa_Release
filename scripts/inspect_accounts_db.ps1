$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
import json
with open(r'C:\muse2api\data\accounts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for a in data.get('accounts', []):
    print('ID:', a.get('id'), 'Label:', a.get('label'), 'OK:', a.get('ok'), 'Note:', a.get('note'))
    cookies = a.get('cookies', {})
    print('Cookie keys:', list(cookies.keys()))
    print('hatch_sess prefix:', cookies.get('hatch_sess', '')[:30] if cookies.get('hatch_sess') else 'None')
    print('hatch_vml prefix:', cookies.get('hatch_vml', '')[:30] if cookies.get('hatch_vml') else 'None')
    print('-'*40)
"
}

Remove-PSSession $s
