$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    C:\muse2api\venv\Scripts\python.exe -c "
import json
with open(r'C:\muse2api\data\accounts.json', 'r', encoding='utf-8') as f:
    accounts = json.load(f)
acc2 = [a for a in accounts if a.get('label') == 'ELLA2'][0]
print('ELLA2 HATCH_SESS:', acc2['cookies']['hatch_sess'][:100])
"
}

Remove-PSSession $s
