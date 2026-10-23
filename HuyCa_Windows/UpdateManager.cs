using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;

namespace HuyCa_Windows;

public static class UpdateManager
{
    private static readonly string[] UPDATE_CONFIG_URLS = new[]
    {
        "https://raw.githubusercontent.com/uhg031486-hub/HuyCaBuonCa_Release/main/version.json",
        "https://cdn.jsdelivr.net/gh/uhg031486-hub/HuyCaBuonCa_Release@main/version.json",
        "https://fastly.jsdelivr.net/gh/uhg031486-hub/HuyCaBuonCa_Release@main/version.json"
    };

    public const int CURRENT_VERSION_CODE = 16;
    public const string CURRENT_VERSION_NAME = "2.5";

    public static async Task CheckForUpdateAsync(Window owner, bool silent = false)
    {
        try
        {
            using var client = new HttpClient();
            client.Timeout = TimeSpan.FromSeconds(10);
            client.DefaultRequestHeaders.Add("User-Agent", "HuyCa-Windows/2.5");
            client.DefaultRequestHeaders.Add("Cache-Control", "no-cache");

            string? response = null;
            foreach (var url in UPDATE_CONFIG_URLS)
            {
                try
                {
                    response = await client.GetStringAsync(url);
                    if (!string.IsNullOrEmpty(response)) break;
                }
                catch
                {
                    // Thử mirror tiếp theo nếu bị chặn DNS
                }
            }

            if (string.IsNullOrEmpty(response))
            {
                throw new Exception("Không thể kết nối đến máy chủ cập nhật (đã thử cả máy chủ chính và các CDN sao lưu).");
            }

            using var doc = JsonDocument.Parse(response);
            var root = doc.RootElement;

            bool isMaintenanceLocked = root.TryGetProperty("isMaintenanceLocked", out var lockProp) && lockProp.GetBoolean();
            string maintenanceMessage = root.TryGetProperty("maintenanceMessage", out var msgProp) ? msgProp.GetString() ?? "" : "Hệ thống đang bảo trì nội bộ. Vui lòng quay lại sau!";

            if (isMaintenanceLocked)
            {
                owner.Dispatcher.Invoke(() =>
                {
                    MessageBox.Show(
                        owner,
                        $"🔒 THÔNG BÁO BẢO TRÌ NỘI BỘ\n\n{maintenanceMessage}",
                        "Bảo Trì Nội Bộ - Huy Cá",
                        MessageBoxButton.OK,
                        MessageBoxImage.Warning
                    );
                    Application.Current.Shutdown();
                });
                return;
            }

            int remoteCode = root.TryGetProperty("versionCode", out var codeProp) ? codeProp.GetInt32() : 0;
            string remoteName = root.TryGetProperty("versionName", out var nameProp) ? nameProp.GetString() ?? "" : "";
            string title = root.TryGetProperty("title", out var titleProp) ? titleProp.GetString() ?? "Phiên bản mới" : "Phiên bản mới";
            string changelog = root.TryGetProperty("changelog", out var logProp) ? logProp.GetString() ?? "" : "";
            string zipUrl = root.TryGetProperty("windowsZipUrl", out var urlProp) ? urlProp.GetString() ?? "" : "";

            if (remoteCode > CURRENT_VERSION_CODE && !string.IsNullOrEmpty(zipUrl))
            {
                owner.Dispatcher.Invoke(() =>
                {
                    string msg = $"🚀 PHÁT HIỆN BẢN CẬP NHẬT MỚI:\n{title} (v{remoteName})\n\n" +
                                 $"Nội dung nâng cấp:\n{changelog}\n\n" +
                                 $"Bạn có muốn tự động tải và cập nhật ứng dụng ngay bây giờ?";

                    var result = MessageBox.Show(
                        owner,
                        msg,
                        "Cập Nhật Huy Cá",
                        MessageBoxButton.YesNo,
                        MessageBoxImage.Information
                    );

                    if (result == MessageBoxResult.Yes)
                    {
                        _ = DownloadAndApplyUpdateAsync(owner, zipUrl, remoteName);
                    }
                });
            }
            else if (!silent)
            {
                owner.Dispatcher.Invoke(() =>
                {
                    MessageBox.Show(
                        owner,
                        $"Ứng dụng đang ở phiên bản mới nhất (Huy Cá v{CURRENT_VERSION_NAME}).",
                        "Huy Cá",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information
                    );
                });
            }
        }
        catch (Exception ex)
        {
            if (!silent)
            {
                owner.Dispatcher.Invoke(() =>
                {
                    MessageBox.Show(
                        owner,
                        $"Không thể kiểm tra cập nhật: {ex.Message}\nVui lòng kiểm tra lại kết nối mạng!",
                        "Huy Cá",
                        MessageBoxButton.OK,
                        MessageBoxImage.Warning
                    );
                });
            }
        }
    }

