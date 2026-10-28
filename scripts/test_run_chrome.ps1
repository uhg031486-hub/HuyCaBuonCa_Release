$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
$s = New-PSSession -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt

Invoke-Command -Session $s -ScriptBlock {
    Write-Host "Chrome 64-bit: $(Test-Path 'C:\Program Files\Google\Chrome\Application\chrome.exe')"
    Write-Host "Chrome 32-bit: $(Test-Path 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')"
    
    # Chạy thử Chrome xem nó có chạy được không
    $proc = Start-Process -FilePath "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--headless=new", "--no-sandbox", "--disable-gpu", "--remote-debugging-port=19210", "about:blank" -PassThru
    Start-Sleep -Seconds 3
    Write-Host "Process Id: $($proc.Id), HasExited: $($proc.HasExited)"
    
    # Test thử port 19210
    try {
        $cdp = Invoke-RestMethod -Uri "http://127.0.0.1:19210/json/version" -TimeoutSec 3
        Write-Host "CDP KET NOI OK: $($cdp.Browser)"
    } catch {
        Write-Host "CDP Loi: $_"
    }
}

Remove-PSSession $s
