using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Text.Json;
using System.Threading;
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
            using var client = CreateDoHHttpClient(TimeSpan.FromSeconds(12));

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
                    // Thử mirror tiếp theo
                }
            }

            if (string.IsNullOrEmpty(response))
            {
                throw new Exception("Không thể kết nối đến máy chủ cập nhật (đã thử cả DoH và Mirrors).");
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

            using (var client = CreateDoHHttpClient(TimeSpan.FromMinutes(10)))
            {
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

    /// <summary>
    /// Khởi tạo HttpClient với cơ chế DoH (DNS over HTTPS) tự động:
    /// Nếu DNS mạng công ty chặn domain (như github.com hay raw.githubusercontent.com),
    /// HttpClient sẽ tự động truy vấn địa chỉ IP qua Cloudflare / Google DoH bảo mật.
    /// </summary>
    public static HttpClient CreateDoHHttpClient(TimeSpan? timeout = null)
    {
        var handler = new SocketsHttpHandler
        {
            ConnectCallback = async (context, cancellationToken) =>
            {
                var host = context.DnsEndPoint.Host;
                var port = context.DnsEndPoint.Port;

                IPAddress[]? ips = null;

                // 1. Thử phân giải DNS hệ thống trước
                try
                {
                    var resolved = await Dns.GetHostAddressesAsync(host, cancellationToken);
                    if (resolved != null && resolved.Length > 0 && !resolved.Any(ip => ip.Equals(IPAddress.Any) || IPAddress.IsLoopback(ip)))
                    {
                        ips = resolved;
                    }
                }
                catch
                {
                    // Lỗi DNS công ty chặn -> Chuyển sang DoH
                }

                // 2. Nếu DNS hệ thống bị chặn hoặc không có IP hợp lệ, dùng DoH Cloudflare & Google
                if (ips == null || ips.Length == 0)
                {
                    ips = await ResolveViaDoHAsync(host, cancellationToken);
                }

                var socket = new Socket(SocketType.Stream, ProtocolType.Tcp) { NoDelay = true };
                try
                {
                    await socket.ConnectAsync(ips, port, cancellationToken);
                    return new NetworkStream(socket, ownsSocket: true);
                }
                catch
                {
                    socket.Dispose();
                    throw;
                }
            }
        };

        var client = new HttpClient(handler);
        client.Timeout = timeout ?? TimeSpan.FromSeconds(15);
        client.DefaultRequestHeaders.Add("User-Agent", "HuyCa-Windows/2.5");
        return client;
    }

    private static readonly ConcurrentDictionary<string, (IPAddress[] ips, DateTime expiry)> _dnsCache = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>
    /// Phân giải tên miền qua Cloudflare (1.1.1.1) và Google (8.8.8.8) bằng HTTPS
    /// Hoàn toàn không phụ thuộc vào máy chủ DNS của công ty.
    /// Có bộ đệm DNS lưu tạm 10 phút giúp video HLS/M3U8 tải tức thì không có độ trễ.
    /// </summary>
    public static async Task<IPAddress[]> ResolveViaDoHAsync(string host, CancellationToken ct)
    {
        if (IPAddress.TryParse(host, out var directIp))
        {
            return new[] { directIp };
        }

        if (_dnsCache.TryGetValue(host, out var cached) && DateTime.UtcNow < cached.expiry)
        {
            return cached.ips;
        }

        var dohEndpoints = new[]
        {
            $"https://1.1.1.1/dns-query?name={Uri.EscapeDataString(host)}&type=A",
            $"https://1.0.0.1/dns-query?name={Uri.EscapeDataString(host)}&type=A",
            $"https://8.8.8.8/resolve?name={Uri.EscapeDataString(host)}&type=A",
            $"https://8.8.4.4/resolve?name={Uri.EscapeDataString(host)}&type=A"
        };

        using var handler = new SocketsHttpHandler
        {
            SslOptions = new System.Net.Security.SslClientAuthenticationOptions
            {
                RemoteCertificateValidationCallback = (sender, cert, chain, errors) => true
            }
        };
        using var rawClient = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(5) };
        rawClient.DefaultRequestHeaders.Add("Accept", "application/dns-json, application/json");
        rawClient.DefaultRequestHeaders.Add("User-Agent", "HuyCa-DoH/1.0");

        foreach (var url in dohEndpoints)
        {
            try
            {
                var jsonStr = await rawClient.GetStringAsync(url, ct);
                using var doc = JsonDocument.Parse(jsonStr);
                if (doc.RootElement.TryGetProperty("Answer", out var answer) && answer.ValueKind == JsonValueKind.Array)
                {
                    var ipList = new List<IPAddress>();
                    foreach (var item in answer.EnumerateArray())
                    {
                        if (item.TryGetProperty("data", out var dataProp))
                        {
                            var ipStr = dataProp.GetString();
                            if (!string.IsNullOrEmpty(ipStr) && IPAddress.TryParse(ipStr, out var ip))
                            {
                                ipList.Add(ip);
                            }
                        }
                    }
                    if (ipList.Count > 0)
                    {
                        var res = ipList.ToArray();
                        _dnsCache[host] = (res, DateTime.UtcNow.AddMinutes(10));
                        return res;
                    }
                }
            }
            catch
            {
                // Thử server DoH tiếp theo
            }
        }

        throw new Exception($"Không thể phân giải tên miền '{host}' qua cả DNS hệ thống và DNS over HTTPS.");
    }
}
