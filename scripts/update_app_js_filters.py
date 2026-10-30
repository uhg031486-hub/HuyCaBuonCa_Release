import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCa_Web/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = """        } else if (currentFilter === 'tv://satellite') {
          filtered = allChannels.filter(c => (c.group || '').includes('Vệ Tinh') || (c.name || '').includes('True Premier') || (c.name || '').includes('Astro') || (c.name || '').includes('Sky Sports') || (c.name || '').includes('TNT Sports'));
        } else if (currentFilter === 'tv://favorites') {
          const favs = getFavorites();
          filtered = allChannels.filter(c => favs.some(f => f.id === c.id));
        } else if (currentFilter === 'tv://football') {
          // Lọc toàn bộ kênh bóng đá đỉnh cao Việt Nam & Quốc Tế
          filtered = allChannels.filter(c => {
            const grp = (c.group || '').toLowerCase();
            const nm = (c.name || '').toLowerCase();
            return grp.includes('bóng đá') || 
                   grp.includes('thể thao') || 
                   grp.includes('c1') ||
                   nm.includes('k+') || 
                   nm.includes('sport') || 
                   nm.includes('football') ||
                   nm.includes('vtv5') || 
                   nm.includes('vtv6') ||
                   nm.includes('htv thể thao') ||
                   nm.includes('bein') ||
                   nm.includes('cbs') ||
                   nm.includes('eurosport') ||
                   nm.includes('espn');
          });
        } else if (currentFilter === 'tv://vtv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtv'));
        } else if (currentFilter === 'tv://vtvcab') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtvcab'));
        } else if (currentFilter === 'tv://sctv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('sctv'));
        } else if (currentFilter === 'tv://sports_intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('ESPN') || (c.group || '').includes('Bóng Rổ') || (c.group || '').includes('FOX'));
        } else if (currentFilter === 'tv://racing_combat') {
          filtered = allChannels.filter(c => (c.group || '').includes('Đua Xe') || (c.group || '').includes('Võ Thuật') || (c.group || '').includes('Mạo Hiểm') || (c.group || '').includes('Đối Kháng'));
        } else if (currentFilter === 'tv://movies') {
          filtered = allChannels.filter(c => (c.group || '').includes('Rạp Phim') || (c.group || '').toLowerCase().includes('phim'));
        } else if (currentFilter === 'tv://live') {
          filtered = allChannels.filter(c => (c.group || '').includes('Sự Kiện') || (c.group || '').includes('LIVE'));
        } else if (currentFilter === 'tv://intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('Quốc Tế') || (c.group || '').includes('Hàn Quốc') || (c.group || '').includes('Trung Quốc') || (c.group || '').includes('Israel') || (c.group || '').includes('In The Box') || (c.group || '').includes('TVB'));
        } else if (currentFilter === 'tv://local') {
          filtered = allChannels.filter(c => (c.group || '').includes('Địa phương') || (c.group || '').includes('HTV'));
        } else if (currentFilter === 'tv://radio') {
          filtered = allChannels.filter(c => (c.group || '').includes('Radio'));
        }"""

