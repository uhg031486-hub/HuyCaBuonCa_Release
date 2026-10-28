$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
with open(r'C:\Users\Administrator\AppData\Roaming\npm\node_modules\9router\app\.next-cli-build\server\app\api\models\custom\route.js', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
for l in lines:
    if 'INSERT' in l or 'SELECT' in l or 'UPDATE' in l or 'create' in l:
        print(l[:150])
"@
    Set-Content -Path "C:\muse2api\parse_sql.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\parse_sql.py"
}
