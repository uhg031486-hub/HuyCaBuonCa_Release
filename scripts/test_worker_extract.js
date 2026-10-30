// Test extraction of NguonC embed URL using pure Web Crypto (Cloudflare Workers compatible)
async function extractNguonCStream(embedUrl) {
  const userAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1';
  
  // 1. Fetch HTML
  const htmlResp = await fetch(embedUrl, {
    headers: {
      'User-Agent': userAgent,
      'Referer': 'https://phim.nguonc.com/'
    }
  });
  if (!htmlResp.ok) throw new Error(`HTML fetch failed: ${htmlResp.status}`);
  const html = await htmlResp.text();

  // 2. Extract bootstrap data from <script id="stream-bootstrap">
  const m = html.match(/<script id="stream-bootstrap" type="application\/json">(.*?)<\/script>/s);
  if (!m) throw new Error('stream-bootstrap tag not found');
  const bootstrapConfig = JSON.parse(m[1]);
  const apiUrl = bootstrapConfig.api || embedUrl;

  // 3. Request bootstrap grant
  const postHeaders = {
    'User-Agent': userAgent,
    'Referer': 'https://phim.nguonc.com/',
    'Origin': new URL(embedUrl).origin,
    'Content-Type': 'application/json'
  };

  const bootstrapBody = {
    action: "bootstrap",
    referrer: "https://phim.nguonc.com/",
    frame_origins: ["https://phim.nguonc.com"],
    request_grant: true,
    playlist_format: "hls",
    pretty_url: true,
    path_chunks: true,
    bootstrap_format: "aesgcm-v1"
  };

  const bResp = await fetch(apiUrl, {
    method: 'POST',
    headers: postHeaders,
    body: JSON.stringify(bootstrapBody)
  });
  if (!bResp.ok) throw new Error(`Bootstrap POST failed: ${bResp.status}`);
  const bData = await bResp.json();

  if (bData.format !== 'aesgcm-v1' || !bData.iv || !bData.data) {
    throw new Error(`Unexpected bootstrap response format: ${bData.format}`);
  }

  // 4. Decrypt bootstrap data using Web Crypto
  const iv = new Uint8Array(bData.iv.match(/../g).map(h => parseInt(h, 16)));
  const ciphertextStr = atob(bData.data);
  const ciphertext = new Uint8Array(ciphertextStr.length);
  for (let i = 0; i < ciphertextStr.length; i++) {
    ciphertext[i] = ciphertextStr.charCodeAt(i);
  }

  const s = new TextEncoder().encode("stream-bootstrap-v1\n" + apiUrl);
  const keyDigest = await crypto.subtle.digest("SHA-256", s);
  const cryptoKey = await crypto.subtle.importKey("raw", keyDigest, { name: "AES-GCM" }, false, ["decrypt"]);
  const decryptedBuf = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: iv, additionalData: s, tagLength: 128 },
    cryptoKey,
    ciphertext
  );

  const decryptedJson = JSON.parse(new TextDecoder("utf-8").decode(decryptedBuf));
  const bootstrapToken = decryptedJson.bootstrap;
  if (!bootstrapToken) throw new Error('Missing bootstrap token');

  // 5. Issue token for HLS playlist
  const issueBody = {
    action: "issue",
    bootstrap: bootstrapToken,
    turnstile_response: null,
    playlist_format: "hls",
    pretty_url: true,
    path_chunks: true,
    frame_origins: ["https://phim.nguonc.com"]
  };

  const issueResp = await fetch(apiUrl, {
    method: 'POST',
    headers: postHeaders,
    body: JSON.stringify(issueBody)
  });
  if (!issueResp.ok) throw new Error(`Issue POST failed: ${issueResp.status}`);
  const issueData = await issueResp.json();
  const playlistUrl = issueData.playlist;
  if (!playlistUrl) throw new Error('Missing playlist URL in issue response');

  // 6. Fetch the m3u8 playlist
  const plResp = await fetch(playlistUrl, {
    headers: {
      'User-Agent': userAgent,
      'Referer': embedUrl
    }
  });
  if (!plResp.ok) throw new Error(`Playlist fetch failed: ${plResp.status}`);
  const m3u8Text = await plResp.text();

  return {
    playlistUrl,
    m3u8Text,
    origin: new URL(embedUrl).origin
  };
}

// Test with Episode 40 and Episode 1
async function test() {
  for (const [title, url] of [
    ['Tập 40', 'https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec'],
    ['Tập 1', 'https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f']
  ]) {
    try {
      console.log(`\n=== Testing ${title}: ${url} ===`);
      const start = Date.now();
      const res = await extractNguonCStream(url);
      console.log(`Success in ${Date.now() - start}ms!`);
      console.log(`Playlist URL: ${res.playlistUrl.slice(0, 60)}...`);
      console.log(`M3U8 snippet:\n${res.m3u8Text.split('\n').slice(0, 8).join('\n')}`);
    } catch(err) {
      console.error(`Failed ${title}:`, err);
    }
  }
}

test();