replacement = """        } else if (currentFilter === 'tv://satellite') {
          filtered = allChannels.filter(c => (c.group || '').includes('Vệ Tinh') || (c.name || '').includes('True Premier') || (c.name || '').includes('Astro') || (c.name || '').includes('Sky Sports') || (c.name || '').includes('TNT Sports') || (c.name || '').includes('beIN'));
        } else if (currentFilter === 'tv://favorites') {
          const favs = getFavorites();
          filtered = allChannels.filter(c => favs.some(f => f.id === c.id));
        } else if (currentFilter === 'tv://football') {
          // Lọc toàn bộ kênh bóng đá đỉnh cao Việt Nam & Quốc Tế
          filtered = allChannels.filter(c => {
            const grp = (c.group || '').toLowerCase();
            const nm = (c.name || '').toLowerCase();
            return grp.includes('bóng đá') || 
                   grp.includes('thể thao') || 
                   grp.includes('c1') ||
                   nm.includes('k+') || 
                   nm.includes('sport') || 
                   nm.includes('football') ||
                   nm.includes('vtv5') || 
                   nm.includes('vtv6') ||
                   nm.includes('htv thể thao') ||
                   nm.includes('bein') ||
                   nm.includes('cbs') ||
                   nm.includes('eurosport') ||
                   nm.includes('fifa') ||
                   nm.includes('espn');
          });
        } else if (currentFilter === 'tv://vtv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtv') || (c.name || '').toLowerCase().startsWith('vtv'));
        } else if (currentFilter === 'tv://vtvcab') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtvcab'));
        } else if (currentFilter === 'tv://sctv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('sctv'));
        } else if (currentFilter === 'tv://sports_intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('ESPN') || (c.group || '').includes('Bóng Rổ') || (c.group || '').includes('FOX') || (c.group || '').includes('Bóng Đá Quốc Tế') || (c.name || '').toLowerCase().includes('sport') || (c.name || '').toLowerCase().includes('bein') || (c.name || '').toLowerCase().includes('eurosport') || (c.name || '').toLowerCase().includes('fifa') || (c.name || '').toLowerCase().includes('red bull'));
        } else if (currentFilter === 'tv://racing_combat') {
          filtered = allChannels.filter(c => (c.group || '').includes('Đua Xe') || (c.group || '').includes('Võ Thuật') || (c.group || '').includes('Mạo Hiểm') || (c.group || '').includes('Đối Kháng') || (c.name || '').toLowerCase().includes('red bull'));
        } else if (currentFilter === 'tv://movies') {
          filtered = allChannels.filter(c => (c.group || '').includes('Rạp Phim') || (c.group || '').toLowerCase().includes('phim') || (c.name || '').toLowerCase().includes('hbo') || (c.name || '').toLowerCase().includes('warner') || (c.name || '').toLowerCase().includes('cinemax'));
        } else if (currentFilter === 'tv://live') {
          filtered = allChannels.filter(c => (c.group || '').includes('Sự Kiện') || (c.group || '').includes('LIVE'));
        } else if (currentFilter === 'tv://intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('Quốc Tế') || (c.group || '').includes('Hàn Quốc') || (c.group || '').includes('Trung Quốc') || (c.group || '').includes('Israel') || (c.group || '').includes('In The Box') || (c.group || '').includes('TVB') || (c.group || '').includes('Vệ Tinh') || (c.name || '').includes('NHK') || (c.name || '').includes('Al Jazeera') || (c.name || '').includes('DW ') || (c.name || '').includes('France 24') || (c.name || '').includes('ABC News') || (c.name || '').includes('CBS News') || (c.name || '').includes('NBC News') || (c.name || '').includes('Bloomberg') || (c.name || '').includes('CNA') || (c.name || '').includes('Euronews') || (c.name || '').includes('Arirang') || (c.name || '').includes('Red Bull'));
        } else if (currentFilter === 'tv://local') {
          filtered = allChannels.filter(c => (c.group || '').includes('Địa phương') || (c.group || '').includes('HTV') || (c.name || '').toLowerCase().startsWith('htv') || (c.name || '').toLowerCase().startsWith('thvl'));
        } else if (currentFilter === 'tv://radio') {
          filtered = allChannels.filter(c => (c.group || '').includes('Radio'));
        }"""

# Chuẩn hóa line endings để tránh lỗi CRLF/LF
target_norm = target.replace('\r\n', '\n')
content_norm = content.replace('\r\n', '\n')
repl_norm = replacement.replace('\r\n', '\n')

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, repl_norm)
    with open('HuyCa_Web/js/app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ Đã cập nhật thành công filter trong HuyCa_Web/js/app.js!")
else:
    print("❌ Không tìm thấy target block trong app.js!")
