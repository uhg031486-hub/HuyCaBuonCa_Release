$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $script = @"
with open(r'C:\Users\Administrator\AppData\Roaming\npm\node_modules\9router\app\.next-cli-build\server\app\api\providers\route.js', 'r', encoding='utf-8', errors='ignore') as f:
    c = f.read()
import re
print('Route providers length:', len(c))
# tìm schema hoặc request body format của POST /api/providers
idx = c.find('POST')
if idx != -1:
    print(c[idx:idx+400])
else:
    print('POST not found directly, looking for export async function POST')
    idx2 = c.find('function POST')
    if idx2 != -1:
        print(c[idx2:idx2+400])
"@
    Set-Content -Path "C:\muse2api\parse_providers_route.py" -Value $script -Encoding UTF8
    & "C:\muse2api\venv\Scripts\python.exe" "C:\muse2api\parse_providers_route.py"
}
