using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media.Imaging;
using Microsoft.Web.WebView2.Core;

namespace HuyCa_Windows;

public partial class MainWindow : Window
{
    private bool _isFullscreen = false;
    private WindowStyle _previousStyle = WindowStyle.SingleBorderWindow;
    private WindowState _previousState = WindowState.Normal;
    private ResizeMode _previousResize = ResizeMode.CanResize;

    public MainWindow()
    {
        InitializeComponent();

        // Nạp icon an toàn, không ném exception nếu thiếu file
        try
        {
            string iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "app.ico");
            if (File.Exists(iconPath))
            {
                Icon = new BitmapImage(new Uri(iconPath, UriKind.Absolute));
            }
        }
        catch { }
    }

    private async void Window_Loaded(object sender, RoutedEventArgs e)
    {
        try
        {
            // Thiết lập thư mục lưu trữ profile và cache cho ứng dụng
            string userDataFolder = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "HuyCa_Windows"
            );
            Directory.CreateDirectory(userDataFolder);

            // Bật cờ trình duyệt tối ưu: Tắt CORS cho HLS, cho phép phát luồng mixed HTTP/HTTPS, tự động autoplay video
            // Tích hợp DNS mã hóa DoH (Cloudflare 1.1.1.1 & Google 8.8.8.8) tự động vượt qua tường lửa/DNS chặn của mạng công ty
            var options = new CoreWebView2EnvironmentOptions
            {
                AdditionalBrowserArguments = "--disable-web-security --allow-running-insecure-content --autoplay-policy=no-user-gesture-required --ignore-certificate-errors --enable-features=DnsOverHttps --dns-over-https-templates=\"https://1.1.1.1/dns-query https://dns.google/dns-query\" --host-resolver-rules=\"MAP cloudflare-dns.com 1.1.1.1, MAP dns.google 8.8.8.8\""
            };

            var env = await CoreWebView2Environment.CreateAsync(null, userDataFolder, options);
            await webView.EnsureCoreWebView2Async(env);

            // Cấu hình WebView2 Engine
            webView.CoreWebView2.Settings.IsStatusBarEnabled = false;
            webView.CoreWebView2.Settings.AreDevToolsEnabled = true;
            webView.CoreWebView2.Settings.IsZoomControlEnabled = true;
            webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = true;
            webView.CoreWebView2.Profile.PreferredColorScheme = CoreWebView2PreferredColorScheme.Dark;

            // Lắng nghe thông điệp từ giao diện web
            webView.CoreWebView2.WebMessageReceived += (s, args) =>
            {
                try
                {
                    string msg = args.TryGetWebMessageAsString();
                    if (msg == "check_update")
                    {
                        Dispatcher.Invoke(() =>
                        {
                            _ = UpdateManager.CheckForUpdateAsync(this, silent: false);
                        });
                    }
                }
                catch { }
            };

            // Xử lý tự động Fullscreen khi video mở toàn màn hình
            webView.CoreWebView2.ContainsFullScreenElementChanged += (s, args) =>
            {
                Dispatcher.Invoke(() =>
                {
                    if (webView.CoreWebView2.ContainsFullScreenElement)
                    {
                        if (!_isFullscreen) ToggleFullscreen();
                    }
                    else
                    {
                        if (_isFullscreen) ToggleFullscreen();
                    }
                });
            };

            webView.NavigationCompleted += (s, args) =>
            {
                Dispatcher.Invoke(() =>
                {
                    loadingOverlay.Visibility = Visibility.Collapsed;
                });

                // Tự động kiểm tra cập nhật trong nền sau 3 giây
                _ = Task.Run(async () =>
                {
                    await Task.Delay(3000);
                    await Dispatcher.InvokeAsync(() =>
                    {
                        _ = UpdateManager.CheckForUpdateAsync(this, silent: true);
                    });
                });
            };

            // Timeout dự phòng: tự ẩn loading sau 6 giây để không bao giờ bị kẹt
            _ = Task.Run(async () =>
            {
                await Task.Delay(6000);
                await Dispatcher.InvokeAsync(() =>
                {
                    loadingOverlay.Visibility = Visibility.Collapsed;
                });
            });

            // Tìm thư mục chứa web assets
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string wwwPath = Path.Combine(baseDir, "www");

            if (!Directory.Exists(wwwPath))
            {
                string devPath = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "www"));
                if (Directory.Exists(devPath))
                {
                    wwwPath = devPath;
                }
            }

            if (Directory.Exists(wwwPath) && File.Exists(Path.Combine(wwwPath, "index.html")))
            {
                // Ánh xạ virtual host https://huyca.local/ để phục vụ web app
                webView.CoreWebView2.SetVirtualHostNameToFolderMapping(
                    "huyca.local",
                    wwwPath,
                    CoreWebView2HostResourceAccessKind.Allow
                );

                webView.CoreWebView2.Navigate("https://huyca.local/index.html");
            }
            else
            {
                loadingOverlay.Visibility = Visibility.Collapsed;
                MessageBox.Show(
                    "Không tìm thấy thư mục tài nguyên 'www/index.html'.\nVui lòng kiểm tra lại thư mục cài đặt ứng dụng!",
                    "Huy Cá",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
        }
        catch (Exception ex)
        {
            loadingOverlay.Visibility = Visibility.Collapsed;
            MessageBox.Show(
                $"Lỗi khởi chạy WebView2: {ex.Message}\n\nLưu ý: Ứng dụng yêu cầu Microsoft Edge WebView2 Runtime (đã tích hợp sẵn trên Windows 10 & 11).",
                "Huy Cá",
                MessageBoxButton.OK,
                MessageBoxImage.Error
            );
        }
    }

    private void Window_KeyDown(object sender, KeyEventArgs e)
    {
        // F11: Bật / tắt chế độ toàn màn hình
        if (e.Key == Key.F11)
        {
            ToggleFullscreen();
            e.Handled = true;
            return;
        }

        // Escape: Thoát toàn màn hình nếu đang bật
        if (e.Key == Key.Escape && _isFullscreen)
        {
            ToggleFullscreen();
            e.Handled = true;
            return;
        }

        // F5 hoặc Ctrl+R: Làm mới ứng dụng
        if (e.Key == Key.F5 || (e.Key == Key.R && (Keyboard.Modifiers & ModifierKeys.Control) == ModifierKeys.Control))
        {
            if (webView.CoreWebView2 != null)
            {
                webView.Reload();
                e.Handled = true;
            }
        }

        // Ctrl+U: Kiểm tra cập nhật ứng dụng
        if (e.Key == Key.U && (Keyboard.Modifiers & ModifierKeys.Control) == ModifierKeys.Control)
        {
            _ = UpdateManager.CheckForUpdateAsync(this, silent: false);
            e.Handled = true;
        }
    }

    private void Window_PreviewMouseDown(object sender, MouseButtonEventArgs e)
    {
        // Xử lý nút Back của chuột (XButton1)
        if (e.ChangedButton == MouseButton.XButton1)
        {
            e.Handled = true;
            _ = Dispatcher.InvokeAsync(async () =>
            {
                try
                {
                    if (webView?.CoreWebView2 != null)
                    {
                        await webView.CoreWebView2.ExecuteScriptAsync("if (typeof window.handleBackAction === 'function') { window.handleBackAction(); }");
                    }
                }
                catch { }
            });
        }
    }

    private void ToggleFullscreen()
    {
        if (!_isFullscreen)
        {
            _previousStyle = WindowStyle;
            _previousState = WindowState;
            _previousResize = ResizeMode;

            WindowStyle = WindowStyle.None;
            ResizeMode = ResizeMode.NoResize;
            WindowState = WindowState.Maximized;
            _isFullscreen = true;
        }
        else
        {
            WindowStyle = _previousStyle;
            ResizeMode = _previousResize;
            WindowState = _previousState;
            _isFullscreen = false;
        }
    }
}