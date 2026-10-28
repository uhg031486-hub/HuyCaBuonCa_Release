$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
import sqlite3, json

conn = sqlite3.connect(r'C:\Users\Administrator\AppData\Roaming\9router\db\data.sqlite')

rows = conn.execute('SELECT provider, authType, name, data FROM providerConnections').fetchall()
providers = set(r[0] for r in rows)
print('Existing providers:', list(providers)[:20])

for r in rows:
    if r[1] == 'api-key' or 'custom' in r[0].lower():
        print('Found api-key provider:', r[0], r[1], r[2], r[3][:100])
        break
"@
    Set-Content -Path "C:\muse2api\find_providers.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\find_providers.py"
}
