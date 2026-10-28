$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
import sqlite3, json

conn = sqlite3.connect(r'C:\Users\Administrator\AppData\Roaming\9router\db\data.sqlite')

rows = conn.execute('SELECT id, provider, authType, name, data FROM providerConnections LIMIT 5').fetchall()
for r in rows:
    try:
        data_obj = json.loads(r[4])
    except Exception:
        data_obj = r[4]
    print({
        'id': r[0],
        'provider': r[1],
        'authType': r[2],
        'name': r[3],
        'data_keys': list(data_obj.keys()) if isinstance(data_obj, dict) else str(data_obj)[:50]
    })
"@
    Set-Content -Path "C:\muse2api\sample_conn.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\sample_conn.py"
}
