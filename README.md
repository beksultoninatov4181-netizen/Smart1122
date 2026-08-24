# 💰 Hisob-kitob boti — v3

Bir nechta biznes uchun Telegram bot: kirim/chiqim, ikkita kassa, qarzlar,
avtomatik kunlik va oylik Excel hisobot.

## Ishga tushirish

`ISHGA-TUSHIRISH.bat` ni bosing. Eski versiyadan o'tish — `ISHGA-TUSHIRISH.txt`.

## Yozish

```
+150000 kunlik savdo      → kirim
-45000 ijara              → chiqim
+20$ mijozdan             → dollarda (kurs bo'yicha so'mga o'giradi)
-1,5 mln tovar oldim      → «ming» va «mln» ishlaydi
```

Bot qaysi biznesga yozishni so'raydi. Kategoriya yo'q — sababini izohga yozasiz.

Tugmalar bilan: **biznes → summa → izoh → to'lov turi**.

To'lov turi uchta: 💵 Naqd, 💳 Karta, 📝 Qarzga.
«Qarzga» kassaga tegmaydi — qarz yopilganda kassaga tushadi.

## Kassa

Ikkita kassa, har biznes uchun alohida:

```
boshlang'ich qoldiq + naqd kirimlar − naqd chiqimlar = 💵 naqd kassa
boshlang'ich qoldiq + karta kirimlar − karta chiqimlar = 💳 karta kassa
```

- **⚙️ Boshlang'ich qoldiq** — bir marta kiritasiz (`2000000, 1500000`)
- **🧮 Kassani tekshirish** — qo'ldagi pulni sanaysiz; farq chiqsa bot uni
  «kamomad» yoki «ortiqcha» yozuvi qilib qo'yadi, kassa haqiqatga teng bo'ladi
- **🔁 Pul ko'chirish** — naqd↔karta yoki biznesdan biznesga; foydaga ta'sir qilmaydi
- **📆 Kassa harakati** — kun-kun qoldiq qanday o'zgargani
- Kassa minusga tushsa bot ogohlantiradi, lekin yozishga to'sqinlik qilmaydi

Kassa bo'limi **faqat bot egasida**. Xodim kassa qoldig'ini ko'rmaydi.

## Avtomatik hisobot

| Qachon | Nima keladi |
|---|---|
| Har kuni **22:00** | Kun yakuni (har biznes + jami + kassa) va Excel fayl |
| Oyning oxirgi kuni | Yuqoridagiga qo'shimcha: oy yakuni va oylik Excel |

Vaqtni o'zgartirish: `/vaqt 21:30`. Hozir olish: `/hisobot`.
Faqat bot egasiga yuboriladi.

## Excel

7 ta varaq:

- **Xulosa** — har biznes bo'yicha kirim/chiqim/foyda + kassa qoldig'i
- **Har biznesga alohida varaq** — barcha yozuvlar
- **Kunlik hisobot** — har kun bir qator, har biznes uchun ustunlar, o'ngda jami
- **Oylik hisobot** — xuddi shunday, oylar bo'yicha
- **Qarzlar**, **Pul ko'chirish**

## Xodimlar

⚙️ Sozlamalar → 👥 Xodimlar → ➕ Xodim qo'shish → ID → qaysi biznes.

Xodim: faqat o'z biznesiga yozadi, o'z hisobotini ko'radi.
Kassani, boshqa biznesni, tekshirish va pul ko'chirishni ko'rmaydi.

## Bizneslar

⚙️ Sozlamalar → 🏢 Bizneslar. Nomini o'zgartirish uchun ustiga bosing.
Emoji ham kerak bo'lsa nom oldiga yozing: `🛒 Markaziy do'kon`.

## 24/7 ishlashi

Bot kompyuter o'chsa to'xtaydi va 22:00 dagi hisobot ham kelmaydi
(keyingi ishga tushganda yuboriladi). Doimiy ishlashi uchun VPS:

```ini
# /etc/systemd/system/hisobot.service
[Unit]
Description=Hisob-kitob boti
After=network.target

[Service]
WorkingDirectory=/home/user/hisobot-bot
ExecStart=/usr/bin/python3 /home/user/hisobot-bot/bot.py
Environment=BOT_TOKEN=sizning_tokeningiz
Restart=always
User=user

[Install]
WantedBy=multi-user.target
```

## Zaxira nusxa

`hisobot.db` — butun bazangiz. Vaqti-vaqti bilan nusxalab qo'ying.

---

# 📱 Mini App (v4)

Botning ichidagi ilova: kassa, yozish, tarix, hisobot — bitta rangli ekranda.
Qo'shimcha kutubxona kerak emas, veb-server botning o'zida ishlaydi.

## Kompyuterda sinash

Bot ishlab turganda: `MINI-APP-OCHISH.bat`
yoki brauzerda `http://localhost:8080/?dev=1`

Xodim ko'rinishi: `http://localhost:8080/?u=XODIM_ID`

## Ekranlar

| Ekran | Nima bor |
|---|---|
| 🏠 Bosh | Kassa (jami + har biznes), bugungi kirim/chiqim, oxirgi yozuvlar, qarzlar |
| ✏️ Yozish | Kirim/chiqim → biznes → summa (klaviatura, `$` tugmasi) → to'lov → izoh |
| 📜 Tarix | Kunlar bo'yicha guruhlangan; uzoq bosib turib o'chirish |
| 📊 Hisobot | 7 kunlik ustunli grafik, oylik foyda, biznes kesimi, Excel |

Har biznes o'z rangiga ega — qayerga qarasangiz ham qaysi biznes ekani ko'rinadi.
Xodim kassani ko'rmaydi (bu yerda ham).

## Telegram ichida ochilishi

Server (https) kerak. Tayyor bo'lgach:

```
/ilova_manzil https://sizning-manzilingiz
```

Keyin `/ilova` — Telegram ichida ochiladigan tugma beradi.

## Xavfsizlik

Telegram yuboradigan `initData` bot tokeni bilan tekshiriladi (HMAC-SHA256) —
boshqa odam o'zini siz deb ko'rsata olmaydi. Ruxsatsiz foydalanuvchi 401 oladi.
`?dev=1` rejimi faqat localhost'dan ishlaydi.
