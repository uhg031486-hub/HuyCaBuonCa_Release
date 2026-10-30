const crypto = require('crypto');

async function testDecrypt() {
  const embedUrl = 'https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f';
  const postBody = {
    action: 'bootstrap',
    referrer: 'https://phim.nguonc.com/',
    frame_origins: ['https://phim.nguonc.com'],
    request_grant: true,
    playlist_format: 'hls',
    pretty_url: true,
    path_chunks: true,
    bootstrap_format: 'aesgcm-v1'
  };

  const resp = await fetch(embedUrl, {
    method: 'POST',
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      'Referer': 'https://phim.nguonc.com/',
      'Origin': 'https://embed17.streamc.xyz',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(postBody)
  });

  const resJson = await resp.json();
  console.log('Got IV:', resJson.iv);

  const iv = Buffer.from(resJson.iv, 'hex');
  const ciphertextWithTag = Buffer.from(resJson.data, 'base64');
  
  // AES-GCM standard tag is last 16 bytes
  const authTag = ciphertextWithTag.slice(ciphertextWithTag.length - 16);
  const ciphertext = ciphertextWithTag.slice(0, ciphertextWithTag.length - 16);

  const s = 'stream-bootstrap-v1\n' + embedUrl;
  const key = crypto.createHash('sha256').update(s, 'utf8').digest();

  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAAD(Buffer.from(s, 'utf8'));
  decipher.setAuthTag(authTag);

  let decrypted = decipher.update(ciphertext, null, 'utf8');
  decrypted += decipher.final('utf8');

  const parsed = JSON.parse(decrypted);
  console.log('Decrypted successfully!');
  console.log('Playlist URL:', parsed.preissued?.playlist);
}

testDecrypt().catch(console.error);
