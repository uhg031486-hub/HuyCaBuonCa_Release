$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Set-Location "C:\muse2api"
    Write-Host "=== TEST CHAY TRUC TIEP PYTHON UVICORN DE XEM LOG LOI ==="
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "C:\muse2api\venv\Scripts\python.exe"
    $pinfo.Arguments = "-m uvicorn app:app --host 0.0.0.0 --port 18610"
    $pinfo.WorkingDirectory = "C:\muse2api"
    $pinfo.RedirectStandardError = $true
    $pinfo.RedirectStandardOutput = $true
    $pinfo.UseShellExecute = $false
    
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $p.Start() | Out-Null
    Start-Sleep -Seconds 5
    if ($p.HasExited) {
        Write-Host "Process da thoat voi ma: $($p.ExitCode)"
        Write-Host "STDERR: $($p.StandardError.ReadToEnd())"
        Write-Host "STDOUT: $($p.StandardOutput.ReadToEnd())"
    } else {
        Write-Host "Process van dang chay tot! PID: $($p.Id)"
        Write-Host "STDOUT hien tai: $($p.StandardOutput.ReadLine())"
    }
}

Remove-PSSession $s
