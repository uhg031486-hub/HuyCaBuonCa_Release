$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    $apiKey = "m2a_c88ad8240c6233938b2a8dfe15685d56fa8a6cb659bdd20f"
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "Content-Type" = "application/json"
    }

    $sessVal = 'ccc900aa-da2b-41b9-99ef-f6c80e5dadcc.v1%3Aa776mt0Jhq9y9ZnWM14gGW07ZM8Cs2hMOhcjEw7DS534gO6u76sypdp5p40TPK8hi50q5HEXQwcMlCmzsepJyXJcftrhTAti39zJwtdTSlsJfH_RngWflTG1FB2hv2OAjf4gMBk4G9dU3H1ExJd4cuefRZYaquIImaRZtLqQWo5JL74_DF6qTtovAEnIJaxRTiOM2ilrLiLZEGg7MdhPNLEG0k6KWHHvVRfezaZZEkonNpfCb16aXC-YPOgF0iFFF1en71Gufl83aYaH6aYiH2HyeIKpOuSmWAkPiQfH4MQ6Tw16v8BgWdP1PNgLZievggK2JXVPyhxTV1mHZh1gr9vRTRj8ViULSgFb8mC3tur4yOjqtXP0GZmyVmWhJfwluEx6otLDBvZVTj-z2EDVpuWq5X4PYqukeenKkPH-l8Py_DFGJaCb9QdMjUTM3C6gWTNYJQr1YRV8zyDC3tgetlU%3AUmrgE9CGiTqHGONQ%3A78jKF86m5i-IIDEobE55_Q.DWPfVZCjva-cq2NXxzWMhe96YxJmIoehFWEgINZarHs'
    
    $cookieHeader = "hatch_sess=$sessVal; datr=WBnYaGhaS74p4XFIIsrQ7MOi"

    $body = @{
        label = "Ella_Account_1"
        cookie_header = $cookieHeader
    } | ConvertTo-Json

    Write-Host "Dang them tai khoan vao muse2api voi Key tu sinh..."
    try {
        $res = Invoke-RestMethod -Uri "http://127.0.0.1:18610/admin/accounts" -Method Post -Headers $headers -Body $body
        Write-Host "KET QUA THEM TAI KHOAN:"
        $res | ConvertTo-Json
    } catch {
        Write-Host "Loi khi goi API: $_"
    }

    Write-Host "`n=== DANH SACH TAI KHOAN TRONG POOL ==="
    try {
        $list = Invoke-RestMethod -Uri "http://127.0.0.1:18610/admin/accounts" -Method Get -Headers $headers
        $list.accounts | Format-Table -AutoSize
    } catch {
        Write-Host "Loi lay danh sach: $_"
    }
}
