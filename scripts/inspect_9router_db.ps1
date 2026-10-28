$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\AppData\Roaming\9router\db\data.sqlite')
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("TABLES:", tables)

for t in ['providers', 'custom_providers', 'models']:
    if t in tables:
        cols = [c[1] for c in conn.execute(f"PRAGMA table_info({t})").fetchall()]
        print(f"COLS in {t}:", cols)
        rows = conn.execute(f"SELECT * FROM {t} LIMIT 3").fetchall()
        print(f"SAMPLE {t}:", rows)
"@
    Set-Content -Path "C:\muse2api\inspect_9router.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\inspect_9router.py"
}
