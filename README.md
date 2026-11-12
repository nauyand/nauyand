# DF Live Banner (TikTok LIVE Studio)
Banner animasi Delta Force + chibi Vyron (fan art) + QR saweran + TOP GLOBAL donatur.

Link untuk sumber **Link** di TikTok LIVE Studio:
- Banner strip (portrait, 1440x480): https://raw.githack.com/nauyand/nauyand/live-overlay/banner.html
- Banner lebar (landscape, 1920x400): https://raw.githack.com/nauyand/nauyand/live-overlay/banner-wide.html
- Chibi Vyron saja (transparan, 320x400): https://raw.githack.com/nauyand/nauyand/live-overlay/vyron.svg

## Chibi Vyron
Gambar dan animasinya ada di `vyron.svg`: melayang pakai jetpack, melambai, berkedip, sesekali
mata senyum ^^ dengan hati muncul di atas antena. Dipakai otomatis oleh semua banner dan widget.

## QR saweran
Upload foto QR kamu ke repo dengan nama **`qr.png`**, dan banner akan langsung memakainya.
Kalau `qr.png` belum ada, QR dibuat dari `link` di `data.json`.
Bisa juga pakai gambar lain lewat URL, misalnya `banner.html?qr=gambar-qr-lain.png`.

## TOP GLOBAL
- **Otomatis dari Tako:** tambahkan `?tako=OVERLAY_KEY` di akhir link banner, misalnya
  `https://raw.githack.com/nauyand/nauyand/live-overlay/banner.html?tako=OVERLAY_KEY`.
  Isi panel diambil langsung dari overlay *Papan Peringkat* Tako. Warna dan tema diatur dari
  dashboard Tako. Ukuran isi bisa diatur dengan `&takozoom=0.8` (default 0.72).
  Sebaiknya overlay key **tidak** ditulis di `data.json`, karena repo ini publik.
- **Manual:** kalau `tako` tidak diisi, daftar diambil dari `top` di `data.json` dan diperbarui tiap 1 menit.

Edit `data.json` untuk mengubah nama, sub, link saweran, dan daftar top donatur manual.
