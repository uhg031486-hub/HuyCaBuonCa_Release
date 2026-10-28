$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\AppData\Roaming\9router\db\data.sqlite')
for r in conn.execute('SELECT key, value FROM settings').fetchall():
    print(r[0], '-->', str(r[1])[:80])
"@
    Set-Content -Path "C:\muse2api\read_settings.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\read_settings.py"
}
