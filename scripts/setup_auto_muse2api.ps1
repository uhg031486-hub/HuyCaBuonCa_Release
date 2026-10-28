$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    # 1. Tạo file startup_muse2api.vbs
    $vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\muse2api"
WshShell.Run "C:\muse2api\venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 18610", 0, False
"@
    Set-Content -Path "C:\muse2api\start_hidden.vbs" -Value $vbsContent -Encoding ASCII

    # 2. Đưa shortcut vào Startup của Windows để tự chạy vĩnh viễn khi boot VPS
    $startupFolder = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
    $wsh = New-Object -ComObject WScript.Shell
    $shortcut = $wsh.CreateShortcut("$startupFolder\Muse2API.lnk")
    $shortcut.TargetPath = "wscript.exe"
    $shortcut.Arguments = "`"C:\muse2api\start_hidden.vbs`""
    $shortcut.WorkingDirectory = "C:\muse2api"
    $shortcut.Save()

    # 3. Kích hoạt chạy ngay bây giờ
    Start-Process "wscript.exe" -ArgumentList "`"C:\muse2api\start_hidden.vbs`""
    Start-Sleep -Seconds 5

    # 4. Kiểm tra sức khỏe endpoint
    $res = Invoke-RestMethod -Uri 'http://127.0.0.1:18610/healthz' -Method Get
    Write-Host "Muse2API khoi chay ngam thanh cong! Status: $($res.status)"
}
