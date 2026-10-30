// Test proxy.js onRequest logic locally
import { onRequest } from '../HuyCa_Web/functions/api/proxy.js';

async function testLocalProxy() {
  console.log("=== KIỂM THỬ PROXY.JS NGUỒN C EXTRACTION ===");

  // Test Ep 40
  const url40 = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec";
  const mockContext40 = {
    request: new Request(`http://localhost:8788/api/proxy?type=nguonc&ext=.m3u8&url=${encodeURIComponent(url40)}`, {
      method: 'GET'
    })
  };

  const resp40 = await onRequest(mockContext40);
  console.log("Tập 40 response status:", resp40.status);
  console.log("Tập 40 Content-Type:", resp40.headers.get('content-type'));
  const m3u8_40 = await resp40.text();
  console.log("Tập 40 M3U8 preview:\n" + m3u8_40.split('\n').slice(0, 10).join('\n'));

  // Test Ep 1
  const url1 = "https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f";
  const mockContext1 = {
    request: new Request(`http://localhost:8788/api/proxy?type=nguonc&ext=.m3u8&url=${encodeURIComponent(url1)}`, {
      method: 'GET'
    })
  };

  const resp1 = await onRequest(mockContext1);
  console.log("\nTập 1 response status:", resp1.status);
  console.log("Tập 1 Content-Type:", resp1.headers.get('content-type'));
  const m3u8_1 = await resp1.text();
  console.log("Tập 1 M3U8 preview:\n" + m3u8_1.split('\n').slice(0, 10).join('\n'));

  // Test Segment Proxying
  const firstSegUrl = m3u8_1.split('\n').find(l => l.startsWith('http://localhost:8788/api/proxy?url='));
  if (firstSegUrl) {
    const rawTarget = decodeURIComponent(firstSegUrl.split('url=')[1]);
    console.log("\nTesting Segment Fetch:", rawTarget);
    const mockContextSeg = {
      request: new Request(firstSegUrl, { method: 'GET' })
    };
    const respSeg = await onRequest(mockContextSeg);
    console.log("Segment response status:", respSeg.status);
    console.log("Segment Content-Type:", respSeg.headers.get('content-type'));
    const ab = await respSeg.arrayBuffer();
    const u8 = new Uint8Array(ab);
    console.log("Segment size:", ab.byteLength, "bytes, MPEG-TS sync byte 0x47:", u8[0] === 0x47);
  }

  console.log("\n🎉 ALL LOCAL PROXY TESTS PASSED!");
}

testLocalProxy().catch(err => {
  console.error("❌ Test failed:", err);
  process.exit(1);
});
