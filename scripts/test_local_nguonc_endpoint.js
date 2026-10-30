const http = require('http');
const url = require('url');

async function decryptNguonC(embedUrl) {
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
      'Origin': new URL(embedUrl).origin,
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
  return parsed.preissued?.playlist;
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (parsed.pathname === '/api/nguonc_stream') {
    try {
      const targetEmbed = parsed.query.url;
      const playlistUrl = await decryptNguonC(targetEmbed);
      
      const plResp = await fetch(playlistUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          'Referer': 'https://streamc.xyz/'
        }
      });
      const plText = await plResp.text();

      const host = req.headers.host;
      const proxyPrefix = `http://${host}/api/proxy?url=`;

      const rewritten = plText.split('\n').map(line => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) return line;
        return `${proxyPrefix}${encodeURIComponent(trimmed)}`;
      }).join('\n');

      res.writeHead(200, { 'Content-Type': 'application/vnd.apple.mpegurl; charset=utf-8' });
      res.end(rewritten);
    } catch(err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  if (parsed.pathname === '/api/proxy') {
    try {
      const targetUrl = parsed.query.url;
      const isSegment = targetUrl.includes('.png') || targetUrl.includes('.ts') || targetUrl.includes('streamaaa');
      
      const forwardHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://streamc.xyz/',
        'Origin': 'https://streamc.xyz'
      };

      const upstream = await fetch(targetUrl, { headers: forwardHeaders });
      const buf = await upstream.arrayBuffer();

      res.writeHead(upstream.status, {
        'Content-Type': isSegment ? 'video/mp2t' : (upstream.headers.get('content-type') || 'application/octet-stream'),
        'Content-Length': buf.byteLength,
        'Access-Control-Allow-Origin': '*'
      });
      res.end(Buffer.from(buf));
    } catch(err) {
      res.writeHead(502);
      res.end();
    }
    return;
  }

  if (parsed.pathname === '/player_test.html') {
    const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Test Clean NguonC Stream</title>
      <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    </head>
    <body style="margin:0; background:#000; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh;">
      <video id="video" controls autoplay style="width:80%; max-width:960px; height:auto; background:#111;"></video>
      <div id="status" style="color:#0f0; margin-top:10px; font-family:sans-serif;">Initializing...</div>
      <script>
        const video = document.getElementById('video');
        const status = document.getElementById('status');
        const streamUrl = '/api/nguonc_stream?url=' + encodeURIComponent('https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f');
        
        if (Hls.isSupported()) {
          const hls = new Hls({
            enableWorker: true,
            lowLatencyMode: false
          });
          hls.loadSource(streamUrl);
          hls.attachMedia(video);
          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            status.innerText = 'MANIFEST_PARSED! Starting playback...';
            video.play().catch(e => { status.innerText = 'Play error: ' + e; });
          });
          hls.on(Hls.Events.FRAG_LOADED, (e, data) => {
            status.innerText = 'FRAG_LOADED: ' + data.frag.sn + ' (duration ' + data.frag.duration + 's)';
          });
          hls.on(Hls.Events.ERROR, (e, data) => {
            status.innerText = 'HLS ERROR: ' + data.details + ' fatal=' + data.fatal;
          });
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
          video.src = streamUrl;
          video.play();
        }
      </script>
    </body>
    </html>
    `;
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(8099, () => {
  console.log('Test clean server running on port 8099');
});
