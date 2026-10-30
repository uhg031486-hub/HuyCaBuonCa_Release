async function testFullStreamPipeline() {
  const embedUrl = 'https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f';
  
  // 1. Decrypt bootstrap
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
  const iv = new Uint8Array(resJson.iv.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
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
    { name: 'AES-GCM', iv: iv, additionalData: aad },
    cryptoKey,
    ciphertextWithTag
  );

  const decoder = new TextDecoder();
  const decryptedText = decoder.decode(decryptedBuffer);
  const parsed = JSON.parse(decryptedText);
  const playlistUrl = parsed.preissued?.playlist;
  console.log('1. Playlist URL:', playlistUrl);

  // 2. Fetch playlist
  const plResp = await fetch(playlistUrl, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      'Referer': 'https://streamc.xyz/'
    }
  });
  const plText = await plResp.text();
  console.log('2. Playlist status:', plResp.status, 'Lines:', plText.split('\n').length);

  // 3. Test first segment fetch with Referer: https://streamc.xyz/
  const lines = plText.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));
  const firstSegUrl = lines[0];
  console.log('3. Fetching first segment:', firstSegUrl);
  const segResp = await fetch(firstSegUrl, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      'Referer': 'https://streamc.xyz/'
    }
  });
  console.log('4. First segment status:', segResp.status, 'Content-Length:', segResp.headers.get('content-length'));
  const buf = await segResp.arrayBuffer();
  const bytes = new Uint8Array(buf);
  console.log('5. Segment first byte (hex):', bytes[0].toString(16), '(should be 47 for MPEG-TS)');
  if (bytes[0] === 0x47) {
    console.log('SUCCESS! Valid MPEG-TS segment verified!');
  } else {
    console.log('FAILURE: First byte is not 0x47!');
  }
}

testFullStreamPipeline().catch(console.error);
