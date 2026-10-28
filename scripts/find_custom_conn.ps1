$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
import sqlite3, json

conn = sqlite3.connect(r'C:\Users\Administrator\AppData\Roaming\9router\db\data.sqlite')

rows = conn.execute('SELECT id, provider, authType, name, data FROM providerConnections').fetchall()
customs = [r for r in rows if 'custom' in r[1].lower() or 'openai' in r[1].lower()]
print(f'Total connections: {len(rows)}')
print(f'Custom connections found: {len(customs)}')
for c in customs:
    print(c[0], c[1], c[2], c[3], c[4][:150])
"@
    Set-Content -Path "C:\muse2api\sample_custom.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\sample_custom.py"
}
