$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
with open(r'C:\Users\Administrator\AppData\Roaming\npm\node_modules\9router\app\.next-cli-build\server\app\api\models\custom\route.js', 'r', encoding='utf-8', errors='ignore') as f:
    c = f.read()
import re
print('Length:', len(c))
matches = re.findall(r'provider[a-zA-Z0-9_]*|custom[a-zA-Z0-9_]*', c, re.IGNORECASE)
print(list(set(matches))[:30])
"@
    Set-Content -Path "C:\muse2api\parse_custom_route.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\parse_custom_route.py"
}
