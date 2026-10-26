with open(r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\index.html", "r", encoding="utf-8") as f:
    content = f.read()

target = '<button id="btnSearch" class="btn-header focusable" tabindex="1" title="Tìm Kiếm">'
replacement = '''<a id="btnCinematicMode" href="cinematic/" class="btn-header btn-header-cinematic focusable" tabindex="0" title="Trải nghiệm giao diện Cinematic Đỉnh Cao">
        <span class="btn-icon">✨</span><span class="btn-text"> BẢN CINEMATIC</span>
      </a>
      <button id="btnSearch" class="btn-header focusable" tabindex="1" title="Tìm Kiếm">'''

if target in content:
    content = content.replace(target, replacement, 1)
    with open(r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated index.html successfully!")
else:
    print("Target not found!")
