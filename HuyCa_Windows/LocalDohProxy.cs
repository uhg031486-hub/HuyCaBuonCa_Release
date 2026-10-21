using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace HuyCa_Windows;

/// <summary>
/// Máy chủ Proxy đường hầm TCP cục bộ (Local DoH Tunneling Proxy):
/// Nhận các kết nối HTTP/HTTPS từ WebView2 và phân giải toàn bộ tên miền
/// thông qua Cloudflare / Google DNS over HTTPS (DoH), hoàn toàn bỏ qua
/// DNS nội bộ của công ty (10.21.16.1) và các cơ chế DNS Sinkhole / Chặn domain.
/// </summary>
public class LocalDohProxy
{
    private TcpListener? _listener;
    private CancellationTokenSource? _cts;
    public int Port { get; private set; }

    public void Start()
    {
        _cts = new CancellationTokenSource();
        _listener = new TcpListener(IPAddress.Loopback, 0); // Chọn cổng ngẫu nhiên khả dụng
        _listener.Start();
        Port = ((IPEndPoint)_listener.LocalEndpoint).Port;
        _ = AcceptClientsAsync(_listener, _cts.Token);
    }

    public void Stop()
    {
        try
        {
            _cts?.Cancel();
            _listener?.Stop();
        }
        catch { }
    }

    private async Task AcceptClientsAsync(TcpListener listener, CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            try
            {
                var client = await listener.AcceptTcpClientAsync(ct);
                _ = HandleClientAsync(client, ct);
            }
            catch when (ct.IsCancellationRequested)
            {
                break;
            }
            catch
            {
                try { await Task.Delay(50, ct); } catch { break; }
            }
        }
    }

    private async Task HandleClientAsync(TcpClient client, CancellationToken ct)
    {
        using (client)
        using (var clientStream = client.GetStream())
        {
            try
            {
                var buffer = new byte[8192];
                int bytesRead = await clientStream.ReadAsync(buffer, 0, buffer.Length, ct);
                if (bytesRead <= 0) return;

                string headerText = Encoding.ASCII.GetString(buffer, 0, bytesRead);
                string firstLine = headerText.Split("\r\n")[0];
                string[] parts = firstLine.Split(' ');
                if (parts.Length < 2) return;

                string method = parts[0];
                string target = parts[1];

                string host;
                int port = 443;

                if (method.Equals("CONNECT", StringComparison.OrdinalIgnoreCase))
                {
                    // HTTPS Tunneling (CONNECT host:port HTTP/1.1)
                    string[] hostParts = target.Split(':');
                    host = hostParts[0];
                    if (hostParts.Length > 1 && int.TryParse(hostParts[1], out int p))
                    {
                        port = p;
                    }

                    // Phân giải IP bằng DNS over HTTPS (Cloudflare / Google)
                    IPAddress[] ips = await ResolveHostAsync(host, ct);

                    using var targetSocket = new Socket(SocketType.Stream, ProtocolType.Tcp) { NoDelay = true };
                    await targetSocket.ConnectAsync(ips, port, ct);
                    using var targetStream = new NetworkStream(targetSocket, ownsSocket: false);

                    // Phản hồi cho Chromium xác nhận đường hầm TCP đã thiết lập thành công
                    byte[] okResponse = Encoding.ASCII.GetBytes("HTTP/1.1 200 Connection Established\r\n\r\n");
                    await clientStream.WriteAsync(okResponse, 0, okResponse.Length, ct);

                    // Chuyển tiếp dữ liệu 2 chiều giữa WebView2 và Server
                    var t1 = clientStream.CopyToAsync(targetStream, ct);
                    var t2 = targetStream.CopyToAsync(clientStream, ct);
                    await Task.WhenAny(t1, t2);

                    try { targetSocket.Shutdown(SocketShutdown.Both); } catch { }
                    try { client.Client.Shutdown(SocketShutdown.Both); } catch { }
                }
                else
                {
                    // Plain HTTP Forwarding (GET http://host:port/... HTTP/1.1)
                    port = 80;
                    if (target.StartsWith("http://", StringComparison.OrdinalIgnoreCase) || target.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
                    {
                        var uri = new Uri(target);
                        host = uri.Host;
                        port = uri.Port > 0 ? uri.Port : 80;
                    }
                    else
                    {
                        // Tìm host từ header "Host: ..."
                        host = target.Split('/')[0];
                        foreach (var line in headerText.Split("\r\n"))
                        {
                            if (line.StartsWith("Host:", StringComparison.OrdinalIgnoreCase))
                            {
                                string hVal = line.Substring(5).Trim();
                                string[] hParts = hVal.Split(':');
                                host = hParts[0];
                                if (hParts.Length > 1 && int.TryParse(hParts[1], out int p)) port = p;
                                break;
                            }
                        }
                    }

                    IPAddress[] ips = await ResolveHostAsync(host, ct);

                    using var targetSocket = new Socket(SocketType.Stream, ProtocolType.Tcp) { NoDelay = true };
                    await targetSocket.ConnectAsync(ips, port, ct);
                    using var targetStream = new NetworkStream(targetSocket, ownsSocket: false);

                    // Gửi request đầu tiên sang server
                    await targetStream.WriteAsync(buffer, 0, bytesRead, ct);

                    // Chuyển tiếp dữ liệu 2 chiều
                    var t1 = clientStream.CopyToAsync(targetStream, ct);
                    var t2 = targetStream.CopyToAsync(clientStream, ct);
                    await Task.WhenAny(t1, t2);

                    try { targetSocket.Shutdown(SocketShutdown.Both); } catch { }
                    try { client.Client.Shutdown(SocketShutdown.Both); } catch { }
                }
            }
            catch
            {
                // Bỏ qua lỗi ngắt kết nối thông thường
            }
        }
    }

    private static async Task<IPAddress[]> ResolveHostAsync(string host, CancellationToken ct)
    {
        if (IPAddress.TryParse(host, out var directIp))
        {
            return new[] { directIp };
        }

        // 1. Thử phân giải DoH trước để vượt tường lửa công ty
        try
        {
            return await UpdateManager.ResolveViaDoHAsync(host, ct);
        }
        catch
        {
            // 2. Dự phòng phân giải hệ thống nếu DoH không phản hồi
            return await Dns.GetHostAddressesAsync(host, ct);
        }
    }
}
