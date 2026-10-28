$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    $engine = Get-Content -Path "C:\muse2api\engine.py" -Raw -Encoding UTF8
    $lines = $engine -split "`n"
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match "api/session") {
            Write-Host "FOUND AT LINE $i"
            $start = [Math]::Max(0, $i - 10)
            $end = [Math]::Min($lines.Length - 1, $i + 20)
            for ($j = $start; $j -le $end; $j++) {
                Write-Host "$($j+1): $($lines[$j])"
            }
        }
    }
}

Remove-PSSession $s
