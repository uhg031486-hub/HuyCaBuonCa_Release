import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

embed_url = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec"
print(f"Fetching embed: {embed_url}...")

req = urllib.request.Request(embed_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://phim.nguonc.com/'
})

try:
    with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
        html = r.read().decode('utf-8', errors='ignore')
        print(f"Status: {r.status}, Length: {len(html)}")
        print("\n--- PREVIEW HTML ---")
        print(html[:1500])
        print("\n--- TÌM M3U8 HOẶC VIDEO SOURCE ---")
        import re
        m3u8s = re.findall(r'(https?://[^\s\"\'\<\>]+\.m3u8[^\s\"\'\<\>]*)', html)
        print("Found m3u8s:", m3u8s)
        sources = re.findall(r'file\s*:\s*[\"\']([^\"\']+)[\"\']', html)
        print("Found file:", sources)
except Exception as e:
    print("Error:", e)
