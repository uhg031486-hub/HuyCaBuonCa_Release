/*! Stream Panel lite-45-jw8513-messages-r25 */
!function(){"use strict";if(window.streamRateWait)return;let e=null;function clock(){try{const e="undefined"!=typeof performance?performance.now?.():NaN;return Number.isFinite(e)?e:null}catch(e){return null}}function clear(){if(!e)return;const t=e;e=null,clearTimeout(t.timer),document.removeEventListener?.("visibilitychange",t.visibility),window.removeEventListener?.("pagehide",t.hide),window.removeEventListener?.("pageshow",t.show),t.retry.removeEventListener?.("click",t.prevent,!0),t.retry.textContent=t.text,t.retry.disabled=t.disabled,null===t.aria?t.retry.removeAttribute?.("aria-disabled"):t.retry.setAttribute?.("aria-disabled",t.aria),null===t.live?t.retry.removeAttribute?.("aria-live"):t.retry.setAttribute?.("aria-live",t.live)}window.streamRateWait={start:function start({label:t,retry:r,seconds:n,message:s,readyMessage:a}={}){if(clear(),!t||!r)return!1;const i=Number(n),o=1e3*Math.max(0,Math.min(86400,Number.isFinite(i)?Math.ceil(i):10)),l={label:t,retry:r,text:r.textContent||"Tải lại",disabled:r.disabled,aria:r.getAttribute?.("aria-disabled")??null,live:r.getAttribute?.("aria-live")??null,timer:null,wall:Date.now(),monotonic:clock(),elapsed:0,hidden:!1};e=l,t.textContent=s||"Mạng của bạn đang mở quá nhiều yêu cầu video. Vui lòng chờ rồi tải lại.";const tick=()=>{if(e!==l)return;clearTimeout(l.timer),l.timer=null;const n=clock();l.elapsed=Math.max(l.elapsed,Date.now()-l.wall,null!==n&&null!==l.monotonic?n-l.monotonic:0);const s=Math.max(0,Math.ceil((o-l.elapsed)/1e3));if(!s)return clear(),r.disabled=!1,r.removeAttribute?.("aria-disabled"),void(t.textContent=a||"Đã hết thời gian chờ. Bạn có thể thử tải lại video.");r.disabled=!0,r.setAttribute?.("aria-disabled","true"),r.setAttribute?.("aria-live","off"),r.textContent=l.text+" ("+function format(e){const pad=e=>String(e).padStart(2,"0"),t=Math.floor(e/3600),r=Math.floor(e/60)%60;return(t?pad(t)+":":"")+pad(r)+":"+pad(e%60)}(s)+")",document.hidden||l.hidden||(l.timer=setTimeout(tick,1e3))};return l.prevent=e=>{e.preventDefault(),e.stopImmediatePropagation?.()},l.visibility=()=>tick(),l.hide=()=>{l.hidden=!0,clearTimeout(l.timer),l.timer=null},l.show=()=>{l.hidden=!1,tick()},r.addEventListener?.("click",l.prevent,!0),document.addEventListener?.("visibilitychange",l.visibility),window.addEventListener?.("pagehide",l.hide),window.addEventListener?.("pageshow",l.show),tick(),!0},clear}}(),function(){"use strict";const e=JSON.parse(document.getElementById("stream-bootstrap").textContent);function frameOrigins(){const e=[document.referrer||""];try{const t=location.ancestorOrigins;for(let r=(t?.length||0)-1;r>=0&&e.length<9;r--)e.push(t[r])}catch(r){}const t=[];for(const n of e)try{const e=new URL(n);["http:","https:"].includes(e.protocol)&&e.origin.length<=320&&!t.includes(e.origin)&&t.push(e.origin)}catch(r){}return t.slice(0,8)}window.videoHash=e.video;const t=!0,r=!1,n=(()=>{const e=navigator.userAgent||"",t=/iphone|ipod|ipad/i.test(e)||"MacIntel"===navigator.platform&&navigator.maxTouchPoints>1||/macintosh/i.test(e)&&!/windows|android/i.test(e),n=/ipad/i.test(e)||"MacIntel"===navigator.platform&&navigator.maxTouchPoints>1,s=/safari/i.test(e)&&!/(?:Chrome|CriOS|chromium|android|phantom)/i.test(e)&&!/SMART-TV/.test(e),a={trial:r,appleDevice:t,mediaSource:!!window.MediaSource,managedMediaSource:!!window.ManagedMediaSource,jwSafari:s,webCrypto:!!window.crypto?.subtle,textCodecs:"function"==typeof TextEncoder&&"function"==typeof TextDecoder,codecSupported:!1};let i,o=!1;if(t)if(n&&/crios/i.test(e))i="ipad_crios_native";else if(a.webCrypto)if(a.textCodecs){const e=window.ManagedMediaSource||window.MediaSource;if("function"!=typeof e?.isTypeSupported)i="media_source_missing";else{try{a.codecSupported=!0===e.isTypeSupported('video/mp4; codecs="avc1.42E01E,mp4a.40.2"')}catch(l){i="codec_probe_failed"}i||a.codecSupported||(i="codec_unsupported"),!i&&window.MediaSource,i||(o=!0,i=window.MediaSource||s?a.managedMediaSource?"apple_mms":"apple_mse":"apple_mms_bridge")}}else i="text_codec_missing";else i="crypto_missing";else i="not_apple";return Object.freeze({...a,reason:i,appleJsHls:o,format:t&&!o?"hls":"aesgcm-v2"})})(),s=n.appleDevice,a=n.appleJsHls,i=s&&!a,o=n.format;try{window.streamSandbox?.pipeline?.({stage:"playback_branch",dependency:"player",...n})}catch(E){}let l=null,c=null,d=!1,u=e.preissued;const m=Number.isFinite(window.streamBootstrapReceivedAt)?window.streamBootstrapReceivedAt:performance.now(),p=15e3;let h=Number.isInteger(e.bootstrapRemainingSeconds)?m+1e3*e.bootstrapRemainingSeconds-p:1/0,g=Number.isInteger(e.bootstrapRefreshRemainingSeconds)?m+1e3*e.bootstrapRefreshRemainingSeconds-p:1/0,f=null;const y=document.getElementById("verification"),w=document.getElementById("verification-message"),v=document.getElementById("verification-retry");let b=null,k=0;function clearRateWait(){clearTimeout(b),b=null,k++,window.streamRateWait?.clear(),v.disabled=!1}function rateFailure(e,t=!1){const r=Math.max(1,Math.min(86400,Number(e)||10)),n=!0===t?"Hệ thống đang bận.":"Mạng của bạn đang mở quá nhiều yêu cầu video.";if(showFailure(n+" Vui lòng chờ khoảng "+(r>=3600?Math.ceil(r/3600)+" giờ":r>=60?Math.ceil(r/60)+" phút":r+" giây")+" rồi tải lại."),window.streamRateWait)window.streamRateWait.start({label:w,retry:v,seconds:r,message:n+" Vui lòng chờ rồi tải lại."});else{v.disabled=!0;const e=k;b=setTimeout(()=>{e===k&&(b=null,v.disabled=!1)},1e3*r)}}function showFailure(e){clearRateWait(),y.classList.remove("is-interactive"),y.classList.add("is-error"),y.hidden=!1,w.textContent=e,v.hidden=!1}function isExpired(){return!!l&&performance.now()>=l.deadline}function expire(){d||(d=!0,window.dispatchEvent(new CustomEvent("stream-token-expired")),showFailure("Phiên xem đã hết hạn. Vui lòng tải lại trang để tiếp tục."))}v.addEventListener("click",()=>{v.disabled||location.reload()});const S=new Set(["hls","aesgcm","aesgcm-v2"]),C=new URL(e.api).origin;function signedPlaylistURL(e){let t;try{t=new URL(e)}catch(E){return null}const r=t.pathname.replace(/\//g,"").length,n=/^\/(?:[A-Za-z0-9_-]{180}\/){0,30}[A-Za-z0-9_-]{1,180}$/.test(t.pathname),s=/^\/[A-Za-z0-9_-]{80,5500}$/.test(t.pathname),a=(n||s)&&r>=80&&r<=5500&&(""===t.search||"?d"===t.search),i="/conf.php"===t.pathname&&!!t.searchParams.get("t");return t.origin!==C||t.username||t.password||t.hash||!a&&!i?null:t}function acceptIssue(e,t=null){const r=signedPlaylistURL(e?.playlist),n=e?.playlistFormat;if(!r||void 0!==n&&!S.has(n)||void 0!==n&&null!==t&&n!==t||!Number.isInteger(e.issuedAt)||!Number.isInteger(e.expiresAt)||e.expiresAt<=e.issuedAt||e.expiresAt-e.issuedAt>86400)throw new Error("bad_token_response");return{playlist:r.href,format:n??null,deadline:performance.now()+1e3*(e.expiresAt-e.issuedAt)}}async function request(t){const r=new AbortController,n=setTimeout(()=>r.abort(),15e3);try{const n=await fetch(e.api,{method:"POST",credentials:"omit",cache:"no-store",headers:{"Content-Type":"application/json"},body:JSON.stringify({...t,frame_origins:frameOrigins()}),signal:r.signal}),s=503===n.status&&"busy"===n.headers?.get?.("X-Stream-RateLimit");if(429===n.status||s){let e={};try{e=await n.json()}catch(E){}const t=new Error(s?"rate_limiter_busy":"rate_limited");throw t.status=n.status,t.retryAfter=e.retry_after||n.headers?.get?.("Retry-After")||10,t}const a=await n.json();if(!n.ok){const e=new Error(a.error||"issue_failed");throw e.status=n.status,e.retryAfter=a.retry_after,e}return a}finally{clearTimeout(n)}}async function issue(t){return acceptIssue(await request({action:"issue",bootstrap:e.bootstrap,turnstile_response:t,playlist_format:o,pretty_url:!0,path_chunks:!0}),o)}async function refreshBootstrap(){if("string"!=typeof e.bootstrapRefresh||!e.bootstrapRefresh||performance.now()>=g)throw new Error("startup_expired");const t=performance.now(),r=await request({action:"refresh_bootstrap",bootstrap_refresh:e.bootstrapRefresh,nonce:e.nonce});if(r?.video!==e.video||r?.nonce!==e.nonce||"string"!=typeof r.bootstrap||!r.bootstrap||!Number.isInteger(r.bootstrapRemainingSeconds)||r.bootstrapRemainingSeconds<=0||r.bootstrapRemainingSeconds>600||!Number.isInteger(r.bootstrapRefreshRemainingSeconds)||r.bootstrapRefreshRemainingSeconds<=0||r.bootstrapRefreshRemainingSeconds>1800||"boolean"!=typeof r.turnstileEnabled||"string"!=typeof r.turnstileSiteKey||r.turnstileEnabled&&!r.turnstileSiteKey)throw new Error("bad_refresh_response");e.bootstrap=r.bootstrap,e.turnstileEnabled=r.turnstileEnabled,e.turnstileSiteKey=r.turnstileSiteKey,h=t+1e3*r.bootstrapRemainingSeconds-p,g=Math.min(g,t+1e3*r.bootstrapRefreshRemainingSeconds-p)}function proofCurrent(t){return!!t&&(!e.turnstileEnabled||t.token&&t.nonce===e.nonce&&t.siteKey===e.turnstileSiteKey&&performance.now()<t.receivedAt+3e5-p)}function challenge(){return clearRateWait(),e.turnstileEnabled?(w.textContent="Đang tải video…",new Promise((t,r)=>{let n=!1;const finish=(a,i)=>{n||(n=!0,clearTimeout(s),y.classList.remove("is-interactive"),a?r(a):t({token:i,nonce:e.nonce,siteKey:e.turnstileSiteKey,receivedAt:performance.now()}))},s=setTimeout(()=>finish(new Error("verification_timeout")),15e4);window.streamTurnstileReady||(window.streamTurnstileReady=new Promise((e,t)=>{const r=document.createElement("script");r.src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit",r.async=!0,r.onload=e,r.onerror=()=>t(new Error("verification_unavailable")),document.head.appendChild(r)})),window.streamTurnstileReady.then(()=>{if(!n)if(window.turnstile)try{if(null!==f){if("function"!=typeof window.turnstile.remove)throw new Error("verification_unavailable");window.turnstile.remove(f),f=null}f=window.turnstile.render("#turnstile-container",{sitekey:e.turnstileSiteKey,action:"playback",cData:e.nonce,appearance:"interaction-only",theme:"dark",retry:"never","refresh-expired":"never","refresh-timeout":"never","before-interactive-callback":()=>{n||(y.classList.add("is-interactive"),w.textContent="Xác minh để tiếp tục")},"after-interactive-callback":()=>{n||(y.classList.remove("is-interactive"),w.textContent="Đang tải video…")},callback:e=>finish(null,e),"error-callback":()=>(finish(new Error("verification_failed")),!0),"expired-callback":()=>finish(new Error("verification_expired")),"timeout-callback":()=>finish(new Error("verification_timeout")),"unsupported-callback":()=>finish(new Error("verification_unavailable"))})}catch(t){finish(t)}else finish(new Error("verification_unavailable"))},()=>finish(new Error("verification_unavailable")))})):Promise.resolve({token:""})}window.streamAccess={ensure:function ensure(){if(isExpired()&&expire(),d)return Promise.reject(new Error("reload_required"));if(!l&&void 0!==u){const r=u;u=void 0;try{if(e.turnstileEnabled)throw new Error("unexpected_preissued_grant");l=acceptIssue(r,o),clearRateWait(),y.hidden=!0}catch(t){return d=!0,showFailure("Chưa thể mở video. Vui lòng tải lại và thử lại."),Promise.reject(t)}}return l?Promise.resolve(l.playlist):c||(c=(async()=>{try{let e=null,r=0;const renew=()=>{if(++r>2)throw new Error("startup_expired")};for(;;)if(window.streamGuard?.isBlocked?.()&&await window.streamGuard.waitForAccess(),performance.now()>=h&&(renew(),await refreshBootstrap()),proofCurrent(e)||(e=await challenge()),window.streamGuard?.isBlocked?.()&&await window.streamGuard.waitForAccess(),performance.now()>=h||!proofCurrent(e))renew(),performance.now()>=h&&await refreshBootstrap(),proofCurrent(e)||(e=null);else{w.textContent="Đang tải video…";try{l=await issue(e.token);break}catch(t){if("token_expired"!==t.message)throw t;renew(),await refreshBootstrap(),e=null}}return clearRateWait(),y.hidden=!0,l.playlist}catch(t){throw l=null,d=!0,429===t.status||"rate_limiter_busy"===t.message?rateFailure(t.retryAfter,503===t.status&&"rate_limiter_busy"===t.message):"website_blocked"===t.message?(showFailure("Website này đã bị chặn sử dụng trình phát."),v.hidden=!0):"startup_expired"===t.message||"token_expired"===t.message?showFailure("Phiên khởi tạo đã hết hạn. Vui lòng tải lại trang để tiếp tục."):showFailure("Chưa thể mở video. Vui lòng tải lại và thử lại."),t}finally{c=null}})(),c)},nativeHls:i,appleDevice:s,appleJsHls:a,playlistFormat:o,managedHlsEnabled:t,sandboxManagedHlsTrial:r,playbackCapability:n,canUseManagedHls:()=>!d&&!!l&&!isExpired(),get usesEncryptedPlaylist(){return"aesgcm"===l?.format||"aesgcm-v2"===l?.format},onRateLimit:rateFailure,onPlaybackError:()=>!!isExpired()&&(expire(),!0),isSignedPlaylistURL:e=>!!signedPlaylistURL(e),isCurrentPlaylistURL:e=>!!l&&signedPlaylistURL(e)?.href===l.playlist,getGrantedPlaylistFormat:()=>l?.format??null,shouldUseSealedLoader:()=>!i&&"hls"!==l?.format}}(),function(){const e=JSON.parse(document.getElementById("stream-bootstrap").textContent),t=!0===e.sharedCache,r={playerToken:"ITWMv7t88JGzI0xPwW8I0+LveiXX9SWbfdmt0ArUSyc="},n=(()=>{try{const t=e.tvc;if(!t||!0!==t.enabled)return null;for(const[e,r,n]of[["offset_seconds",0,86400],["skip_seconds",0,300],["request_timeout_ms",500,3e4]])if(!Number.isInteger(t[e])||t[e]<r||t[e]>n)return null;if("direct"===t.mode)return"string"!=typeof t.vastxml||t.vastxml.length>32768||!/^\s*(?:<\?xml[^>]*\?>\s*)?<VAST(?:\s|>)/.test(t.vastxml)||/<!DOCTYPE|<!ENTITY/i.test(t.vastxml)?null:t;if(void 0!==t.mode&&"vast"!==t.mode)return null;if(!Array.isArray(t.tags)||!t.tags.length||t.tags.length>10)return null;for(const e of t.tags){if("string"!=typeof e||e.length>2048||/[\s<>"'\\]/.test(e))return null;const t=new URL(e);if("https:"!==t.protocol||t.username||t.password||t.hash)return null}return t}catch(t){return null}})(),s="string"==typeof e.server?.country&&e.server.country.length>0&&e.server.country.length<=40?e.server.country:"Máy chủ hiện tại",a={playerInstance:null,skipAdsForThisSession:!1,skipResumeForThisSession:!1,timers:{},isInitialized:!1,setupGeneration:0,resetGeneration:0,eventsBound:!1,currentVideoHash:null,resumeTime:0,completed:!1,_streamURL:null,_streamPromise:null,_streamPreparation:null,_streamAbortController:null,_streamHandoff:null,_streamReplay:null,_streamReplayTimer:null,_streamGeneration:0,managedPrimeCleanup:null,managedPrimeEvent:null,managedGestureCleanup:null,settingsCleanup:null,mobileCleanup:null,loadProgressCleanup:null,playbackRecoveryCleanup:null,playbackTelemetryCleanup:null,relativeSeeking:null,savePositionCheckpoint:null};function bindLoadProgress(e,t=null){let r=!1,n=null,s=null,a=null,i=null,o=!1,l=!1,c=null,d=new WeakSet;const u=[],m=new Set,p=["progress","loadedmetadata","durationchange","emptied","loadstart","waiting","playing","pause"],safe=e=>(...t)=>{if(!r)try{e(...t)}catch(n){}},on=(t,r)=>{const n=safe(r);try{e.on(t,n),u.push(()=>e.off?.(t,n))}catch(s){}},httpsURL=e=>{try{const t=new URL(e);return"https:"!==t.protocol||t.username||t.password?null:t.href}catch(t){return null}};try{if("string"==typeof t&&t.length<=32768&&!/<!DOCTYPE|<!ENTITY/i.test(t)&&"function"==typeof DOMParser){const e=(new DOMParser).parseFromString(t,"application/xml");if(!e.getElementsByTagName("parsererror").length)for(const t of Array.from(e.getElementsByTagName("MediaFile")).slice(0,16)){const e=httpsURL(t.textContent.trim());e&&m.add(e)}}}catch(g){}const h=safe(e=>{if("emptied"===e.type||"loadstart"===e.type)d.delete(e.target),c=null;else if(l&&n?.classList.contains("jw-flag-ads")&&"VIDEO"===e.target?.tagName&&m.has(httpsURL(e.target.currentSrc))){if(d.add(e.target),"playing"===e.type||"pause"===e.type)return void hide();"waiting"===e.type&&(o=!0)}o&&render()});function render(){if(!function mount(){const t=e.getContainer?.();if(!t?.querySelector||!t?.classList)return!1;if(n!==t){detachDOM(),n=t;for(const e of p)n.addEventListener(e,h,!0)}const r=n.querySelector(".jw-display-icon-display");return!!r&&(s&&s.parentNode===r||(s?.remove(),s=document.createElement("span"),s.className="stream-load-progress",s.setAttribute("aria-hidden","true"),a=document.createElement("span"),a.className="stream-load-progress-value",i=document.createElement("span"),i.className="stream-load-progress-caption",i.textContent="Đã đệm",s.appendChild(a),s.appendChild(i),r.appendChild(s)),!0)}())return;n.classList.toggle("stream-load-progress-active",o);const t=l||n.classList.contains("jw-flag-ads");let r=null;try{r=t?function adBufferedPercent(){if(!l||!n?.classList.contains("jw-flag-ads")||!m.size)return null;const e=Array.from(n.querySelectorAll("video")).filter(e=>m.has(httpsURL(e.currentSrc)));if(1!==e.length)return null;const t=e[0],r=t.duration,s=t.buffered;if(!d.has(t)||!Number.isInteger(t.readyState)||t.readyState<1||!Number.isFinite(r)||r<=0||!s||!Number.isInteger(s.length)||s.length<0||s.length>128)return null;let a=0,i=0;for(let n=0;n<s.length;n++){const e=s.start(n),t=s.end(n);if(!Number.isFinite(e)||!Number.isFinite(t)||e<i||t<e)return null;a+=Math.max(0,Math.min(t,r)-Math.min(e,r)),i=t}return Math.min(100,Math.floor(a/r*100))}():c}catch(g){}const u=null===r?"Đang tải":`${r}%`;a.textContent!==u&&(a.textContent=u),i.hidden=null===r,s.classList.toggle("is-unknown",null===r)}function detachDOM(){if(n){n.classList.remove("stream-load-progress-active");for(const e of p)n.removeEventListener(e,h,!0)}s?.remove(),n=s=a=i=null}function hide(){o=!1,render()}function cleanup(){if(!r){r=!0;for(const e of u)try{e()}catch(g){}try{detachDOM()}catch(g){}}}on("ready",render),on("buffer",()=>{o=!0,render()}),on("bufferChange",t=>{if(l||e.getContainer?.()?.classList?.contains("jw-flag-ads"))return;const r=t?.bufferPercent;c="number"==typeof r&&Number.isFinite(r)&&r>=0&&r<=100&&Number.isFinite(t?.duration)&&t.duration>0?Math.floor(r):null,o&&render()}),on("adRequest",()=>{d=new WeakSet,l=!0,o=!0,c=null,render()}),on("adBuffer",()=>{l=!0,o=!0,render()});for(const f of["adPlay","adStarted","adPause"])on(f,()=>{l=!0,hide()});for(const f of["adComplete","adSkipped","adError"])on(f,()=>{d=new WeakSet,l=!1,c=null,hide()});for(const f of["play","firstFrame","pause"])on(f,()=>{l||hide()});for(const f of["complete","idle","error","setupError","playAttemptFailed"])on(f,hide);return on("seek",()=>{c=null,o&&render()}),on("playlistItem",()=>{d=new WeakSet,l=!1,c=null,hide()}),on("remove",cleanup),safe(render)(),cleanup}function bindPlaybackRecovery(player, generation, onAppendFailure = null) {
    const state=a, init=g, uiManager=m;
    const notify=status=>{try {window.streamSandboxControl?.notify?.(status);}catch (_) {}};
    let intended=false;
    let closed = false, timer = null, notice = null;
    let progressWatch = null, progressTimer = null, seekTarget = null, accessExpired = false;
    let appendRun = null, pendingAppendFailure = null;
    let started = false, buffering = false, paused = false, seeking = false;
    let adActive = false, pageActive = true, lastPosition = null;
    const off = [];
    const current = () => !closed && generation === state.setupGeneration && player === state.playerInstance;
    const inAd = () => adActive || player.getContainer?.()?.classList?.contains('jw-flag-ads');
    const contentActive = () => current() && (started || intended) && !paused && !accessExpired &&
      pageActive && !document.hidden && !inAd() && !window.streamGuard?.isBlocked?.() &&
      document.getElementById('verification')?.hidden !== false;
    const eligible = () => contentActive() && buffering && !seeking;
    const safe = callback => (...args) => {
      if (current()) { try { callback(...args); } catch (_) { /* Recovery m must not affect playback. */ } }
    };
    const on = (name, callback) => {
      const wrapped = safe(callback);
      try { player.on(name, wrapped); off.push(() => player.off?.(name, wrapped)); } catch (_) {}
    };
    const listen = (target, name, callback) => {
      const wrapped = safe(callback);
      target.addEventListener(name, wrapped);
      off.push(() => target.removeEventListener(name, wrapped));
    };
    function clear() {
      clearTimeout(timer); timer = null;
      if (notice) { notice.remove(); notice = null; }
    }
    function emptyActiveMedia() {
      // A nonfatal append warning alone is recoverable. Only classify the R16
      // failure pattern after content has played and its active media has lost
      // metadata AND all buffered ranges. No provider internals are required.
      if (!current() || !started || !pageActive || document.hidden || inAd() ||
          window.streamGuard?.isBlocked?.() || document.getElementById('verification')?.hidden === false) return null;
      const media = player.getContainer?.()?.querySelector?.('video');
      return media?.readyState === 0 && media.paused === false && media.ended !== true &&
        media.buffered?.length === 0 ? media : null;
    }
    function appendSource(media) {
      const source = media?.querySelector?.('source');
      return {media, source, childURL:source?.getAttribute?.('src') || source?.src || '',
        directURL:media?.getAttribute?.('src') || ''};
    }
    function sameAppendSource(run, media) {
      if (!media || run.media !== media) return false;
      const next = appendSource(media);
      return run.source === next.source && run.childURL === next.childURL && run.directURL === next.directURL;
    }
    function queueAppendFailure(run = null, validate = null, failure = null) {
      if (pendingAppendFailure && (pendingAppendFailure.run === null || run !== null)) {
        // JW may emit the terminal append warning and clear media.error in
        // the same turn as the native error. Keep terminal evidence instead
        // of losing both callbacks when native validation no longer matches.
        if (run === null && validate === null) pendingAppendFailure.terminal = true;
        return;
      }
      const pending = {run, validate, failure,
        source:appendSource(player.getContainer?.()?.querySelector?.('video')), terminal:false};
      pendingAppendFailure = pending;
      // Defer teardown until HLS/JW finish dispatching this warning. Progress,
      // a new source, ad, guard change or cleanup can invalidate a nonfatal run.
      Promise.resolve().then(() => {
        if (pendingAppendFailure !== pending) return;
        pendingAppendFailure = null;
        if (!current()) return;
        let acceptedFailure = failure;
        if (validate && !validate()) {
          const media = player.getContainer?.()?.querySelector?.('video');
          if (!pending.terminal || !started || !pageActive || accessExpired || document.hidden || inAd() ||
              window.streamGuard?.isBlocked?.() || document.getElementById('verification')?.hidden === false ||
              !sameAppendSource(pending.source, media) || media.ended === true || media.buffered?.length !== 0 ||
              !(media.readyState === 0 || media.error?.code === 3)) return;
          // The native decode error is gone; retain the established manual
          // terminal-error path, never guess eligibility for an auto rebuild.
          acceptedFailure = null;
        }
        if (run && (appendRun !== run || !sameAppendSource(run, emptyActiveMedia()))) return;
        if (acceptedFailure) {
          try { window.streamSandbox?.pipeline?.({stage:'managed_recovery', state:'detected', phase:acceptedFailure.reason, count:0}); } catch (_) {}
        }
        onAppendFailure(started && !inAd(), acceptedFailure ? {...acceptedFailure, resume:!paused} : null);
      });
    }
    // A paused MMS can lose its source before JW reports an append warning.
    // Observe only the active video's native error, after content has played.
    // Never treat normal empties/ad switches or background suspension as loss.
    let lossMedia = null, lossHandler = null;
    function bindMediaLoss() {
      if (!onAppendFailure) return;
      const media = player.getContainer?.()?.querySelector?.('video');
      if (media === lossMedia) return;
      lossMedia?.removeEventListener?.('error', lossHandler);
      lossMedia = media;
      lossHandler = safe(() => {
        if (!media) return;
        const source = appendSource(media);
        if (!/^blob:/i.test(source.childURL || source.directURL)) return;
        const nativeDecode = media.error?.code === 3;
        const lost = () => started && pageActive && !accessExpired && !document.hidden && !inAd() &&
          !window.streamGuard?.isBlocked?.() && document.getElementById('verification')?.hidden !== false &&
          media === player.getContainer?.()?.querySelector?.('video') && sameAppendSource(source, media) &&
          media.ended !== true && media.buffered?.length === 0 &&
          (nativeDecode ? media.error?.code === 3 : media.readyState === 0);
        // Safari can retain HAVE_ENOUGH_DATA and a running clock after its
        // decoder fails and MMS detaches. Metadata loss is not required.
        if (lost()) queueAppendFailure(null, lost, nativeDecode ? {reason:'native_error'} : null);
      });
      media?.addEventListener?.('error', lossHandler);
    }
    off.push(() => { lossMedia?.removeEventListener?.('error', lossHandler); lossMedia = null; });
    on('ready', bindMediaLoss);
    on('firstFrame', bindMediaLoss);
    function checkMediaLoss() {
      if (!onAppendFailure) return;
      bindMediaLoss();
      // Reinspect on a new intent/foreground event: an error suppressed while
      // hidden is not guaranteed to be dispatched again when the page returns.
      if (lossMedia?.error?.code === 3) lossHandler?.();
    }
    if (onAppendFailure) on('warning', event => {
      const error = event?.sourceError;
      if (event?.code !== 334002 || error?.type !== 'mediaError' || error.details !== 'bufferAppendError') return;
      if (error.fatal === true) { queueAppendFailure(); return; }
      if (error.fatal !== false) return;
      const media = emptyActiveMedia(), now = performance.now();
      if (!media || !Number.isFinite(now)) { appendRun = null; return; }
      // Warning-driven only: no polling and no timer/request on healthy video.
      // Sparse warnings cannot accumulate into a failure across healthy gaps.
      if (!appendRun || !sameAppendSource(appendRun, media) || now < appendRun.lastAt || now - appendRun.lastAt > 2000) {
        appendRun = {...appendSource(media), since:now, lastAt:now, count:1};
        return;
      }
      appendRun.lastAt = now;
      appendRun.count++;
      if (appendRun.count >= 3 && now - appendRun.since >= 5000) queueAppendFailure(appendRun);
    });
    function cancelProgressWatch() {
      clearTimeout(progressTimer); progressTimer = null; progressWatch = null;
    }
    function recovered() { cancelProgressWatch(); appendRun = null; buffering = false; clear(); }
    function showNotice() {}
function watchedMedia(run) {
      const media = player.getContainer?.()?.querySelector?.('video');
      return sameAppendSource(run, media) ? media : null;
    }
    function progressEligible(run) {
      if (!contentActive() || progressWatch !== run) return false;
      const media = watchedMedia(run);
      if (!media || media.ended === true || ['idle', 'complete', 'error'].includes(player.getState?.())) return false;
      // media.paused can stay true after a failed resume. Only a new pause
      // intent/lifecycle event cancels that attempt; JW's state alone is not
      // evidence that content is moving again.
      return true;
    }
    function videoFrames(media) {
      if (!(media?.videoWidth > 0 && media?.videoHeight > 0)) return null;
      try {
        const quality = media.getVideoPlaybackQuality?.();
        const count = quality?.totalVideoFrames ?? media.webkitDecodedFrameCount;
        const dropped = quality?.droppedVideoFrames ?? media.webkitDroppedFrameCount;
        return Number.isFinite(count) && count >= 0
          ? Math.max(0, count - (Number.isFinite(dropped) && dropped >= 0 ? dropped : 0)) : null;
      } catch (_) { return null; }
    }
    function observedProgress(run) {
      const media = watchedMedia(run), position = media?.currentTime, now = performance.now();
      if (!media || media.error || media.seeking === true || media.paused !== false || media.readyState < 2 ||
          !Number.isFinite(position) || !Number.isFinite(now)) return false;
      const frames = videoFrames(media);
      const rate = Number.isFinite(media.playbackRate) && media.playbackRate > 0 ? media.playbackRate : 1;
      if (run.rebase) {
        // The target jump and the frame decoded for a seek are not playback.
        const targetWindow = Math.max(0, now - run.requestedAt) / 1000 * rate + 1;
        if (Number.isFinite(run.target) && (position < run.target - 1 || position > run.target + targetWindow)) return false;
        run.rebase = false; run.position = position; run.at = now; run.frames = frames;
        return false;
      }
      const elapsed = Math.max(0, now - run.at) / 1000;
      const delta = position - run.position;
      if (!Number.isFinite(run.position) || delta < -0.05 || delta > elapsed * rate + 1) {
        // Rebase an unreported native seek/discontinuity too. Never use a JW
        // time event's position as proof that the media element advanced.
        run.position = position; run.at = now; run.frames = frames;
        return false;
      }
      if (frames !== null) {
        if (run.frames === null || frames < run.frames) {
          run.frames = frames; run.position = position; run.at = now;
          return false;
        }
        if (frames <= run.frames) return false;
      }
      return delta >= 0.5;
    }
    function checkProgress() {
      const run = progressWatch;
      if (!run) return;
      if (!progressEligible(run)) { cancelProgressWatch(); clear(); return; }
      if (observedProgress(run)) { seeking = false; seekTarget = null; recovered();notify('playing'); }
    }
    function watchProgress() {
      if (!contentActive()) return;
      const media = player.getContainer?.()?.querySelector?.('video');
      if (!media || media.ended === true) return;
      if (progressWatch && sameAppendSource(progressWatch, media)) return;
      cancelProgressWatch(); clear();
      const target = seeking && Number.isFinite(seekTarget) ? seekTarget : null;
      if (Number.isFinite(target) && Number.isFinite(media.duration) && target >= media.duration - 0.05) return;
      const now = performance.now();
      const run = progressWatch = {...appendSource(media), position:media.currentTime, at:now, requestedAt:now,
        target, rebase:seeking || media.seeking === true, frames:videoFrames(media)};
      // Event-triggered, one bounded deadline. No loop, segment prefetch,
      // playback command, provider access or background request is introduced.
      progressTimer = setTimeout(safe(() => {
        progressTimer = null;
        if (progressWatch !== run) return;
        checkProgress();
        if (progressWatch === run) showNotice(() => progressEligible(run));
      }), 15000);
    }
    function arm() {
      if (progressWatch || timer !== null || notice || !eligible()) return;
      timer = setTimeout(safe(() => {
        timer = null;
        if (!eligible() || (typeof player.getState === 'function' && player.getState() !== 'buffering')) return;
        showNotice(eligible);
      }), 30000);
    }
    on('buffer', () => { buffering = true; arm(); });
    on('playAttempt', () => { if (!inAd()) { intended=true;paused = false; checkMediaLoss(); watchProgress(); } });
    on('play', () => {
      if (inAd()) return;
      intended=true;paused = false;
      checkMediaLoss();
      // Preserve an existing deadline/notice until the DOM media progresses.
      watchProgress();
      if (progressWatch) checkProgress(); else recovered();
    });
    on('firstFrame', () => {
      if (inAd()) return;
      started = true; intended=true;paused = false;
      if (progressWatch) checkProgress(); else { seeking = false; recovered(); }
    });
    on('time', event => {
      if (inAd() || paused) return;
      if (progressWatch) { checkProgress(); return; }
      if (seeking) return;
      if (player.getContainer?.()?.querySelector?.('video')?.error) return;
      const position = event?.position;
      if (!Number.isFinite(position) || position < 0) return;
      if (lastPosition !== null && position > lastPosition + 0.05) {
        started = true;
        if (buffering || timer !== null || notice || appendRun) recovered();
      }
      lastPosition = position;
    });
    on('pause', () => { intended=false;paused = true; recovered(); });
    on('seek', event => {
      seeking = true; seekTarget = Number.isFinite(event?.offset) ? event.offset : null;
      lastPosition = null; recovered(); watchProgress();
    });
    on('seeked', () => { seeking = false; if (progressWatch) checkProgress(); else recovered(); });
    for (const name of ['adRequest', 'adBuffer', 'adPlay', 'adStarted', 'adPause']) {
      on(name, () => { intended=false;adActive = true; recovered(); });
    }
    for (const name of ['adComplete', 'adSkipped', 'adError']) {
      on(name, () => { adActive = false; lastPosition = null; recovered(); });
    }
    on('playAttemptFailed', () => {
      // A rejected resume can leave the same stuck video paused. Keep its
      // explicit intent under observation; pause/ads/source changes cancel it
      // separately. Initial autoplay rejection still uses JW's own m.
      if (started && progressWatch && !paused) return;
      recovered();
    });
    for (const name of ['complete', 'idle', 'error', 'setupError', 'playlistItem']) {
      on(name, () => { intended=false;started = false; lastPosition = null; recovered(); });
    }
    listen(document, 'visibilitychange', () => {
      appendRun = null; cancelProgressWatch(); clear();
      if (!document.hidden) { checkMediaLoss(); watchProgress(); arm(); }
    });
    listen(window, 'pagehide', () => { appendRun = null; pageActive = false; cancelProgressWatch(); clear(); });
    listen(window, 'pageshow', () => { appendRun = null; pageActive = true; checkMediaLoss(); watchProgress(); arm(); });
    // Guard inspection also reports unchanged healthy state periodically.
    // Those reports must not postpone an already running stall deadline.
    listen(window, 'stream:guard', () => {
      checkMediaLoss();
      if (appendRun && !emptyActiveMedia()) appendRun = null;
      if (!contentActive()) { cancelProgressWatch(); clear(); }
      else if (progressWatch) checkProgress(); else if (!eligible()) clear(); else arm();
    });
    listen(window, 'stream-token-expired', () => { intended=false;accessExpired = true;recovered(); });
    function cleanup() {
      if (closed) return;
      closed = true; appendRun = null; pendingAppendFailure = null; cancelProgressWatch(); clear();
      for (const remove of off) { try { remove(); } catch (_) {} }
    }
    on('remove', cleanup);
    return cleanup;
  }
function startupDiagnostics(e){try{const t=window.streamSandbox,r=t?.pipeline;if("function"!=typeof r)return null;const n=a._streamGeneration,now=()=>{try{const e=performance.now();return Number.isFinite(e)&&e>=0?e:null}catch(e){return null}},s=now();if(null===s)return null;const record=(i,o=s)=>{try{if(e!==a.setupGeneration||n!==a._streamGeneration||window.streamSandbox!==t||null===o)return;const s=now();if(null===s||s<o||s-o>864e5)return;Reflect.apply(r,t,[{stage:"startup_phase",phase:i,ms:s-o}])}catch(l){}};return{now,record,observe(e,t){try{null!==t&&["object","function"].includes(typeof t)?Promise.prototype.then.call(t,()=>record(e),()=>{}):record(e)}catch(r){}return t}}}catch(t){return null}}function bindRelativeSeeking(e,t){let r=!1,n=null,s=null,i=null,o=-1/0,l=null,c=!1,d=!1,u=!1;const m=[],allowed=()=>!r&&t===a.setupGeneration&&e===a.playerInstance&&!document.hidden&&!d&&!u&&!1!==document.getElementById?.("verification")?.hidden&&!window.streamGuard?.isBlocked?.()&&!e.getContainer?.()?.classList?.contains("jw-flag-ads")&&["playing","paused","buffering"].includes(e.getState?.()),cancel=()=>{clearTimeout(n),n=null,s=i=null,o=-1/0,l=null},on=(t,r)=>{e.on(t,r),m.push(()=>e.off?.(t,r))},listen=(e,t,r,n=!1)=>{e?.addEventListener?.(t,r,n),m.push(()=>e?.removeEventListener?.(t,r,n))};function issue(){if(n=null,l=null,!allowed())return cancel(),!1;if(null===s||s===i)return!0;i=s,c=!0;try{e.seek(s)}catch(t){return cancel(),!1}finally{c=!1}return!0}on("seek",e=>{if(c)return;const t=Number(e?.offset);null!==i&&Number.isFinite(t)&&Math.abs(t-i)<.01||cancel()}),listen(e.getContainer?.(),"seeking",e=>{if(c)return;const t=Number(e.target?.currentTime);null!==i&&Number.isFinite(t)&&Math.abs(t-i)<.01||cancel()},!0);for(const a of["pause","complete","playlistItem","error","setupError"])on(a,cancel);for(const a of["adRequest","adStarted","adPlay"])on(a,()=>{d=!0,cancel()});for(const a of["adComplete","adSkipped","adError","adBreakEnd"])on(a,()=>{d=!1,cancel()});function cleanup(){if(!r){r=!0,cancel();for(const e of m.splice(0))e()}}return listen(window,"stream:guard",()=>{window.streamGuard?.isBlocked?.()&&cancel()}),listen(window,"stream-token-expired",()=>{u=!0,cancel()}),listen(window,"pagehide",cancel),listen(document,"visibilitychange",()=>{document.hidden&&cancel()}),on("remove",cleanup),{request:function request(t){if(!Number.isFinite(t)||0===t||!allowed())return cancel(),!1;const r=performance.now(),a=Number(e.getPosition?.()),c=Number(e.getDuration?.());if(!Number.isFinite(a))return cancel(),!1;const d=null!==s&&r-o<=400;return s=Math.max(0,(d?s:a)+t),Number.isFinite(c)&&c>0&&(s=Math.min(c,s)),o=r,d?(clearTimeout(n),n=null,s===i?(l=null,!0):(null===l&&(l=r),n=setTimeout(issue,Math.min(180,Math.max(0,l+400-r))),!0)):(clearTimeout(n),i=null,issue())},cleanup}}const i={getCurrentVideoHash:()=>window.videoHash?a.currentVideoHash=window.videoHash:a.currentVideoHash?a.currentVideoHash:null,usesNativeHls:()=>window.streamAccess.nativeHls,addRandomParam:e=>{const t=Math.floor(1e6*Math.random());return e.includes("?")?`${e}&r=${t}`:`${e}?r=${t}`}},o={keyVideo:null,keyPromise:null,parseEnvelope(e){const t=String(e).trim().split(/\r?\n/),r=/^#ENC-AESGCM;iv=([a-fA-F0-9]{24})$/.exec(t[1]||"");if(4!==t.length||"#EXTM3U"!==t[0]||!r||"#EXT-X-B65:0-138"!==t[2]||!/^[A-Za-z0-9+/]+={0,2}$/.test(t[3])||t[3].length%4!=0)throw new Error("bad_playlist_envelope");const n=Uint8Array.from(r[1].match(/../g),e=>parseInt(e,16)),s=Uint8Array.from(atob(t[3]),e=>e.charCodeAt(0));if(s.length<=16)throw new Error("bad_playlist_envelope");return{iv:n,combined:s}},async getKey(){if(!window.crypto?.subtle)throw new Error("webcrypto_required");const e=i.getCurrentVideoHash();if(!e)throw new Error("video_key_required");return this.keyPromise&&this.keyVideo===e||(this.keyVideo=e,this.keyPromise=(async()=>{const t=new TextEncoder,r=await window.crypto.subtle.importKey("raw",t.encode("stream-derive-v1"),{name:"HMAC",hash:"SHA-256"},!1,["sign"]),n=await window.crypto.subtle.sign("HMAC",r,t.encode(e));return window.crypto.subtle.importKey("raw",n,{name:"AES-GCM"},!1,["decrypt"])})()),this.keyPromise},async decryptM3U8(e){const{iv:t,combined:r}=this.parseEnvelope(e),n=await this.getKey(),s=await window.crypto.subtle.decrypt({name:"AES-GCM",iv:t,tagLength:128},n,r),a=new TextDecoder("utf-8",{fatal:!0}).decode(s);if(!/^#EXTM3U(?:\r?\n|$)/.test(a))throw new Error("bad_decrypted_playlist");return a},async unwrapM3U8(e,t=!1){const r=String(e);if(r.includes("#ENC-AESGCM")||r.includes("#EXT-X-B65"))return this.decryptM3U8(r);if(t)throw new Error("unencrypted_playlist");if(!/^#EXTM3U(?:\r?\n|$)/.test(r))throw new Error("bad_playlist");return r}},l=new Set;function warmMediaConnections(e,t){if(!(l.size>=2||document.hidden||window.streamGuard?.isBlocked?.()))try{const warm=e=>{if(l.size>=2)return;let r;try{r=new URL(e,t)}catch(n){return}if("https:"!==r.protocol||r.username||r.password||r.origin===location.origin||l.has(r.origin))return;if(!Array.from(document.querySelectorAll?.('link[rel="preconnect"]')||[]).some(e=>e.href.replace(/\/$/,"")===r.origin&&"anonymous"===e.crossOrigin)){const e=document.createElement("link");e.rel="preconnect",e.crossOrigin="anonymous",e.href=r.origin,document.head.appendChild(e)}l.add(r.origin)};let r=!1,n=e.slice(0,16384);e.length>n.length&&(n=n.slice(0,n.lastIndexOf("\n")+1));for(const e of n.split("\n",96)){const t=e.trim();if(t.startsWith("#EXTINF:"))r=!0;else if(t.startsWith("#EXT-X-MAP:")){const e=/(?:^#EXT-X-MAP:|,)\s*URI="([^"]+)"/.exec(t);e&&warm(e[1])}else t&&!t.startsWith("#")&&(r&&warm(t),r=!1);if(l.size>=2)break}}catch(r){}}const c={async waitForAccess(e){if(await(window.streamGuard?.waitForAccess?.()),await window.streamAccess.ensure(),e!==a._streamGeneration)throw new Error("playlist_request_cancelled")},async getStreamURL(){const e=a._streamGeneration,t=startupDiagnostics(a.setupGeneration),r=this.startPreparation(e),n=this.waitForAccess(e);t?.observe("prepare_source",r),t?.observe("prepare_guard",n);const[s]=await Promise.all([r,n]);return await this.waitForAccess(e),t?.record("prepare_stream"),s},startPreparation(e){if(a._streamPreparation?.generation===e)return a._streamPreparation.promise;const t=this.prepareStreamURL(e),r=new Promise((e,r)=>{t.catch(r)});return a._streamPreparation={generation:e,promise:t,failure:r},t.catch(()=>{}),r.catch(()=>{}),t},async getAuthorizedStreamURL(){const e=a._streamGeneration,t=startupDiagnostics(a.setupGeneration),r=this.startPreparation(e),n=this.waitForAccess(e);t?.observe("prepare_source",r),t?.observe("prepare_guard",n);const s=a._streamPreparation.failure,[i]=await Promise.race([Promise.all([window.streamAccess.ensure(),n]),s]);return await this.waitForAccess(e),t?.record("prepare_stream"),i},async prepareStreamURL(e){const r=await window.streamAccess.ensure();if(window.streamGuard?.isBlocked?.()&&await this.waitForAccess(e),e!==a._streamGeneration)throw new Error("playlist_request_cancelled");const n=window.streamAccess.getGrantedPlaylistFormat?.()??null;if(i.usesNativeHls()||"hls"===n)return r;if(a._streamURL)return a._streamURL;if(a._streamPromise)return a._streamPromise;const s=new AbortController;a._streamAbortController=s;const l=setTimeout(()=>s.abort(),15e3);return a._streamPromise=(async()=>{try{const l=performance.now(),c=await fetch(r,{credentials:"omit",cache:t?"default":"no-store",signal:s.signal}),d=performance.now();if(429===c.status||503===c.status&&"busy"===c.headers?.get?.("X-Stream-RateLimit"))throw window.streamAccess.onRateLimit?.(c.headers?.get?.("Retry-After")||10,503===c.status),new Error("rate_limited");if(!c.ok)throw new Error("playlist_fetch_failed");const u=await c.text(),m=await o.unwrapM3U8(u,"aesgcm-v2"===n||"aesgcm"===n);if(await window.streamAccess.ensure(),s.signal.aborted||e!==a._streamGeneration)throw new Error("playlist_request_cancelled");warmMediaConnections(m,c.url||r);const p=performance.now(),h=(new TextEncoder).encode(u).byteLength;a._streamHandoff={generation:e,url:r,decrypted:!0,response:{url:c.url||r,data:m,code:c.status},networkDetails:c,stats:{aborted:!1,loaded:h,retry:0,total:h,chunkCount:1,bwEstimate:0,loading:{start:l,first:d,end:p},parsing:{start:0,end:0},buffering:{start:0,first:0,end:0}}};const g=function playlistReplaySeconds(e,r,n,s){if(!t||"string"!=typeof e||e.length>262144)return 0;try{const t=r?.headers,a=t?.get?.("X-Stream-Playlist-Reuse"),i=t?.get?.("Cache-Control")||"",o=[...i.matchAll(/(?:^|,)\s*s-maxage\s*=\s*(\d+)\s*(?=,|$)/gi)],l=Date.parse(t?.get?.("Date")||""),c=t?.get?.("Age");if(!/^\d+$/.test(a||"")||Number(a)<=0||!Number.isSafeInteger(Number(a))||1!==o.length||!Number.isSafeInteger(Number(o[0][1]))||!/(?:^|,)\s*public\s*(?=,|$)/i.test(i)||/(?:^|,)\s*(?:no-store|no-cache|private)(?:\s|=|,|$)/i.test(i)||!Number.isFinite(l)||null!=c&&!/^\d+$/.test(c))return 0;const d=Math.max(0,s-n)/1e3,u=Math.max(0,(Date.now()-l)/1e3,Number(c||0)+d),m=Math.min(30,Number(a)-u,Number(o[0][1])-u);if(!(m>0)||!Number.isFinite(m)||!/^#EXT-X-ENDLIST\s*$/m.test(e)||/^#EXT-X-(?:STREAM-INF|I-FRAME-STREAM-INF|MEDIA|RENDITION-REPORT|PART|PRELOAD-HINT|SERVER-CONTROL|DEFINE|CONTENT-STEERING|SKIP):/m.test(e)||/^#EXT-X-PLAYLIST-TYPE:\s*EVENT\s*$/m.test(e))return 0;const stableURI=e=>{const t=new URL(e,r.url);return!("https:"!==t.protocol||t.username||t.password||t.search||t.hash||/\.m3u[89]$/i.test(t.pathname))};for(const r of e.split(/\r\n|\n|\r/)){const e=r.trim();if(e)if("#"!==e[0]){if(!stableURI(e))return 0}else if(e.includes("URI=")){if(!/^#EXT-X-(?:KEY|MAP):/.test(e))return 0;const t=[...e.matchAll(/(?:^|,)\s*URI="([^"]+)"/g)],r=/^#EXT-X-(?:KEY|MAP):\s*URI="([^"]+)"/.exec(e);if(r&&t.push(r),!t.length||t.some(e=>!stableURI(e[1])))return 0}}return m}catch(a){return 0}}(m,c,l,p);if(g>0){clearTimeout(a._streamReplayTimer);const t=a._streamReplay={generation:e,url:r,expires:p+1e3*g,response:{...a._streamHandoff.response}};a._streamReplayTimer=setTimeout(()=>{a._streamReplay===t&&(a._streamReplay=null),a._streamReplayTimer=null},Math.ceil(1e3*g))}a._streamURL=r;try{window.streamSandbox?.playlistResources?.(m,c.url||r)}catch(i){}return window.streamSandbox?.pipeline?.({stage:"entry_decrypted",format:n,role:"root"}),a._streamURL}finally{clearTimeout(l),a._streamAbortController===s&&(a._streamAbortController=null,a._streamPromise=null)}})(),a._streamPromise},takeHandoff(e,t){const r=a._streamHandoff;if(r&&r.generation===t&&r.url===e)return a._streamHandoff=null,r;const n=a._streamReplay,s=performance.now();return n&&n.generation===t&&n.url===e&&!0===window.streamAccess.isCurrentPlaylistURL?.(e)?s>=n.expires?(clearTimeout(a._streamReplayTimer),a._streamReplayTimer=null,a._streamReplay=null,null):{decrypted:!0,reused:!0,expires:n.expires,response:{...n.response},networkDetails:null,stats:{aborted:!1,loaded:0,retry:0,total:0,chunkCount:0,bwEstimate:0,loading:{start:s,first:s,end:s},parsing:{start:0,end:0},buffering:{start:0,first:0,end:0}}}:null},resetCache(){a._streamGeneration++,a._streamAbortController?.abort(),a._streamURL=null,a._streamPromise=null,a._streamPreparation=null,a._streamAbortController=null,a._streamHandoff=null,clearTimeout(a._streamReplayTimer),a._streamReplayTimer=null,a._streamReplay=null}};class SealedPlaylistLoader{constructor(e){this.config=e,this.context=null,this.callbacks=null,this.loader=null,this.responseHeaders=null,this.stats={aborted:!1,loaded:0,retry:0,total:0,chunkCount:0,bwEstimate:0,loading:{start:0,first:0,end:0},parsing:{start:0,end:0},buffering:{start:0,first:0,end:0}},this.generation=a._streamGeneration,this.aborted=!1,this.destroyed=!1,this.settled=!1}load(e,t,r){this.context=e,this.loaderConfig=t,this.callbacks=r,this.owned=!0===window.streamAccess.isSignedPlaylistURL?.(e?.url),this.owned?this.start(e,t):this.startBase(e,t,!1)}async start(e,t){try{if(await window.streamAccess.ensure(),window.streamGuard?.isBlocked?.()&&await c.waitForAccess(this.generation),!this.active())return;const r=a._streamPreparation;if(r?.generation===this.generation&&!0===window.streamAccess.isCurrentPlaylistURL?.(e.url)&&(await r.promise,await window.streamAccess.ensure(),window.streamGuard?.isBlocked?.()&&await c.waitForAccess(this.generation),!this.active()))return;const n=c.takeHandoff(e.url,this.generation);if(n)return this.stats=n.stats,this.responseHeaders=n.networkDetails?.headers||null,void(await this.finishSuccess(n.response,n.stats,e,n.networkDetails,!0===n.decrypted,!0===n.reused,n.expires));this.startBase(e,t,!0)}catch(r){this.finishError(r,e)}}startBase(e,t,r){try{const n=this.config?.loader;if("function"!=typeof n||n===SealedPlaylistLoader)throw new Error("playlist_loader_unavailable");if(this.loader=new n(this.config),this.loader.stats&&(this.stats=this.loader.stats),!this.active())return void this.loader.abort?.();this.loader.load(e,t,{onSuccess:(t,n,s,a)=>{this.stats=n||this.stats,r?this.finishSuccess(t,this.stats,s||e,a):this.finishPlain(t,this.stats,s||e,a)},onError:(...e)=>this.finishCallback("onError",e),onTimeout:(...e)=>this.finishCallback("onTimeout",e),onAbort:(...e)=>this.finishAbort(e),onProgress:(...e)=>{this.active()&&this.callbacks?.onProgress?.(...e)}})}catch(n){this.finishError(n,e)}}active(){return!this.aborted&&!this.destroyed&&!this.settled&&this.generation===a._streamGeneration}async finishSuccess(e,t,r,n,s=!1,a=!1,i=0){let l;try{if(!this.active())return;const t=window.streamAccess.getGrantedPlaylistFormat?.()??null,n=!0===window.streamAccess.isCurrentPlaylistURL?.(r?.url),d="aesgcm-v2"===t||"aesgcm"===t&&n;if(l=s?await o.unwrapM3U8(e?.data,!1):await o.unwrapM3U8(e?.data,d),await window.streamAccess.ensure(),window.streamGuard?.isBlocked?.()&&await c.waitForAccess(this.generation),!this.active())return;if(a&&performance.now()>=i)return void this.startBase(r,this.loaderConfig,!0);warmMediaConnections(l,e?.url||r.url)}catch(u){return void this.finishError(u,r,t,n)}const d=this.callbacks;if(this.settled=!0,!s)try{window.streamSandbox?.playlistResources?.(l,e?.url||r.url)}catch(m){}window.streamSandbox?.pipeline?.({stage:a?"playlist_reused":s?"playlist_handoff":"playlist_decoded",role:!0===window.streamAccess.isCurrentPlaylistURL?.(r?.url)?"root":"child"}),d?.onSuccess?.({...e,data:l},t,r,n)}finishPlain(e,t,r,n){if(!this.active())return;const s=this.callbacks;this.settled=!0,s?.onSuccess?.(e,t,r,n)}finishError(e,t=this.context,r=this.stats,n=null){if(!this.active())return;const s=this.callbacks;this.settled=!0,window.streamSandbox?.pipeline?.({stage:"pipeline_error",code:"playlist_load_failed",role:!0===window.streamAccess.isCurrentPlaylistURL?.(t?.url)?"root":"child"}),s?.onError?.({code:0,text:e?.message||"playlist_decrypt_failed"},t,n,r)}finishCallback(e,t){if(!this.active())return;const r=this.callbacks;this.settled=!0,r?.[e]?.(...t)}finishAbort(e=[]){if(this.destroyed||this.settled)return;const t=this.callbacks;this.aborted=!0,this.stats.aborted=!0,this.settled=!0,t?.onAbort?.(...e.length?e:[this.stats,this.context,null])}abort(){this.destroyed||this.settled||(this.aborted=!0,this.stats.aborted=!0,this.loader?.abort?.(),this.settled||this.finishAbort())}destroy(){this.destroyed||(this.destroyed=!0,this.aborted=!0,this.loader?.destroy?.(),this.loader=null,this.responseHeaders=null,this.callbacks=null)}getCacheAge(){const e=this.loader?.getCacheAge?.();if(null!=e)return e;const t=this.getResponseHeader("age");return"string"==typeof t&&/^\s*[\d.]+\s*$/.test(t)?parseFloat(t):null}getResponseHeader(e){const t=this.loader?.getResponseHeader?.(e);return null!=t?t:this.responseHeaders?.get?.(e)??null}}function needsLegacyManagedHlsFix(){const e=window.jwplayer?.version;return"string"==typeof e&&/^8\.38\.2(?:\+[!-~]+)?$/.test(e)}function needsManagedPrimeGuard(){const e=window.jwplayer?.version;return"string"==typeof e&&/^8\.(?:38\.2|51\.3)(?:\+[!-~]+)?$/.test(e)}let d=null;function enableManagedHlsProvider(){const e=function needsCurrentManagedHlsFix(){const e=window.jwplayer?.version;return!0===window.streamAccess.managedHlsEnabled&&!1===window.streamAccess.playbackCapability?.jwSafari&&"string"==typeof e&&/^8\.51\.3(?:\+[!-~]+)?$/.test(e)}();if(!needsLegacyManagedHlsFix()&&!e||!0!==window.streamAccess.appleJsHls||window.MediaSource||"function"!=typeof window.ManagedMediaSource?.isTypeSupported)return;const t=window.jwplayer?.api?.availableProviders,r=Array.isArray(t)&&t.find(e=>"hlsjs"===e?.name);if(!r||"function"!=typeof r.supports)throw new Error("managed_hls_provider_unavailable");if(d===r)return;const n=r.supports;r.supports=function(t,...r){try{const r="string"==typeof t?.file?t.file:t?.file?.url,n=/hls|m3u8/.test(String(t?.type||"").toLowerCase())||String(r||"").toLowerCase().includes(".m3u8"),s=(Array.isArray(t?.mediaTypes)&&t.mediaTypes.length?t.mediaTypes:['video/mp4; codecs="avc1.42E01E,mp4a.40.2"']).every(e=>"string"==typeof e&&!0===window.ManagedMediaSource.isTypeSupported(e));if((!e||!0===window.streamAccess.canUseManagedHls?.())&&!t?.drm&&n&&!0===t?.safarihlsjs&&s&&!0===window.streamAccess.isCurrentPlaylistURL?.(r)&&!0===window.streamAccess.shouldUseSealedLoader?.())return!0}catch(s){}return n.apply(this,[t,...r])},d=r}function armManagedPrimeGuard(e,t,r="before_play",n=window.event){if(!needsManagedPrimeGuard())return;if(a.managedPrimeEvent===n&&a.managedPrimeCleanup)return;a.managedPrimeCleanup?.(),a.managedPrimeCleanup=null;const s=e?.getContainer?.(),i=s?.querySelector?.("video");if(!i||"function"!=typeof i.load)return;let o=i.querySelector?.("source"),l=o?.getAttribute?.("src")||o?.src||"",c="window_gesture"===r&&!o;if(i.getAttribute?.("src")||!c&&!/^blob:/i.test(l))return;const d=Object.getOwnPropertyDescriptor(i,"load");if(d&&(!("value"in d)||!d.writable))return;const u=i.load;let m,p=!0,h=0;const restore=()=>{if(p){p=!1,clearTimeout(m);try{i.load===guardedLoad&&(d?Object.defineProperty(i,"load",d):delete i.load)}catch(e){}a.managedPrimeCleanup===restore&&(a.managedPrimeCleanup=null,a.managedPrimeEvent=null)}};function guardedLoad(...s){const d=i.querySelector?.("source"),m=d?.getAttribute?.("src")||d?.src||"",g=p&&this===i&&t===a.setupGeneration&&e===a.playerInstance&&!i.getAttribute?.("src")&&window.event===n;if(c&&g&&(!d||/^blob:/i.test(m))){d&&(o=d,l=m,c=!1);try{return Reflect.apply(u,this,s)}catch(y){throw restore(),y}}const f=needsLegacyManagedHlsFix()||i.readyState>=1;if(!g||d!==o||m!==l||!f)return restore(),Reflect.apply(u,this,s);h++,("window_gesture"!==r||h>=2)&&restore();try{window.streamSandbox?.pipeline?.({stage:"managed_prime_guard",state:"suppressed",phase:r,count:h})}catch(w){}}try{Object.defineProperty(i,"load",d?{...d,value:guardedLoad}:{value:guardedLoad,writable:!0,configurable:!0})}catch(g){restore()}p&&(a.managedPrimeCleanup=restore,"window_gesture"===r?(a.managedPrimeEvent=n,m=setTimeout(restore,0)):Promise.resolve().then(restore))}const u={getStorageKey:e=>e?`videoWatchTime_${e}`:null,getSkipResumeKey:e=>e?`skipResume_${e}`:null,setItem(e,t){try{return localStorage.setItem(e,t),!0}catch(r){return console.warn("localStorage.setItem thất bại:",r),!1}},getItem(e){try{return localStorage.getItem(e)}catch(t){return console.warn("localStorage.getItem thất bại:",t),null}},removeItem(e){try{localStorage.removeItem(e)}catch(t){console.warn("localStorage.removeItem thất bại:",t)}},saveWatchTime(e,t){const r=this.getStorageKey(e);return!(!e||!Number.isFinite(t)||t<1||!r)&&(this.setItem(r,t.toString()),!0)},getSavedWatchTime(e){const t=e&&this.getStorageKey(e),r=t?this.getItem(t):null,n=r?Number(r):0;return Number.isFinite(n)&&n>0?n:0},clearWatchTime(e){e&&(this.removeItem(this.getStorageKey(e)),this.removeItem(this.getSkipResumeKey(e)))},setSkipResume(e){e&&(a.skipResumeForThisSession=!0)},shouldSkipResume(e){return e&&this.removeItem(this.getSkipResumeKey(e)),!!e&&a.skipResumeForThisSession}},m={showErrorMessage(message) {
  const state=a, init=g, playerManager=p, streamManager=c, utils=i;
  if (window.streamAccess?.onPlaybackError?.() || document.getElementById('verification')?.hidden===false) return;
  init.saveCurrentPosition();
  const hash=utils.getCurrentVideoHash(),reset=state.resetGeneration;
  state.setupGeneration++;
  const generation=state.setupGeneration;
  playerManager._setupInProgress=false;
  playerManager.cleanup();
  streamManager.resetCache();
  const player=document.getElementById('player');
  if (!player) return;
  player.innerHTML='<div class="stream-playback-error" role="alert" style="position:fixed;inset:0;z-index:999999"><div class="stream-playback-recovery"><p></p><button class="stream-playback-reload" type="button" data-player-reload>Tải lại trang</button></div></div>';
  player.querySelector('.stream-playback-recovery').querySelector('p').textContent=message || 'Đã xảy ra lỗi khi phát video. Vui lòng tải lại trang.';
  let reloading=false;
  player.querySelector('[data-player-reload]').addEventListener('click',event=>{
    event.preventDefault();event.stopPropagation();
    if (reloading || generation!==state.setupGeneration || reset!==state.resetGeneration || hash!==utils.getCurrentVideoHash()) return;
    reloading=true;
    init.saveCurrentPosition();
    if (typeof window.streamSandboxControl?.reload==='function') window.streamSandboxControl.reload();
    else location.reload();
  });
  try {window.streamSandboxControl?.notify?.('error');} catch (_) {}
},createResumePopup(){if(this._resumeComponent)return this._resumeComponent;const e=document.createElement("div");e.id="resumeOverlay",e.className="stream-resume",e.hidden=!0,e.innerHTML='\n        <div class="stream-resume-card" role="dialog" aria-modal="true" aria-labelledby="stream-resume-title">\n          <h2 class="stream-resume-title" id="stream-resume-title">Tiếp tục xem?</h2>\n          <p class="stream-resume-copy">\n            Bạn đã dừng tại <span class="stream-resume-time" id="resumeTime"></span>\n          </p>\n          <div class="stream-resume-actions">\n            <button class="stream-resume-button" id="resumeBtn" type="button">Tiếp tục xem</button>\n            <button class="stream-resume-button stream-resume-button-secondary" id="restartBtn" type="button">Xem lại từ đầu</button>\n          </div>\n        </div>',document.body.appendChild(e);const t=e.querySelector("#resumeBtn"),r=e.querySelector("#restartBtn"),n=e.querySelector("#resumeTime");return t.onclick=async()=>{a.skipAdsForThisSession=!0,e.hidden=!0;try{await p.setupPlayer(!1,a.resumeTime)}finally{h._resumeInProgress=!1}},r.onclick=async()=>{const t=i.getCurrentVideoHash();t&&(u.clearWatchTime(t),u.setSkipResume(t)),a.skipAdsForThisSession=!1,a.skipResumeForThisSession=!0,e.hidden=!0;try{await p.setupPlayer(!0,0)}finally{h._resumeInProgress=!1}},this._resumeComponent={overlay:e,resumeBtn:t,restartBtn:r,resumeTimeSpan:n},this._resumeComponent},showResumePopup(e){const t=this.createResumePopup();a.resumeTime=Math.floor(e);const r=Math.floor(a.resumeTime/60),n=a.resumeTime%60;t.resumeTimeSpan.textContent=`${r} phút ${n} giây`,t.overlay.hidden=!1,t.resumeBtn.focus()},setupSeekButtons(e){const seekForward=e=>{e?.preventDefault(),e?.stopPropagation(),a.relativeSeeking?.request(10)},bindForward=e=>{e.removeAttribute("id"),e.removeAttribute("onclick"),e.classList.remove("jw-icon-rewind","jw-display-icon-rewind","stream-seek-backward"),e.setAttribute("role","button"),e.setAttribute("tabindex","0"),e.onclick=seekForward,"BUTTON"!==e.tagName&&(e.onkeydown=e=>{"Enter"!==e.key&&" "!==e.key||seekForward(e)})},decorateSeekIcon=(e,t)=>{if(!e)return;const r="forward"===t?"Tua tới 10 giây":"Tua lại 10 giây";e.classList.add("stream-seek-icon",`stream-seek-${t}`),e.setAttribute("aria-label",r),e.innerHTML=(e=>`<svg class="stream-seek-svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="${"forward"===e?"M15.6 4.1l4.2 3.2-4.2 3.2V8.2A7.2 7.2 0 1 0 18 13.4":"M8.4 4.1 4.2 7.3l4.2 3.2V8.2A7.2 7.2 0 1 1 6 13.4"}"/><text x="12" y="15.5">10</text></svg>`)(t)},t=e.querySelector(".jw-button-container .jw-icon-rewind");if(decorateSeekIcon(t,"backward"),t&&!e.querySelector(".forward-control-bar-button")){const e=t.cloneNode(!0);bindForward(e),decorateSeekIcon(e,"forward"),e.classList.add("forward-control-bar-button"),t.parentNode.insertBefore(e,t.nextElementSibling)}const r=e.querySelector(".jw-display-icon-rewind"),n=r?.querySelector(".jw-icon-rewind");if(decorateSeekIcon(n,"backward"),r?.setAttribute("aria-label","Tua lại 10 giây"),r&&!e.querySelector(".forward-display-button")){const t=r.cloneNode(!0),n=t.querySelector(".jw-icon-rewind");n?.classList.remove("jw-icon-rewind","stream-seek-backward"),n?.removeAttribute("id"),n?.setAttribute("tabindex","-1"),decorateSeekIcon(n,"forward"),t.setAttribute("aria-label","Tua tới 10 giây"),t.classList.add("forward-display-button"),bindForward(t);const s=e.querySelector(".jw-display-icon-next");s?(s.parentNode.insertBefore(t,s),s.style.display="none"):r.parentNode.appendChild(t)}},setupSettingsMenu(e){if(e.querySelector(".stream-settings-panel"))return;const t=a.playerInstance,r=e.querySelector(".jw-button-container .jw-icon-settings");if(!t||!r)return;a.settingsCleanup?.();const n=document.createElement("section");n.id="stream-settings-panel",n.className="stream-settings-panel",n.hidden=!0,n.setAttribute("role","dialog"),n.setAttribute("aria-label","Cài đặt trình phát"),e.appendChild(n),e.classList.add("stream-custom-settings-enabled"),r.setAttribute("aria-haspopup","dialog"),r.setAttribute("aria-controls",n.id),r.setAttribute("aria-expanded","false"),r.setAttribute("aria-label","Cài đặt");const i={quality:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h7M15 7h5M11 4v6M4 17h4M12 17h8M8 14v6M4 12h12M20 12h0M16 9v6"/></svg>',speed:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 15a8 8 0 0 1 16 0M12 15l4-4"/><circle cx="12" cy="15" r="1"/></svg>',server:'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="6" rx="2"/><rect x="4" y="14" width="16" height="6" rx="2"/><path d="M8 7h.01M8 17h.01M12 7h5M12 17h5"/></svg>',aspect:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4H4v5M15 20h5v-5M4 9l6-6M20 15l-6 6"/></svg>',chevron:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>',back:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg>',check:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>',refresh:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 7v5h-5M4 17v-5h5M18.2 9A7 7 0 0 0 6.4 6.4L4 9M5.8 15A7 7 0 0 0 17.6 17.6L20 15"/></svg>'},o=[{value:"auto",label:"Tự động",ratio:null},{value:"4:3",label:"4:3",ratio:4/3},{value:"16:9",label:"16:9",ratio:16/9}];let l="root",c=o[0],d=null,u=null,m=0;const updateAspectLayout=()=>{if(!c.ratio)return;const{width:t,height:r}=e.getBoundingClientRect();if(!(t>0&&r>0))return;const n=Math.min(t,r*c.ratio);e.style.setProperty("--stream-video-width",`${n}px`),e.style.setProperty("--stream-video-height",n/c.ratio+"px")},setAspect=t=>{if(d?.disconnect(),d=null,window.removeEventListener("resize",updateAspectLayout),c=t,e.classList.toggle("stream-fixed-aspect",!!t.ratio),!t.ratio)return e.style.removeProperty("--stream-video-width"),void e.style.removeProperty("--stream-video-height");updateAspectLayout(),"function"==typeof ResizeObserver?(d=new ResizeObserver(updateAspectLayout),d.observe(e)):window.addEventListener("resize",updateAspectLayout)},qualityLevels=()=>{try{const e=t.getQualityLevels?.();return Array.isArray(e)?e:[]}catch(e){return[]}},qualityIndex=()=>{try{const e=Number(t.getCurrentQuality?.());return Number.isInteger(e)&&e>=0?e:0}catch(e){return 0}},qualityLabel=(e,t)=>{if(0===t)return"Auto";if(Number.isFinite(Number(e?.height))&&Number(e.height)>0)return`${Math.round(Number(e.height))}p`;return("string"==typeof e?.label?e.label.trim().slice(0,30):"")||`Mức ${t}`},currentRate=()=>{try{const e=Number(t.getPlaybackRate?.());return Number.isFinite(e)&&e>=.25&&e<=4?e:1}catch(e){return 1}},header=(e,t=!1)=>`\n        <header class="stream-settings-header">\n          <button class="stream-settings-back" type="button" data-settings-action="back" aria-label="Quay lại">${i.back}</button>\n          <h2>${e}</h2>\n          ${t?`<button class="stream-settings-refresh" type="button" data-settings-action="refresh-server" aria-label="Đo lại độ trễ">${i.refresh}</button>`:'<span class="stream-settings-header-space" aria-hidden="true"></span>'}\n        </header>`,rootRow=(e,t)=>`\n        <button class="stream-settings-row" type="button" data-settings-view="${e}">\n          <span class="stream-settings-row-icon">${i[e]}</span>\n          <span class="stream-settings-row-label">${t}</span>\n          <span class="stream-settings-row-value" data-settings-value="${e}"></span>\n          <span class="stream-settings-chevron">${i.chevron}</span>\n        </button>`,renderRoot=()=>{l="root",n.innerHTML=`\n          <header class="stream-settings-header stream-settings-root-header"><h2>Cài đặt</h2></header>\n          <div class="stream-settings-list">\n            ${rootRow("quality","Chất lượng")}\n            ${rootRow("speed","Tốc độ")}\n            ${rootRow("server","Máy chủ")}\n            ${rootRow("aspect","Tỉ lệ màn hình")}\n          </div>`,n.querySelector('[data-settings-value="quality"]').textContent=(()=>{const e=qualityLevels(),t=qualityIndex();return e[t]?qualityLabel(e[t],t):"Auto"})(),n.querySelector('[data-settings-value="speed"]').textContent=(e=>{const t=Number(e);return`${Number.isFinite(t)?Number(t.toFixed(2)):1}x`})(currentRate()),n.querySelector('[data-settings-value="server"]').textContent=s,n.querySelector('[data-settings-value="aspect"]').textContent=c.label},renderQuality=()=>{l="quality",n.innerHTML=`${header("Chất lượng")}<div class="stream-settings-options" data-settings-options="quality"></div>`;const e=n.querySelector('[data-settings-options="quality"]'),t=qualityLevels(),r=t.length?t:[{label:"Auto"}],s=qualityIndex();if(r.forEach((t,r)=>{const n=document.createElement("button");n.type="button",n.className="stream-settings-option"+(r===s?" is-active":""),n.dataset.settingsQuality=String(r),n.innerHTML=`<span class="stream-settings-option-label"></span><span class="stream-settings-check">${i.check}</span>`,n.querySelector(".stream-settings-option-label").textContent=qualityLabel(t,r),e.appendChild(n)}),t.length<=1){const t=document.createElement("p");t.className="stream-settings-note",t.textContent="Nguồn hiện chỉ có chế độ tự động.",e.appendChild(t)}},updateSpeedView=()=>{if("speed"!==l)return;const e=currentRate(),t=n.querySelector("[data-settings-speed-readout]"),r=n.querySelector("[data-settings-speed-range]");t&&(t.textContent=`${e.toFixed(2)}x`),r&&(r.value=String(Math.min(2,Math.max(.25,e)))),n.querySelectorAll("[data-settings-rate]").forEach(t=>{t.classList.toggle("is-active",Number(t.dataset.settingsRate)===e)})},setRate=e=>{const r=Math.min(2,Math.max(.25,Math.round(4*Number(e))/4));Number.isFinite(r)&&(t.setPlaybackRate?.(r),updateSpeedView())},updateServerProbe=(e,t=null)=>{if("server"!==l)return;const r=n.querySelector("[data-settings-server-latency]"),s=n.querySelector("[data-settings-server-status]"),a=n.querySelector(".stream-server-bars");if(!r||!s||!a)return;if(a.classList.remove("is-fast","is-medium","is-slow","is-error"),"loading"===e)return r.textContent="Đang đo…",void(s.textContent="Đang đo kết nối trang");if("error"===e||!Number.isFinite(t))return a.classList.add("is-error"),r.textContent="-- ms",void(s.textContent="Không đo được");const i=t<=200?"is-fast":t<=600?"is-medium":"is-slow";a.classList.add(i),r.textContent=`${t} ms`,s.textContent="Độ trễ kết nối trang"},measureServer=async()=>{const e=++m;if(u?.abort(),updateServerProbe("loading"),"function"!=typeof fetch||"function"!=typeof AbortController)return void updateServerProbe("error");const t=new AbortController;u=t;const r=setTimeout(()=>t.abort(),4e3),n=performance.now();try{const r=new URL("player-lite.css",location.href);r.search=`?ver=lite-27-startup&stream_ping=${Date.now()}`;if(!(await fetch(r.href,{method:"HEAD",credentials:"omit",cache:"no-store",signal:t.signal})).ok)throw new Error("server_probe_failed");const s=Math.max(1,Math.round(performance.now()-n));e===m&&updateServerProbe("ready",s)}catch(s){e===m&&updateServerProbe("error")}finally{clearTimeout(r),u===t&&(u=null)}},renderAspect=()=>{l="aspect",n.innerHTML=`${header("Tỉ lệ màn hình")}<div class="stream-settings-options" data-settings-options="aspect"></div>`;const e=n.querySelector('[data-settings-options="aspect"]');o.forEach(t=>{const r=document.createElement("button");r.type="button",r.className="stream-settings-option"+(t.value===c.value?" is-active":""),r.dataset.settingsAspect=t.value,r.innerHTML=`<span class="stream-settings-option-label"></span><span class="stream-settings-check">${i.check}</span>`,r.querySelector(".stream-settings-option-label").textContent=t.label,e.appendChild(r)})},closeMenu=()=>{n.hidden=!0,r.setAttribute("aria-expanded","false"),e.classList.remove("stream-settings-open")},onSettingsClick=t=>{t.preventDefault(),t.stopImmediatePropagation(),n.hidden?(renderRoot(),n.hidden=!1,r.setAttribute("aria-expanded","true"),e.classList.add("stream-settings-open"),n.querySelector("button")?.focus({preventScroll:!0})):closeMenu()},onOutsidePointer=e=>{n.hidden||n.contains(e.target)||r.contains(e.target)||closeMenu()},onKeyDown=e=>{"Escape"!==e.key||n.hidden||(e.preventDefault(),closeMenu(),r.focus?.({preventScroll:!0}))},syncSettings=()=>{n.hidden||("root"===l?renderRoot():"quality"===l?renderQuality():"speed"===l&&updateSpeedView())};r.addEventListener("click",onSettingsClick,!0),n.addEventListener("click",e=>{e.stopPropagation();const r=e.target.closest?.("button");if(!r)return;const a=r.dataset.settingsView;if("quality"===a)renderQuality();else if("speed"===a)l="speed",n.innerHTML=`${header("Tốc độ phát")}\n          <div class="stream-speed-panel">\n            <strong class="stream-speed-readout" data-settings-speed-readout>1.00x</strong>\n            <div class="stream-speed-adjust">\n              <button type="button" data-settings-rate-delta="-0.25" aria-label="Giảm tốc độ">−</button>\n              <input type="range" min="0.25" max="2" step="0.25" value="1" data-settings-speed-range aria-label="Tốc độ phát">\n              <button type="button" data-settings-rate-delta="0.25" aria-label="Tăng tốc độ">+</button>\n            </div>\n            <div class="stream-speed-presets">\n              ${[1,1.25,1.5,2].map(e=>`<button type="button" data-settings-rate="${e}">${e.toFixed(1===e||2===e?1:2)}x</button>`).join("")}\n            </div>\n          </div>`,updateSpeedView();else if("server"===a)l="server",n.innerHTML=`${header("Máy chủ",!0)}\n          <div class="stream-server-card">\n            <span class="stream-server-bars" aria-hidden="true"><i></i><i></i><i></i></span>\n            <span class="stream-server-copy"><strong data-settings-server-country></strong><small><span data-settings-server-status>Đang đo kết nối trang</span></small></span>\n            <span class="stream-server-latency" data-settings-server-latency>Đang đo…</span>\n            <span class="stream-settings-check stream-server-check">${i.check}</span>\n          </div>`,n.querySelector("[data-settings-server-country]").textContent=s,measureServer();else if("aspect"===a)renderAspect();else if("back"===r.dataset.settingsAction)renderRoot();else if("refresh-server"===r.dataset.settingsAction)measureServer();else if(void 0!==r.dataset.settingsQuality){const e=Number(r.dataset.settingsQuality);Number.isInteger(e)&&e>=0&&e<Math.max(1,qualityLevels().length)&&(t.setCurrentQuality?.(e),renderQuality())}else if(void 0!==r.dataset.settingsRate)setRate(r.dataset.settingsRate);else if(void 0!==r.dataset.settingsRateDelta)setRate(currentRate()+Number(r.dataset.settingsRateDelta));else if(void 0!==r.dataset.settingsAspect){const e=o.find(e=>e.value===r.dataset.settingsAspect);e&&(setAspect(e),renderAspect())}}),n.addEventListener("input",e=>{e.target.matches?.("[data-settings-speed-range]")&&setRate(e.target.value)}),n.addEventListener("pointerdown",e=>e.stopPropagation()),document.addEventListener("pointerdown",onOutsidePointer,!0),document.addEventListener("keydown",onKeyDown,!0),t.on?.("levels",syncSettings),t.on?.("levelsChanged",syncSettings),t.on?.("playbackRateChanged",syncSettings),renderRoot(),a.settingsCleanup=()=>{setAspect(o[0]),m++,u?.abort(),r.removeEventListener("click",onSettingsClick,!0),document.removeEventListener("pointerdown",onOutsidePointer,!0),document.removeEventListener("keydown",onKeyDown,!0),t.off?.("levels",syncSettings),t.off?.("levelsChanged",syncSettings),t.off?.("playbackRateChanged",syncSettings),e.classList.remove("stream-custom-settings-enabled","stream-settings-open"),n.remove(),r.removeAttribute("aria-controls"),r.setAttribute("aria-expanded","false"),a.settingsCleanup&&(a.settingsCleanup=null)}},setupMobileGestures(e){if(e.querySelector(".stream-mobile-lock-button"))return;a.mobileCleanup?.();const t=a.playerInstance;if(!t)return;const isMobile=()=>window.matchMedia?.("(max-width: 760px), (pointer: coarse)")?.matches||navigator.maxTouchPoints>0,r=document.createElement("button");r.type="button",r.className="stream-mobile-lock-button",r.setAttribute("aria-pressed","false");const n=document.createElement("div");n.className="stream-mobile-lock-shield",n.setAttribute("aria-hidden","true");const s=document.createElement("div");s.className="stream-double-tap-feedback",s.hidden=!0,s.setAttribute("aria-live","polite"),s.innerHTML='<span class="stream-double-tap-icon" aria-hidden="true"></span><span class="stream-double-tap-copy">10 giây</span>',e.appendChild(n),e.appendChild(s),e.appendChild(r);let i=0;const hideLockControl=()=>{clearTimeout(i),i=0,e.classList.remove("stream-mobile-lock-visible")},showLockControl=()=>{e.classList.contains("stream-mobile-locked")&&(e.classList.add("stream-mobile-lock-visible"),clearTimeout(i),i=setTimeout(hideLockControl,1800))},setLocked=t=>{e.classList.toggle("stream-mobile-locked",t),r.setAttribute("aria-pressed",String(t)),r.setAttribute("aria-label",t?"Mở khóa màn hình":"Khóa màn hình"),r.innerHTML=(e=>e?'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>':'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M16 10V7a4 4 0 0 0-7.7-1.5"/></svg>')(t),t?showLockControl():hideLockControl()};setLocked(!1),r.addEventListener("click",t=>{t.preventDefault(),t.stopPropagation(),isMobile()&&setLocked(!e.classList.contains("stream-mobile-locked"))}),n.addEventListener("pointerdown",e=>{e.preventDefault(),e.stopPropagation()}),n.addEventListener("click",e=>{e.preventDefault(),e.stopPropagation()});let o=null,l=null,c=null,d=!1,u=0;const contentTouch=r=>{if(!isMobile()||r.target.closest?.(".jw-controlbar,.jw-settings-menu,.stream-settings-panel,.stream-mobile-lock-button,.stream-playback-recovery,.jw-display-icon-container,.jw-icon,.jw-slider,.jw-skip,button,a,input,select,textarea,[role=button]")||e.classList.contains("jw-flag-ads"))return!1;const n=t.getState?.();return!n||["playing","paused","buffering"].includes(n)},stopGesture=(e,t=!0)=>{t&&e.preventDefault(),e.stopPropagation(),e.stopImmediatePropagation?.()},resetGesture=()=>{o=l=c=null,d=!1},near=(e,t,r)=>Math.hypot(e.x-t.x,e.y-t.y)<=r,point=e=>({x:e.clientX,y:e.clientY}),recentHandled=e=>c&&performance.now()-c.time<=700&&near(e,c,40),onTouch=e=>{e.touches?.length>1?resetGesture():d&&(stopGesture(e,"touchend"===e.type&&!!c),"touchend"===e.type&&(d=!1))},onCompatibilityEvent=e=>{!contentTouch(e)||"click"===e.type&&0===e.detail||!1===e.sourceCapabilities?.firesTouchEvents&&"pen"!==c?.pointerType||"mouse"===e.pointerType||recentHandled(point(e))&&stopGesture(e)},m={pointerdown:t=>{if(!contentTouch(t)||!["touch","pen"].includes(t.pointerType)||!1===t.isPrimary||l)return void resetGesture();e.classList.contains("stream-mobile-locked")&&showLockControl();const r=e.getBoundingClientRect();if(!r.width)return void resetGesture();const n=t.clientX-r.left,s=n<.36*r.width?-1:n>.64*r.width?1:0;if(!s)return void resetGesture();const a=performance.now(),i=point(t),c=!!(o&&o.direction===s&&a-o.time<=330&&near(i,o,40));l={...i,direction:s,time:a,id:t.pointerId,second:c,moved:!1},d=c||!!recentHandled(i),d&&stopGesture(t,!1)},pointermove:e=>{l&&l.id===e.pointerId&&!near(point(e),l,16)&&(l.moved=!0)},pointerup:e=>{const t=l;if(l=null,!t||t.id!==e.pointerId||!1===e.isPrimary||!contentTouch(e)||t.moved||!near(point(e),t,16)||performance.now()-t.time>350)return void(o=null);const r=performance.now();if(!t.second)return void(o={...point(e),direction:t.direction,time:r});o=null,c={...point(e),time:r,pointerType:e.pointerType},stopGesture(e);const n=t.direction;a.relativeSeeking?.request(10*n)&&(e=>{clearTimeout(u),s.classList.remove("is-visible","is-forward","is-backward"),s.classList.add(e>0?"is-forward":"is-backward"),s.querySelector(".stream-double-tap-icon").innerHTML=e>0?"↻":"↺",s.hidden=!1,requestAnimationFrame(()=>s.classList.add("is-visible")),u=setTimeout(()=>{s.classList.remove("is-visible"),s.hidden=!0},520)})(n)},pointercancel:resetGesture,touchcancel:resetGesture,touchstart:onTouch,touchend:onTouch,click:onCompatibilityEvent,dblclick:onCompatibilityEvent,mousedown:onCompatibilityEvent,mouseup:onCompatibilityEvent};for(const[a,p]of Object.entries(m))e.addEventListener(a,p,{passive:!1,capture:!0});document.addEventListener?.("fullscreenchange",resetGesture),window.addEventListener?.("resize",resetGesture);for(const a of["adPlay","fullscreen","resize"])t.on?.(a,resetGesture);a.mobileCleanup=()=>{resetGesture(),hideLockControl(),clearTimeout(u);for(const[t,r]of Object.entries(m))e.removeEventListener(t,r,!0);document.removeEventListener?.("fullscreenchange",resetGesture),window.removeEventListener?.("resize",resetGesture);for(const e of["adPlay","fullscreen","resize"])t.off?.(e,resetGesture);e.classList.remove("stream-mobile-locked","stream-mobile-lock-visible"),n.remove(),s.remove(),r.remove(),a.mobileCleanup&&(a.mobileCleanup=null)}}};const p={_setupInProgress:!1,async setupPlayer(withAds, startPosition = 0, streamURL = null) {
      const state=a, uiManager=m, streamManager=c, utils=i, playerConfig=r, tvcConfig=n, timeTracker=u;
      function bindPlaybackTelemetry(player, generation, hasTvc) {
    const listeners = [];
    let adActive = false;
    const current = () => generation === state.setupGeneration && player === state.playerInstance;
    const on = (name, callback) => {
      player.on(name, callback); listeners.push([name, callback]);
    };
    const emit = (name, data) => {
      if (!current()) return;
      try { window.streamTelemetry?.event?.(name, data); } catch (_) {}
    };
    on('firstFrame', () => {
      try {
        if (adActive || player.getContainer?.()?.classList?.contains('jw-flag-ads')) return;
        emit('content_first_frame'); // Dedupe spans JW rebuilds within this bootstrap.
      } catch (_) {} // Optional observation must not interrupt JW event handlers.
    });
    if (hasTvc) {
      for (const name of ['adRequest', 'adBuffer', 'adPlay', 'adStarted', 'adPause', 'adImpression']) {
        on(name, () => { if (current()) adActive = true; });
      }
      on('adRequest', () => emit('tvc_request'));
      // adStarted is not evidence of actual media playback. JW adImpression
      // represents an ad that has rendered and begun playing.
      on('adImpression', () => emit('tvc_impression'));
      for (const [name, metric] of [['adComplete', 'tvc_complete'], ['adSkipped', 'tvc_skipped'], ['adError', 'tvc_error']]) {
        on(name, e => {
          if (!current()) return;
          adActive = false;
          try { emit(metric, metric === 'tvc_error' ? {code:e?.code} : undefined); } catch (_) {}
        });
      }
      on('adBreakEnd', () => { if (current()) adActive = false; });
    }
    return () => { for (const [name, callback] of listeners) { try { player.off?.(name, callback); } catch (_) {} } };
  }
      function bindManagedWindowPrimeGuard(player, generation) {
    state.managedGestureCleanup?.();
    if (!needsManagedPrimeGuard()) return;
    let capturedEvent = null;
    const cleanup = () => {
      window.removeEventListener('click', onGesture, true);
      window.removeEventListener('keydown', onGesture, true);
      window.removeEventListener('click', onWindowGesture, false);
      window.removeEventListener('keydown', onWindowGesture, false);
      if (state.managedGestureCleanup === cleanup) state.managedGestureCleanup = null;
    };
    const onGesture = event => {
      // Match the setup shim's once('gesture'), including a click elsewhere in
      // this frame or the synthetic click that follows a touch-started playback.
      if (generation !== state.setupGeneration || player !== state.playerInstance) {
        cleanup();
        return;
      }
      capturedEvent = event;
      armManagedPrimeGuard(player, generation, 'window_gesture', event);
    };
    const onWindowGesture = event => {
      // Settings/lock controls can stop propagation. Keep capture coverage until
      // an event actually reaches the shim's window listeners. This observer is
      // registered after JW setup; it never changes event propagation itself.
      if (event === capturedEvent) cleanup();
    };
    window.addEventListener('click', onGesture, true);
    window.addEventListener('keydown', onGesture, true);
    window.addEventListener('click', onWindowGesture, false);
    window.addEventListener('keydown', onWindowGesture, false);
    state.managedGestureCleanup = cleanup;
  }
      const generation = ++state.setupGeneration;
      const streamGeneration = state._streamGeneration;
      const checkpoint=Number.isFinite(startPosition) && startPosition>=0 ? startPosition : 0;
      const fail=message=>{
        if(generation!==state.setupGeneration) return;
        this._setupInProgress=false;
        let live;try{live=state.savePositionCheckpoint?.();}catch(_){}
        if(!window.streamAccess?.onPlaybackError?.()) uiManager.showErrorMessage(message);
      };
      const diagnostics = startupDiagnostics(generation);
      let adBreak = null;
      let managedHls = false;
      this._setupInProgress = true;

      try {
        const streamReady = streamURL || streamManager.getStreamURL();
        const jwReady = window.streamJwReady || Promise.resolve();
        const guardReady = streamManager.waitForAccess(streamGeneration);
        diagnostics?.observe('wait_stream', streamReady);
        diagnostics?.observe('wait_jw', jwReady);
        diagnostics?.observe('wait_guard', guardReady);
        const dependencies = Promise.all([streamReady, jwReady, guardReady]);
        const preparation = state._streamPreparation;
        [streamURL] = await (preparation?.generation === streamGeneration
          ? Promise.race([dependencies, preparation.failure]) : dependencies);
        diagnostics?.record('wait_all');

        // Also gate supplied/cached URLs, and recheck after a slow JW download.
        const recheckStarted = diagnostics?.now();
        await streamManager.waitForAccess(streamGeneration);
        diagnostics?.record('recheck_guard', recheckStarted);

        if (generation !== state.setupGeneration) return;

        if (!streamURL) {
          this._setupInProgress = false;
          fail('Chưa lấy được nguồn video. Vui lòng tải lại trang.');
          return;
        }

        this.cleanup();
        state.completed = false;
        if (typeof window.jwplayer !== 'function') throw new Error('player_library_unavailable');
        if (playerConfig.playerToken && typeof window.jwplayer === "function") {
          window.jwplayer.key = playerConfig.playerToken;
        }

        const nativeHls = utils.usesNativeHls();
        const sealedHls = window.streamAccess.shouldUseSealedLoader?.() === true;
        managedHls = sealedHls && window.streamAccess.appleJsHls === true &&
          typeof window.ManagedMediaSource === 'function';
        if (sealedHls) enableManagedHlsProvider();
        state.playerInstance = jwplayer("player");

        if (withAds && tvcConfig && !(startPosition > 0 && tvcConfig.offset_seconds <= startPosition)) {
          const offset = tvcConfig.offset_seconds === 0 ? 'pre' : tvcConfig.offset_seconds;
          if (tvcConfig.mode === 'direct') adBreak = {offset, vastxml: tvcConfig.vastxml};
          else {
            const stored = Number(timeTracker.getItem("adIndex"));
            const adIndex = Number.isSafeInteger(stored) && stored >= 0 ? stored % tvcConfig.tags.length : 0;
            timeTracker.setItem("adIndex", (adIndex + 1) % tvcConfig.tags.length);
            adBreak = {offset, tag: utils.addRandomParam(tvcConfig.tags[adIndex])};
          }
        }

        // Let JW preload automatically instead of limiting idle HLS preload
        // to one segment. This does not enable autoplay or delay Play for a
        // complete preload; JW and the browser control the actual buffer.
        const preload = 'auto';
        const setupStarted = diagnostics?.now();
        state.playerInstance.setup({
          file: streamURL,
          type: "hls",
          width: "100%",
          height: "100%",
          primary: "html5",
          autostart: false,
          mute: false,
          playbackRateControls: true,
          displaytitle: false,
          displaydescription: false,
          skin: { name: "streamlite" },
          // Hls.js disables remote playback while ManagedMediaSource is in use.
          cast: { airplay: !(sealedHls && !!window.ManagedMediaSource) },
          preload,
          advertising: adBreak ? {
            client: "vast",
            // Direct n has no advertiser trackers. Do not emit impression or
            // progress pixels; external VAST keeps its provider's tracking.
            ...(tvcConfig.mode === 'direct' ? {trackingFilter: () => false} : {}),
            skipoffset: tvcConfig.skip_seconds,
            skiptext: "Bỏ qua quảng cáo",
            skipmessage: "Có thể bỏ qua sau xx giây.",
            admessage: "Quảng cáo còn xx giây.",
            schedule: [adBreak],
            requestTimeout: tvcConfig.request_timeout_ms,
          } : undefined,
          startparam: "start",
          startposition: startPosition,
          hlsjsdefault: !nativeHls,
          safarihlsjs: sealedHls && window.streamAccess.appleJsHls === true,
          hlsjsConfig: sealedHls ? {pLoader: SealedPlaylistLoader} : undefined,
        });
        diagnostics?.record('setup_sync', setupStarted);
        // JW setup clears existing API listeners. Register diagnostics after
        // it returns, before its asynchronous readiness/ad events are emitted.
        window.streamSandbox?.player?.(state.playerInstance);
        window.streamSandbox?.pipeline?.({stage:'player_setup', build:'lite-45-jw8513-messages-r25',
          preload,
          safarihlsjs:sealedHls && window.streamAccess.appleJsHls === true});
      } catch (e) {
        if (generation !== state.setupGeneration) return;
        this._setupInProgress = false;
        console.error("setupPlayer error:", e);
        try { window.streamSandbox?.error?.('player', e?.message); } catch (_) {}
        fail('Chưa thể khởi động video. Vui lòng tải lại trang.');
        return;
      }

      clearTimeout(state.timers.setupWatchdog);
      const armSetupWatchdog = () => {
        if (generation !== state.setupGeneration || streamGeneration !== state._streamGeneration || !this._setupInProgress) return;
        state.timers.setupWatchdog = setTimeout(() => {
          if (generation === state.setupGeneration && this._setupInProgress) {
            this._setupInProgress = false;
            fail('Video đang tải lâu hơn dự kiến. Bạn có thể tải lại trang.');
          }
        }, 10000);
      };
      const pendingEntry = state._streamPreparation;
      if (pendingEntry?.generation === streamGeneration) {
        // Keep the old setup budget after entry preparation, rather than
        // cutting a legitimate 15s playlist request off with a new 10s timer.
        pendingEntry.promise.then(armSetupWatchdog, () => {
          if (generation !== state.setupGeneration || streamGeneration !== state._streamGeneration) return;
          // Initial preparation errors have always been terminal. If JW has
          // already initialized, stop it and discard the failed handoff now.
          fail('Chưa thể khởi động video. Vui lòng tải lại trang.');
        });
      } else armSetupWatchdog();

      const clearSetupState = () => {
        clearTimeout(state.timers.setupWatchdog);
        this._setupInProgress = false;
      };

      const player = state.playerInstance;
      try { state.playbackTelemetryCleanup = bindPlaybackTelemetry(player, generation, !!adBreak); } catch (_) {}
      state.relativeSeeking = bindRelativeSeeking(player, generation);
      state.loadProgressCleanup = bindLoadProgress(player, adBreak?.vastxml);
      state.playbackRecoveryCleanup = bindPlaybackRecovery(player, generation, managedHls ? (allowResume, failure) => {
        clearSetupState();
        if (!window.streamAccess.onPlaybackError()) {
          uiManager.showErrorMessage('Không thể nạp dữ liệu video trên thiết bị này. Vui lòng tải lại trang để thử lại.', allowResume, failure);
        }
      } : null);
      window.streamGuard?.registerPlayer?.(player);
      if (managedHls) bindManagedWindowPrimeGuard(player, generation);

      player.on('beforePlay', () => {
        if (!managedHls || generation !== state.setupGeneration ||
            player !== state.playerInstance) return;
        // Match JW's actual pool-prime gesture predicate, not playReason:
        // player.play() inside a real click is labelled "external" by JW.
        if (!/^(?:mouse|pointer|touch|gesture|click|key)/.test(window.event?.type || '')) return;
        armManagedPrimeGuard(player, generation);
      });

      player.on("play", () => {
        if (generation !== state.setupGeneration) return;
        state.completed = false;
        if (window.streamGuard?.isBlocked?.()) return;
        if (typeof window.streamPlaybackStartedAt !== 'number') window.streamPlaybackStartedAt = performance.now();
        window.dispatchEvent(new CustomEvent('stream:play'));
      });

      player.on("ready", () => {
        if (generation !== state.setupGeneration) return;
        requestAnimationFrame(() => {
          if (generation !== state.setupGeneration) return;
          this.setupPlayerUI();
        });
        if (startPosition > 0) player.seek(startPosition);
        clearSetupState();
      });

      player.on("setupError", () => {
        if (generation !== state.setupGeneration) return;
        clearSetupState();
        fail('Chưa thể khởi động video. Vui lòng tải lại trang.');
      });

      player.on("error", () => {
        if (generation !== state.setupGeneration) return;
        clearSetupState();
        if(!window.streamAccess?.onPlaybackError?.()) uiManager.showErrorMessage('Đã xảy ra lỗi khi phát video. Vui lòng tải lại trang.');
      });

      this.setupTimeTracking(checkpoint);
    },setupPlayerUI(){const e=a.playerInstance?.getContainer();e&&(m.setupSeekButtons(e),m.setupSettingsMenu(e),m.setupMobileGestures(e))},setupTimeTracking(startPosition=0) {
      const state=a, utils=i, timeTracker=u;
      const currentHash = utils.getCurrentVideoHash();
      if (!currentHash) return;

      state.resumeTime = 0;
      const player = state.playerInstance;
      const generation = state.setupGeneration;
      let lastSave = performance.now();
      let lastContentPosition = Number.isFinite(startPosition) && startPosition>=0 ? startPosition : 0, adActive = false;
      const remember=position=>{if(Number.isFinite(position) && position>=0) state._watchCheckpoint={hash:currentHash,reset:state.resetGeneration,position};};
      remember(lastContentPosition);
      const inAd = () => adActive || player.getContainer?.()?.classList?.contains('jw-flag-ads');

      const handleSave = () => {
        if (state.completed || generation !== state.setupGeneration || player !== state.playerInstance) return;
        let pos = lastContentPosition;
        // JW may already have reset or detached its provider on an error.
        // Never replace a content checkpoint with the current ad's position.
        if (!inAd() && !player.getContainer?.()?.querySelector?.('video')?.error) {
          try {
            const currentPosition = player?.getPosition?.();
            if (Number.isFinite(currentPosition) && currentPosition > 0) pos = currentPosition;
          } catch (_) { /* Keep the last observed content position. */ }
        }
        // Pause can expose a newer position than the last JW time event.
        // Retain it before a detached provider starts reporting zero.
        if (Number.isFinite(pos) && pos >= 0) {lastContentPosition = pos;remember(pos);}
        if (pos > 0) {
          timeTracker.saveWatchTime(currentHash, pos);
          lastSave = performance.now();
        }
        return pos;
      };
      state.savePositionCheckpoint = handleSave;

      const handleTimeSave = (e) => {
        if (state.completed || generation !== state.setupGeneration || inAd()) return;
        // A failed Safari decoder can keep advancing the clock with zero new
        // frames. Keep the last healthy/pause/explicit-seek checkpoint instead.
        if (player.getContainer?.()?.querySelector?.('video')?.error) return;
        const pos = Number(e?.position);
        if (!Number.isFinite(pos) || pos < 0) return;
        // A detached MMS provider can emit time:0 after content has played.
        // Keep the content checkpoint; an explicit seek to zero below still
        // updates lastContentPosition and is never turned into a resume jump.
        if (pos === 0 && lastContentPosition > 0 &&
            player.getContainer?.()?.querySelector?.('video')?.readyState === 0) return;
        lastContentPosition = pos;remember(pos);
        if (performance.now() - lastSave >= 30000) {
          lastSave = performance.now();
          timeTracker.saveWatchTime(currentHash, pos);
        }
      };

      player.on("pause", handleSave);
      for (const name of ['adRequest', 'adBuffer', 'adPlay', 'adStarted', 'adPause']) {
        player.on(name, () => { if (generation === state.setupGeneration) adActive = true; });
      }
      for (const name of ['adComplete', 'adSkipped', 'adError']) {
        player.on(name, () => { if (generation === state.setupGeneration) adActive = false; });
      }
      player.on("seek", e => {
        if (generation !== state.setupGeneration || inAd()) return;
        state.completed = false;
        if (Number.isFinite(e?.offset)) {
          lastContentPosition = e.offset;remember(e.offset);
          if (e.offset >= 0 && e.offset < 1) timeTracker.clearWatchTime(currentHash);
          else timeTracker.saveWatchTime(currentHash, e.offset);
          lastSave = performance.now();
        } else handleSave();
      });
      player.on("time", handleTimeSave);
      player.on("complete", () => {
        if (generation !== state.setupGeneration) return;
        state.completed = true;
        state._watchCheckpoint=null;
        timeTracker.clearWatchTime(currentHash);
      });
    },cleanup(){if(clearTimeout(a.timers.setupWatchdog),a.relativeSeeking?.cleanup(),a.relativeSeeking=null,a.playbackRecoveryCleanup?.(),a.playbackRecoveryCleanup=null,a.playbackTelemetryCleanup?.(),a.playbackTelemetryCleanup=null,a.savePositionCheckpoint=null,a.loadProgressCleanup?.(),a.loadProgressCleanup=null,a.settingsCleanup?.(),a.mobileCleanup?.(),a.managedGestureCleanup?.(),a.managedGestureCleanup=null,a.managedPrimeCleanup?.(),a.managedPrimeCleanup=null,window.streamGuard?.registerPlayer?.(null),a.playerInstance){try{a.playerInstance.stop()}catch(e){}try{a.playerInstance.remove()}catch(e){}a.playerInstance=null}}},h={_resumeInProgress:!1,async tryResume(){if(this._resumeInProgress||a.isInitialized)return;this._resumeInProgress=!0,a.isInitialized=!0;const e=a.resetGeneration;try{const t=i.getCurrentVideoHash(),r=t&&u.getSavedWatchTime(t)>60&&!u.shouldSkipResume(t)&&!a.skipResumeForThisSession,s=n&&!a.skipAdsForThisSession,o=await(r||s?c.getStreamURL():c.getAuthorizedStreamURL());if(e!==a.resetGeneration)return void(this._resumeInProgress=!1);if(!o)return a.isInitialized=!1,this._resumeInProgress=!1,void m.showErrorMessage("Chưa lấy được nguồn video. Vui lòng tải lại trang.");t?(a.currentVideoHash=t,await this.processResume(t,o,e)):(await p.setupPlayer(!a.skipAdsForThisSession,0,o),this._resumeInProgress=!1)}catch(t){if(e!==a.resetGeneration)return;console.error("tryResume error:",t),a.isInitialized=!1,this._resumeInProgress=!1,m.showErrorMessage("Chưa thể khởi động video. Vui lòng tải lại trang.")}},async processResume(e,t,r){const n=u.getSavedWatchTime(e),s=u.shouldSkipResume(e)||a.skipResumeForThisSession;if(a.resumeTime=n,n>60&&!s){if(r!==a.resetGeneration||!a.isInitialized)return;m.showResumePopup(n),this._resumeInProgress=!1}else await p.setupPlayer(!a.skipAdsForThisSession,0,t),this._resumeInProgress=!1},reset(){this._resumeInProgress=!1,a.isInitialized=!1,a.currentVideoHash=null,c.resetCache()}},g={start(){window.playerInitialized||(window.playerInitialized=!0,"loading"===document.readyState?document.addEventListener("DOMContentLoaded",()=>this.initializeAfterDOM(),{once:!0}):this.initializeAfterDOM())},saveCurrentPosition() {
  const state=a, utils=i, timeTracker=u;
  if (state.completed) return;
  try {
    const value=state.savePositionCheckpoint?.();
    if (Number.isFinite(value) && value>=0) return value;
  } catch (_) {}
  const checkpoint=state._watchCheckpoint;
  if (checkpoint?.hash===utils.getCurrentVideoHash() && checkpoint.reset===state.resetGeneration &&
      Number.isFinite(checkpoint.position) && checkpoint.position>=0) {
    if(checkpoint.position>0) timeTracker.saveWatchTime(checkpoint.hash,checkpoint.position);
    return checkpoint.position;
  }
},initializeAfterDOM(){this.exposeGlobalFunctions(),h.tryResume(),a.eventsBound||(a.eventsBound=!0,window.addEventListener("stream:before-reload",()=>this.saveCurrentPosition()),window.addEventListener("pagehide",(e={})=>{this.saveCurrentPosition(),e.persisted||(a.setupGeneration++,a.resetGeneration++,p.cleanup(),Object.values(a.timers).forEach(clearTimeout),a.timers={},c.resetCache())}),document.addEventListener("visibilitychange",()=>{document.hidden&&this.saveCurrentPosition()}),window.addEventListener("stream-token-expired",()=>{this.saveCurrentPosition(),a.playerInstance?.pause?.(),c.resetCache()}))},exposeGlobalFunctions(){window.playerSetup=p.setupPlayer.bind(p),window.playerTryResume=h.tryResume.bind(h),window.getStreamURL=c.getStreamURL.bind(c),window.getCurrentVideoHash=i.getCurrentVideoHash.bind(i),window.resetPlayer=()=>{if(a.setupGeneration++,a.resetGeneration++,h.reset(),p.cleanup(),p._setupInProgress=!1,Object.values(a.timers).forEach(clearTimeout),a.timers={},a.isInitialized=!1,a.currentVideoHash=null,a.skipAdsForThisSession=!1,a.skipResumeForThisSession=!1,a.resumeTime=0,a.completed=!1,window.playerInitialized=!1,m._resumeComponent){const{overlay:e,resumeBtn:t,restartBtn:r}=m._resumeComponent;t.onclick=null,r.onclick=null,e.remove(),m._resumeComponent=null}g.start()},window.timeTracker={save:(e,t)=>u.saveWatchTime(e,t),get:e=>u.getSavedWatchTime(e),clear:e=>u.clearWatchTime(e),setSkip:e=>u.setSkipResume(e),shouldSkip:e=>u.shouldSkipResume(e),getConfig:()=>r,getState:()=>({currentHash:a.currentVideoHash})}}};g.start()}();

;
/* Stream player ticker 03. Build: replace __STREAM_TICKER_CSS__ with a JSON string
 * containing ticker.css, then append this IIFE to the existing player asset.
 * The bootstrap must contain playerTicker: { enabled, text, speed, startSeconds, endSeconds }.
 * HTML overlays follow JW's HTML fullscreen, but cannot appear in the iOS
 * system video fullscreen view. This component never changes playback.
 */
(function () {
  "use strict";

  var marker = "__streamPlayerTicker03";
  if (window[marker]) return;

  var config;
  try {
    var seed = document.getElementById("stream-bootstrap");
    config = seed && JSON.parse(seed.textContent).playerTicker;
  } catch (_) {
    return;
  }
  if (!config || config.enabled !== true || typeof config.text !== "string") return;
  var text = Array.from(config.text).slice(0, 1000).join("").replace(/\s+/gu, " ").trim();
  if (!text) return;
  var speed = Number.isInteger(config.speed) ? Math.max(20, Math.min(120, config.speed)) : 50;
  var startSeconds = Number.isInteger(config.startSeconds) && config.startSeconds >= 0 && config.startSeconds <= 86400 ? config.startSeconds : 0;
  var endSeconds = null;
  if (config.endSeconds !== undefined && config.endSeconds !== null) {
    if (!Number.isInteger(config.endSeconds) || config.endSeconds <= startSeconds || config.endSeconds > 86400) return;
    endSeconds = config.endSeconds;
  }
  var timelineRequired = startSeconds > 0 || endSeconds !== null;
  var css = "/* Ticker stays below verification/guard and settings panels. It never takes\n   pointer input, including in HTML fullscreen. iOS system fullscreen is native. */\n.jwplayer > .stream-player-ticker {\n  --stream-ticker-height: 32px;\n  position: absolute;\n  top: 0;\n  left: 0;\n  right: 0;\n  z-index: 3;\n  height: calc(var(--stream-ticker-height) + env(safe-area-inset-top, 0px));\n  padding-top: env(safe-area-inset-top, 0px);\n  box-sizing: border-box;\n  overflow: hidden;\n  background: rgba(8, 11, 16, .76);\n  color: #fff;\n  font: 500 14px/var(--stream-ticker-height) system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;\n  text-align: left;\n  direction: ltr;\n  pointer-events: none !important;\n  user-select: none;\n  -webkit-user-select: none;\n  contain: paint;\n  visibility: hidden;\n}\n.jwplayer > .stream-player-ticker[data-ready=\"true\"][data-started=\"true\"] { visibility: visible; }\n.jwplayer.jw-flag-ads > .stream-player-ticker,\n.jwplayer.jw-state-error > .stream-player-ticker,\n.jwplayer.jw-flag-error > .stream-player-ticker,\n.jwplayer.stream-guard-test > .stream-player-ticker { display: none !important; }\n.stream-player-ticker * { pointer-events: none !important; box-sizing: border-box; }\n.stream-ticker-track {\n  display: flex;\n  align-items: center;\n  width: max-content;\n  white-space: nowrap;\n  animation: stream-ticker-scroll var(--stream-ticker-duration, 10s) linear infinite;\n  will-change: transform;\n}\n.stream-ticker-copy {\n  display: inline-flex;\n  align-items: center;\n  flex: 0 0 auto;\n  gap: 28px;\n  padding-right: 28px;\n  white-space: pre;\n}\n.stream-ticker-separator { color: #ef3340; font-size: 18px; }\n.stream-ticker-text { color: inherit; }\n.stream-player-ticker[data-paused=\"true\"] .stream-ticker-track { animation-play-state: paused; }\n.stream-player-ticker[data-started=\"false\"] .stream-ticker-track { animation-play-state: paused; }\n.stream-ticker-sr {\n  position: absolute;\n  width: 1px;\n  height: 1px;\n  padding: 0;\n  margin: -1px;\n  overflow: hidden;\n  clip: rect(0, 0, 0, 0);\n  white-space: nowrap;\n  border: 0;\n}\n@keyframes stream-ticker-scroll {\n  from { transform: translate3d(0, 0, 0); }\n  to { transform: translate3d(var(--stream-ticker-distance), 0, 0); }\n}\n@media (max-width: 600px) {\n  .jwplayer > .stream-player-ticker { --stream-ticker-height: 27px; font-size: 12px; }\n  .stream-ticker-copy { gap: 20px; padding-right: 20px; }\n}\n@media (prefers-reduced-motion: reduce) {\n  .stream-ticker-track {\n    display: block;\n    width: 100%;\n    animation: none;\n    transform: none;\n    will-change: auto;\n  }\n  .stream-ticker-copy { display: none; }\n  .stream-ticker-copy:first-child { display: flex; gap: 0; padding: 0 12px; }\n  .stream-ticker-copy:first-child .stream-ticker-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }\n  .stream-ticker-separator { display: none; }\n}\n";

  var active = false;
  var generation = 0;
  var frame = 0;
  var root = null;
  var overlay = null;
  var track = null;
  var style = null;
  var discovery = null;
  var rootObserver = null;
  var resizeObserver = null;
  var lastWidth = -1;
  var lastStride = -1;
  var api = null;
  var apiEvents = [];
  var contentPosition = null;
  var adActive = false;
  var adClass = false;
  var awaitingContent = false;

  function updateTimeline() {
    if (!overlay) return;
    var inWindow = !timelineRequired || (!adActive && !adClass && !awaitingContent &&
      contentPosition !== null && contentPosition >= startSeconds && (endSeconds === null || contentPosition < endSeconds));
    var started = inWindow ? "true" : "false";
    if (overlay.getAttribute("data-started") !== started) overlay.setAttribute("data-started", started);
  }

  function unbindTimeline() {
    if (api && typeof api.off === "function") {
      apiEvents.forEach(function (entry) { try { api.off(entry[0], entry[1]); } catch (_) {} });
    }
    api = null;
    apiEvents = [];
    contentPosition = null;
    adActive = false;
    adClass = false;
    awaitingContent = false;
  }

  function adStarted() {
    adActive = true;
    awaitingContent = true;
    updateTimeline();
  }

  function adEnded() {
    adActive = false;
    // JW reuses its <video> for TVC. Its native currentTime/getPosition can
    // still contain the ad position at adBreakEnd; wait for a content event.
    awaitingContent = true;
    updateTimeline();
  }

  function contentTime(event) {
    if (!active || !api || adActive || adClass || root.classList.contains("jw-flag-ads")) return;
    var position = event && event.position;
    if (!Number.isFinite(position) || position < 0) return;
    contentPosition = position;
    awaitingContent = false;
    updateTimeline();
  }

  function contentSeek(event) {
    // `offset` is the requested position in the content timeline, including
    // a seek while paused. It is unrelated to the ad's playback clock.
    contentTime({ position: event && event.offset });
  }

  function readContentPosition() {
    if (!api || awaitingContent || adActive || adClass || !isPlayer() || root.classList.contains("jw-flag-ads")) return;
    try { contentTime({ position: api.getPosition() }); } catch (_) {}
  }

  function readInitialPosition() {
    // A runtime attached to an already playing native source can synchronize
    // immediately if its URL matches JW's content item. For blob/HLS.js sources
    // or unknown source identity the next content time event is authoritative.
    if (!api || root.classList.contains("jw-flag-ads")) return;
    try {
      var video = root.querySelector("video.jw-video, video");
      var item = api.getPlaylistItem();
      var source = video && (video.currentSrc || video.getAttribute("src"));
      var files = [item && item.file].concat(item && Array.isArray(item.sources) ? item.sources.map(function (entry) { return entry.file; }) : []);
      if (!video || video.readyState < 2 || !source) return;
      if (files.some(function (file) { return typeof file === "string" && new URL(file, document.baseURI).href === source; })) readContentPosition();
    } catch (_) {}
  }

  function bindTimeline() {
    if (!timelineRequired) return;
    if (!isPlayer()) { unbindTimeline(); return; }
    var next = null;
    try {
      if (typeof window.jwplayer === "function") {
        var candidate = window.jwplayer(root.id);
        if (candidate && typeof candidate.on === "function" && typeof candidate.off === "function" &&
            typeof candidate.getContainer === "function" && candidate.getContainer() === root) next = candidate;
      }
    } catch (_) {}
    if (next !== api) {
      unbindTimeline();
      api = next;
      if (api) {
        function on(name, handler) {
          api.on(name, handler);
          apiEvents.push([name, handler]);
        }
        on("time", contentTime);
        on("seek", contentSeek);
        on("seeked", readContentPosition);
        on("ready", readInitialPosition);
        ["adRequest", "adBuffer", "adPlay", "adStarted", "adPause"].forEach(function (name) { on(name, adStarted); });
        ["adComplete", "adSkipped", "adError", "adBreakEnd"].forEach(function (name) { on(name, adEnded); });
        on("playlistItem", function () { contentPosition = null; awaitingContent = true; updateTimeline(); });
        readInitialPosition();
      }
    }
    var nextAdClass = root.classList.contains("jw-flag-ads");
    if (nextAdClass !== adClass) {
      adClass = nextAdClass;
      if (adClass) adStarted();
      else adEnded();
    }
    updateTimeline();
  }

  function isPlayer() {
    return root && root.isConnected && root.classList.contains("jwplayer") &&
      !root.classList.contains("stream-guard-test");
  }

  function copy() {
    var item = document.createElement("span");
    item.className = "stream-ticker-copy";
    item.setAttribute("aria-hidden", "true");
    var words = document.createElement("span");
    words.className = "stream-ticker-text";
    words.textContent = text;
    var separator = document.createElement("span");
    separator.className = "stream-ticker-separator";
    separator.textContent = "\u2022";
    item.appendChild(words);
    item.appendChild(separator);
    return item;
  }

  function detach() {
    if (resizeObserver) resizeObserver.disconnect();
    resizeObserver = null;
    if (overlay) overlay.remove();
    overlay = null;
    track = null;
    lastWidth = -1;
    lastStride = -1;
  }

  function visibility() {
    if (overlay) overlay.setAttribute("data-paused", document.hidden ? "true" : "false");
  }

  function measure() {
    frame = 0;
    if (!active) return;
    discover();
    if (!overlay || !track || !isPlayer()) return;
    var width = overlay.clientWidth;
    var first = track.firstElementChild;
    var stride = first ? first.getBoundingClientRect().width : 0;
    if (!(width > 0 && stride > 0)) return;
    if (width === lastWidth && stride === lastStride) return;
    lastWidth = width;
    lastStride = stride;
    var count = Math.max(2, Math.ceil(width / stride) + 1);
    while (track.children.length > count) track.lastElementChild.remove();
    while (track.children.length < count) track.appendChild(copy());
    track.style.setProperty("--stream-ticker-distance", (-stride) + "px");
    track.style.setProperty("--stream-ticker-duration", (stride / speed) + "s");
    overlay.setAttribute("data-ready", "true");
  }

  function schedule() {
    if (active && !frame) frame = window.requestAnimationFrame(measure);
  }

  function mount() {
    if (!isPlayer()) {
      detach();
      return;
    }
    if (overlay && overlay.parentNode === root) return;
    detach();
    // A repeated setup or a recovered player must never leave two bands.
    root.querySelectorAll(":scope > .stream-player-ticker").forEach(function (node) { node.remove(); });
    overlay = document.createElement("div");
    overlay.className = "stream-player-ticker";
    // Set before insertion so a resumed or rebuilt player cannot flash a band
    // before its first trusted content timeline event.
    overlay.setAttribute("data-started", timelineRequired ? "false" : "true");
    var accessible = document.createElement("span");
    accessible.className = "stream-ticker-sr";
    accessible.textContent = text;
    track = document.createElement("div");
    track.className = "stream-ticker-track";
    track.setAttribute("aria-hidden", "true");
    track.appendChild(copy());
    overlay.appendChild(accessible);
    overlay.appendChild(track);
    root.appendChild(overlay);
    updateTimeline();
    visibility();
    if (typeof window.ResizeObserver === "function") {
      resizeObserver = new ResizeObserver(schedule);
      resizeObserver.observe(root);
    }
    schedule();
  }

  function discover() {
    var next = document.getElementById("player");
    if (next !== root) {
      if (rootObserver) rootObserver.disconnect();
      unbindTimeline();
      detach();
      root = next;
      if (root) {
        rootObserver = new MutationObserver(function () {
          if (!active) return;
          bindTimeline();
          mount();
          schedule();
        });
        rootObserver.observe(root, { attributes: true, attributeFilter: ["class"] });
      }
    }
    bindTimeline();
    mount();
  }

  function changed(records) {
    if (!active) return;
    // Internal copy/measurement updates are deliberately ignored. The parent
    // mutation caused by JW removing the entire band still triggers remount.
    var external = records.some(function (record) {
      if (overlay && (record.target === overlay || overlay.contains(record.target))) return false;
      if (record.target === root && !record.removedNodes.length &&
          Array.from(record.addedNodes).every(function (node) { return node === overlay; })) return false;
      return true;
    });
    if (external) discover();
  }

  function start() {
    if (active) return;
    active = true;
    var cycle = ++generation;
    style = document.createElement("style");
    style.className = "stream-ticker-style";
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);
    discovery = new MutationObserver(changed);
    discovery.observe(document.documentElement, { childList: true, subtree: true });
    document.addEventListener("visibilitychange", visibility);
    window.addEventListener("resize", schedule);
    window.addEventListener("pagehide", pagehide);
    if (document.fonts) {
      if (document.fonts.addEventListener) document.fonts.addEventListener("loadingdone", schedule);
      document.fonts.ready.then(function () { if (active && generation === cycle) schedule(); });
    }
    discover();
  }

  function stop() {
    active = false;
    ++generation;
    if (frame) window.cancelAnimationFrame(frame);
    frame = 0;
    if (discovery) discovery.disconnect();
    if (rootObserver) rootObserver.disconnect();
    discovery = null;
    rootObserver = null;
    unbindTimeline();
    detach();
    root = null;
    if (style) style.remove();
    style = null;
    document.removeEventListener("visibilitychange", visibility);
    window.removeEventListener("resize", schedule);
    window.removeEventListener("pagehide", pagehide);
    if (document.fonts && document.fonts.removeEventListener) document.fonts.removeEventListener("loadingdone", schedule);
  }

  function pagehide(event) {
    stop();
    // The single pageshow hook is retained only while a page is in BFCache.
    if (!event.persisted) window.removeEventListener("pageshow", pageshow);
  }

  function pageshow(event) {
    if (event.persisted) start();
  }

  window[marker] = {
    version: "stream-ticker-03",
    destroy: function () {
      stop();
      window.removeEventListener("pageshow", pageshow);
      delete window[marker];
    }
  };
  window.addEventListener("pageshow", pageshow);
  start();
}());

