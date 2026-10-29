with open('HuyCa_Web/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace in GaMoMePhimClient
old_gamome_proxy = '''    getProxyUrl(target) {
      if (window.location.protocol.startsWith('http')) {
        return '/api/proxy?url=' + encodeURIComponent(target);
      }
      return 'https://huyca.pages.dev/api/proxy?url=' + encodeURIComponent(target);
    },'''

new_proxy = '''    getProxyUrl(target) {
      return getAppProxyUrl(target);
    },'''

print("Gamome match:", old_gamome_proxy in content)
content = content.replace(old_gamome_proxy, new_proxy)

# Check if FreeReelsClient also has it
old_fr_proxy = '''    getProxyUrl(target) {
      if (window.location.protocol.startsWith('http')) {
        return '/api/proxy?url=' + encodeURIComponent(target);
      }
      return 'https://huyca.pages.dev/api/proxy?url=' + encodeURIComponent(target);
    },'''
print("FR match:", old_fr_proxy in content)
content = content.replace(old_fr_proxy, new_proxy)

with open('HuyCa_Web/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done replace proxy in app.js!")
