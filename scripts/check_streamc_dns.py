import sys
sys.stdout.reconfigure(encoding='utf-8')
import socket
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

domains_to_test = [
    'embed14.streamc.xyz',
    'embed11.streamc.xyz',
    'streamc.xyz',
    'embed.streamc.xyz',
    'streamc.net',
    'embed.streamc.net',
    'player.streamc.xyz',
    'embed.nguonc.com',
    'player.nguonc.com',
    'streamc.me',
    'streamc.org',
    'streamc.top',
    'streamc.cc',
    'streamc.site'
]

print("Kiểm tra DNS phân giải IP của các domain streamc:")
for d in domains_to_test:
    try:
        ip = socket.gethostbyname(d)
        print(f"✅ {d} -> IP: {ip}")
    except Exception as e:
        print(f"❌ {d} -> Không phân giải được IP ({e})")
