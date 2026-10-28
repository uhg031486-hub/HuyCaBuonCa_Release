import os
import win32file
import win32con

def copy_locked_file(src, dst):
    h = win32file.CreateFile(
        src,
        win32con.GENERIC_READ,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL,
        None
    )
    with open(dst, 'wb') as f:
        while True:
            hr, data = win32file.ReadFile(h, 64*1024)
            if not data:
                break
            f.write(data)
    win32file.CloseHandle(h)

user_data = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
profiles = ['Default'] + [x for x in os.listdir(user_data) if x.startswith('Profile ')]
for p in profiles:
    cp = os.path.join(user_data, p, 'Network', 'Cookies')
    if os.path.exists(cp):
        tmp = os.path.join(os.environ['TEMP'], f'c_{p}.db')
        try:
            copy_locked_file(cp, tmp)
            import sqlite3
            conn = sqlite3.connect(tmp)
            c = conn.cursor()
            c.execute('SELECT DISTINCT host_key FROM cookies')
            hosts = [r[0] for r in c.fetchall() if 'muse' in r[0]]
            print(p, 'MATCHING HOSTS:', hosts)
            conn.close()
            os.remove(tmp)
        except Exception as e:
            print(p, 'ERR:', e)
