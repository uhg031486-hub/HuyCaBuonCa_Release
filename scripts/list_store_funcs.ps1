$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    python -c "
with open(r'C:\muse2api\store.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if l.strip().startswith('def '):
        print(f'{i+1}: {l.strip()}')
"
}

Remove-PSSession $s
