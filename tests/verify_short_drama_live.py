import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
import uuid

sys.stdout.reconfigure(encoding='utf-8')

API_BASE = 'https://apiv2.free-reels.com/frv2-api'
APP_SECRET = '8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv'
TAB_META = {
    '503': {'moduleKey': '1036', 'pos': 10000, 'simpleNext': True},
    '505': {'moduleKey': '1040', 'pos': 10001, 'simpleNext': False},
    '504': {'moduleKey': '1039', 'pos': 10003, 'simpleNext': False},
    '506': {'moduleKey': '1041', 'pos': 10004, 'simpleNext': False},
    '547': {'moduleKey': '2204', 'pos': 10005, 'simpleNext': True}
}


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


class FreeReelsSim:
    def __init__(self, seed=0):
        self.seed = seed
        self.device_id = str(uuid.uuid4())
        self.session_id = str(uuid.uuid4())
        self.oauth_token = ''
        self.oauth_secret = ''
        self.login()

    def login(self):
        sign = md5(APP_SECRET + self.device_id)
        req = urllib.request.Request(
            f"{API_BASE}/anonymous/login",
            data=json.dumps({'device_id': self.device_id, 'device_name': 'samsung SM-A536E', 'sign': sign}).encode('utf-8'),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'app-name': 'com.freereels.app',
                'app-version': '2.2.81',
                'device': 'android',
                'device-version': '33',
                'device-id': self.device_id,
                'session-id': self.session_id,
                'language': 'vi-VN',
                'country': 'VN'
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8')).get('data', {})
            self.oauth_token = data.get('auth_key', '')
            self.oauth_secret = data.get('auth_secret', '')

    def headers(self):
        ts = str(int(time.time() * 1000))
        sig = md5(f"{APP_SECRET}&{self.oauth_secret}")
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'app-name': 'com.freereels.app',
            'app-version': '2.2.81',
            'device': 'android',
            'device-version': '33',
            'device-id': self.device_id,
            'session-id': self.session_id,
            'language': 'vi-VN',
            'country': 'VN',
            'Authorization': f"oauth_signature={sig},oauth_token={self.oauth_token},ts={ts}"
        }

    def fetch_tab_feed(self, tab_key, offset=0):
        if tab_key == 'foryou':
            next_param = f"offset={offset}" if offset > 0 else ""
            url = f"{API_BASE}/foryou/feed?next={urllib.parse.quote(next_param)}"
            req = urllib.request.Request(url, headers=self.headers(), method='GET')
        else:
            meta = TAB_META.get(tab_key, TAB_META['503'])
            next_str = (
                f"offset={offset}&position_index={meta['pos']}"
                if meta['simpleNext']
                else f"last_quality=0&offset={offset}&position_index={meta['pos']}&timestamp="
            )
            body = json.dumps({'tab_key': tab_key, 'module_key': meta['moduleKey'], 'next': next_str}).encode('utf-8')
            req = urllib.request.Request(f"{API_BASE}/homepage/v2/tab/feed", data=body, headers=self.headers(), method='POST')

        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read().decode('utf-8')).get('data', {})
            items = d.get('items') or d.get('list') or []
            out = []
            for it in items:
                s = it.get('series') or it.get('info') or it
                sid = s.get('id') or s.get('key') or s.get('series_id')
                title = s.get('title') or s.get('name') or ''
                if sid and title and not title.upper().startswith('TOP'):
                    out.append((sid, title))
            return out

    def get_foryou(self, page=1):
        rot = (self.seed % 4) * 10
        base = (page - 1) * 20
        a = self.fetch_tab_feed('505', base + rot)
        b = self.fetch_tab_feed('foryou', base + rot)
        c = self.fetch_tab_feed('503', base + ((rot + 10) % 40))
        seen = set()
        res = []
        for sid, title in a + b + c:
            if sid not in seen:
                seen.add(sid)
                res.append((sid, title))
        return res


def main():
    print("=== LIVE VERIFICATION OF DYNAMIC SHORT DRAMA ROTATION ===")
    sim0 = FreeReelsSim(seed=0)
    sim1 = FreeReelsSim(seed=1)

    list0 = sim0.get_foryou(page=1)
    list1 = sim1.get_foryou(page=1)

    print(f"Slot 0 (seed=0) count: {len(list0)} | Top 4: {[t for _, t in list0[:4]]}")
    print(f"Slot 1 (seed=1) count: {len(list1)} | Top 4: {[t for _, t in list1[:4]]}")

    assert len(list0) >= 15, f"Expected >= 15 dramas in Slot 0, got {len(list0)}"
    assert len(list1) >= 15, f"Expected >= 15 dramas in Slot 1, got {len(list1)}"
    ids0 = [sid for sid, _ in list0[:10]]
    ids1 = [sid for sid, _ in list1[:10]]
    assert ids0 != ids1, "Slot 0 and Slot 1 should surface different top dramas!"
    print("✅ PASS: Dynamic rotation produces distinct, fresh short drama feeds across slots/refreshes!")


if __name__ == '__main__':
    main()