    private static async Task DownloadAndApplyUpdateAsync(Window owner, string zipUrl, string remoteVersionName)
    {
        string tempDir = Path.Combine(Path.GetTempPath(), "HuyCa_Update");
        string zipPath = Path.Combine(tempDir, "HuyCa_New.zip");
        string batPath = Path.Combine(tempDir, "apply_update.cmd");
        string appDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);

        try
        {
            Directory.CreateDirectory(tempDir);
            if (File.Exists(zipPath)) File.Delete(zipPath);

            owner.Dispatcher.Invoke(() =>
            {
                MessageBox.Show(
                    owner,
                    $"Đang bắt đầu tải bản cập nhật Huy Cá v{remoteVersionName} trong nền...\nỨng dụng sẽ tự động khởi động lại sau khi hoàn tất.",
                    "Cập Nhật Huy Cá",
                    MessageBoxButton.OK,
                    MessageBoxImage.Information
                );
            });

            using (var client = new HttpClient())
            {
                client.Timeout = TimeSpan.FromMinutes(10);
                var data = await client.GetByteArrayAsync(zipUrl);
                await File.WriteAllBytesAsync(zipPath, data);
            }

            // Tạo tập lệnh tự động cập nhật và khởi động lại
            string batContent = 
                "@echo off\r\n" +
                "chcp 65001 > nul\r\n" +
                "title Dang Cap Nhat Huy Ca...\r\n" +
                "echo ====================================================\r\n" +
                "echo    Dang cap nhat Huy Ca len phien ban moi nhat...\r\n" +
                "echo ====================================================\r\n" +
                "timeout /t 2 /nobreak > nul\r\n" +
                $"powershell -NoProfile -Command \"Expand-Archive -Path '{zipPath}' -DestinationPath '{appDir}' -Force\"\r\n" +
                "echo Hoan tat cap nhat! Dang khoi dong lai ung dung...\r\n" +
                $"start \"\" \"{Path.Combine(appDir, "HuyCa.exe")}\"\r\n" +
                "exit\r\n";

            await File.WriteAllTextAsync(batPath, batContent);

            var psi = new ProcessStartInfo
            {
                FileName = batPath,
                UseShellExecute = true,
                CreateNoWindow = false
            };
            Process.Start(psi);

            owner.Dispatcher.Invoke(() =>
            {
                Application.Current.Shutdown();
            });
        }
        catch (Exception ex)
        {
            owner.Dispatcher.Invoke(() =>
            {
                var fallback = MessageBox.Show(
                    owner,
                    $"Lỗi tự động cập nhật: {ex.Message}\n\nBạn có muốn mở trình duyệt để tải bản mới về thủ công không?",
                    "Cập Nhật Huy Cá",
                    MessageBoxButton.YesNo,
                    MessageBoxImage.Warning
                );

                if (fallback == MessageBoxResult.Yes)
                {
                    try
                    {
                        Process.Start(new ProcessStartInfo
                        {
                            FileName = zipUrl,
                            UseShellExecute = true
                        });
                    }
                    catch { }
                }
            });
        }
    }
}
