with open(r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\index.html", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("css/style.css?v=3.0.0", "css/style.css?v=3.0.1")
c = c.replace("js/hls.min.js?v=3.0.0", "js/hls.min.js?v=3.0.1")
c = c.replace("js/app.js?v=3.0.0", "js/app.js?v=3.0.1")

with open(r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\index.html", "w", encoding="utf-8") as f:
    f.write(c)

print("Bumped version query string to v=3.0.1 in index.html!")
