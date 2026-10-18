using System;
using System.IO;
using System.Windows;
using System.Windows.Input;
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

            var env = await CoreWebView2Environment.CreateAsync(null, userDataFolder);
            await webView.EnsureCoreWebView2Async(env);

            // Cấu hình WebView2 Engine
            webView.CoreWebView2.Settings.IsStatusBarEnabled = false;
            webView.CoreWebView2.Settings.AreDevToolsEnabled = true;
            webView.CoreWebView2.Settings.IsZoomControlEnabled = true;
            webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = true;
            webView.CoreWebView2.Profile.PreferredColorScheme = CoreWebView2PreferredColorScheme.Dark;

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
            };

            // Tìm thư mục chứa web assets
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string wwwPath = Path.Combine(baseDir, "www");

            // Nếu chạy trong Visual Studio hoặc chế độ dev, fallback tìm www ở parent folder
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
                // Ánh xạ virtual host https://huyca.local/ để tránh lỗi CORS khi tải HLS m3u8
                webView.CoreWebView2.SetVirtualHostNameToFolderMapping(
                    "huyca.local",
                    wwwPath,
                    CoreWebView2HostResourceAccessKind.Allow
                );

                webView.CoreWebView2.Navigate("https://huyca.local/index.html");
            }
            else
            {
                MessageBox.Show(
                    "Không tìm thấy thư mục tài nguyên 'www/index.html'.\nVui lòng kiểm tra lại quá trình cài đặt ứng dụng!",
                    "Huy Cá",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
        }
        catch (Exception ex)
        {
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