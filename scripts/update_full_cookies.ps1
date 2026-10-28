$sec = ConvertTo-SecureString 'Quanghuy1005@' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ('Administrator', $sec)
$opt = New-PSSessionOption -SkipCACheck -SkipCNCheck

Invoke-Command -ComputerName 100.92.145.57 -Credential $cred -UseSSL -SessionOption $opt -ScriptBlock {
    # 1. Cập nhật đầy đủ cookie cho muse2api (có thêm hatch_native_auth_device)
    $apiKey = "m2a_c88ad8240c6233938b2a8dfe15685d56fa8a6cb659bdd20f"
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "Content-Type" = "application/json"
    }

    $sessVal = 'ccc900aa-da2b-41b9-99ef-f6c80e5dadcc.v1%3Aa776mt0Jhq9y9ZnWM14gGW07ZM8Cs2hMOhcjEw7DS534gO6u76sypdp5p40TPK8hi50q5HEXQwcMlCmzsepJyXJcftrhTAti39zJwtdTSlsJfH_RngWflTG1FB2hv2OAjf4gMBk4G9dU3H1ExJd4cuefRZYaquIImaRZtLqQWo5JL74_DF6qTtovAEnIJaxRTiOM2ilrLiLZEGg7MdhPNLEG0k6KWHHvVRfezaZZEkonNpfCb16aXC-YPOgF0iFFF1en71Gufl83aYaH6aYiH2HyeIKpOuSmWAkPiQfH4MQ6Tw16v8BgWdP1PNgLZievggK2JXVPyhxTV1mHZh1gr9vRTRj8ViULSgFb8mC3tur4yOjqtXP0GZmyVmWhJfwluEx6otLDBvZVTj-z2EDVpuWq5X4PYqukeenKkPH-l8Py_DFGJaCb9QdMjUTM3C6gWTNYJQr1YRV8zyDC3tgetlU%3AUmrgE9CGiTqHGONQ%3A78jKF86m5i-IIDEobE55_Q.DWPfVZCjva-cq2NXxzWMhe96YxJmIoehFWEgINZarHs'
    $deviceVal = 'v1%3AUsd065LLPHKFRobEVcKe2qyN_gjxv4dG3vRNji3U70Zyl185Z7Wx9Rpvug%3AlgBqlJga0UTpLTPx%3AeZmkgWi6DFSXVs30el2_WA'

    $fullCookie = "hatch_sess=$sessVal; hatch_native_auth_device=$deviceVal; datr=WBnYaGhaS74p4XFIIsrQ7MOi"

    $body = @{
        label = "Ella_Full_Account"
        cookie_header = $fullCookie
    } | ConvertTo-Json

    Write-Host "1. Cap nhat Cookie day du vao muse2api..."
    try {
        $res = Invoke-RestMethod -Uri "http://127.0.0.1:18610/admin/accounts" -Method Post -Headers $headers -Body $body
        Write-Host "Ket qua:"
        $res | ConvertTo-Json
    } catch {
        Write-Host "Loi cap nhat: $_"
    }
}
