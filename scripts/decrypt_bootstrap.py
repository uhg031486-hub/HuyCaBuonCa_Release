import urllib.request
import json
import sys
import hashlib
import binascii
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.stdout.reconfigure(encoding='utf-8')

url = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec"
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Referer': 'https://phim.nguonc.com/',
    'Origin': 'https://embed14.streamc.xyz',
    'Content-Type': 'application/json'
}

post_body = {
    "action": "bootstrap",
    "referrer": "https://phim.nguonc.com/",
    "frame_origins": ["https://phim.nguonc.com"],
    "request_grant": True,
    "playlist_format": "hls",
    "pretty_url": True,
    "path_chunks": True,
    "bootstrap_format": "aesgcm-v1"
}

req_post = urllib.request.Request(url, data=json.dumps(post_body).encode('utf-8'), headers=headers, method='POST')
with urllib.request.urlopen(req_post) as resp_post:
    resp_data = json.loads(resp_post.read().decode())

iv = binascii.unhexlify(resp_data['iv'])
ciphertext = base64.b64decode(resp_data['data'])
s = ("stream-bootstrap-v1\n" + url).encode('utf-8')
key = hashlib.sha256(s).digest()

aesgcm = AESGCM(key)
plaintext = aesgcm.decrypt(iv, ciphertext, s)
decrypted_json = json.loads(plaintext.decode('utf-8'))
print("DECRYPTED BOOTSTRAP JSON:")
print(json.dumps(decrypted_json, indent=2, ensure_ascii=False)[:1000])
