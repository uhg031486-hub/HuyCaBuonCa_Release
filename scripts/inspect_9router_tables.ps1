$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
import sqlite3, json
conn = sqlite3.connect(r'C:\Users\Administrator\AppData\Roaming\9router\db\data.sqlite')

print('--- providerConnections ---')
for c in conn.execute('PRAGMA table_info(providerConnections)').fetchall():
    print(c)
rows = conn.execute('SELECT * FROM providerConnections LIMIT 2').fetchall()
print('Sample rows:', rows)

print('--- providerNodes ---')
for c in conn.execute('PRAGMA table_info(providerNodes)').fetchall():
    print(c)
rows2 = conn.execute('SELECT * FROM providerNodes LIMIT 2').fetchall()
print('Sample rows:', rows2)
"@
    Set-Content -Path "C:\muse2api\inspect_9router_tables.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\inspect_9router_tables.py"
}
