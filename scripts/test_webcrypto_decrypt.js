async function testWebCrypto() {
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
  
  // Hex to Uint8Array for IV
  const iv = new Uint8Array(resJson.iv.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
  
  // Base64 to Uint8Array for ciphertext (which includes 16-byte tag at the end)
  const binaryString = atob(resJson.data);
  const ciphertextWithTag = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    ciphertextWithTag[i] = binaryString.charCodeAt(i);
  }

  const s = 'stream-bootstrap-v1\n' + embedUrl;
  const encoder = new TextEncoder();
  const aad = encoder.encode(s);
  
  const keyHash = await crypto.subtle.digest('SHA-256', aad);
  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    keyHash,
    { name: 'AES-GCM' },
    false,
    ['decrypt']
  );

  const decryptedBuffer = await crypto.subtle.decrypt(
    {
      name: 'AES-GCM',
      iv: iv,
      additionalData: aad
    },
    cryptoKey,
    ciphertextWithTag
  );

  const decoder = new TextDecoder();
  const decryptedText = decoder.decode(decryptedBuffer);
  const parsed = JSON.parse(decryptedText);

  console.log('Web Crypto decrypted successfully!');
  console.log('Playlist URL:', parsed.preissued?.playlist);
}

testWebCrypto().catch(console.error);
