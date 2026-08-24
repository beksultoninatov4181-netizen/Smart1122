# Railway'ga qo'yish — qadamma-qadam

Botni internetdagi serverga ko'chiramiz. Shundan keyin:

- kompyuteringiz o'chsa ham bot **24/7 ishlaydi**
- Mini App **doimiy manzil**ga ega bo'ladi (tunnel kerak emas)
- yozuvlaringiz **doimiy diskda** saqlanadi

Butun jarayon ~20 daqiqa.

---

## 0. Avval: kompyuterdagi botni to'xtating

⚠️ Ikkita bot bitta token bilan ishlasa, bir-biriga xalal beradi va bot
g'alati ishlaydi.

Qora oynada **Ctrl+C** bosing va oynani yoping.

---

## 1. GitHub'ga yuklash

Railway kodni GitHub'dan oladi.

1. [github.com](https://github.com) → ro'yxatdan o'ting (bepul)
2. O'ng yuqorida **+** → **New repository**
3. Nom: `hisobot-bot`
4. **⚠️ MUHIM: `Private` ni tanlang** — bazangizda moliyaviy ma'lumot bor.
   Ochiq (Public) qilsangiz uni internetdagi hamma ko'radi
5. **Create repository**
6. Keyingi sahifada **uploading an existing file** havolasini bosing
7. `hisobot-railway` papkasining **ichidagi hamma narsani** oynaga sudrab tashlang
8. Pastda **Commit changes**

---

## 2. Railway'da loyiha yaratish

1. [railway.com](https://railway.com) → **New Project**
2. **Deploy from GitHub repo** → `hisobot-bot` ni tanlang
3. Railway qura boshlaydi — **kutib turing, hali tugamadi**

---

## 3. Token qo'shish

1. Xizmat kartochkasini bosing → **Variables**
2. **New Variable**:
   - Nomi: `BOT_TOKEN`
   - Qiymati: @BotFather bergan token
3. **Add**

---

## 4. ⚠️ Doimiy disk — eng muhim qadam

**Busiz har yangilanishda hamma yozuvingiz o'chib ketadi.**

1. Xizmat kartochkasiga o'ng tugma → **Attach Volume**
   (yoki: xizmat → **Settings** → **Volumes** → **Add Volume**)
2. **Mount path** maydoniga aynan shuni yozing:

   ```
   /data
   ```

3. **Add**

Bot ilk ishga tushganda bazani shu diskka ko'chiradi va bundan keyin doimo
o'sha yerdan ishlaydi. Keyingi yangilanishlar bazaga tegmaydi.

---

## 5. Domen olish (Mini App uchun)

1. Xizmat → **Settings** → **Networking**
2. **Generate Domain** → port so'rasa **8080** yozing

`xxx.up.railway.app` ko'rinishidagi manzil beriladi.
Bot uni **o'zi topib oladi** — qo'lda hech narsa yozmaysiz.

---

## 6. Tekshirish

**Deployments** → oxirgi deploy → **View Logs**. Shunday chiqishi kerak:

```
[baza] Boshlang'ich nusxa ko'chirildi -> /data/hisobot.db
[mini app] Manzil avtomatik saqlandi: https://xxx.up.railway.app
  ✅ Bot ishga tushdi:  @sizning_bot
  📂 Baza:              /data/hisobot.db
  🏢 Bizneslar:         ➕ Kirim, Smart
```

Telegramda botga **/start** yozing → keyin **/ilova** → Mini App ochiladi.

---

## Ma'lumot xavfsizligi

**Zaxira nusxa** — botga **/zaxira** yozing, u `.db` faylni yuboradi.
Shu faylni saqlab qo'ying. Vaqti-vaqti bilan takrorlang.

**Tiklash** — botga **/tikla** yozing, so'ng zaxira faylni **fayl sifatida**
yuboring. Baza o'sha holatga qaytadi. Almashtirishdan oldin hozirgi holat
ham avtomatik saqlanadi.

---

## Yangilash

Kodni o'zgartirganda GitHub'ga yangi faylni yuklaysiz — Railway o'zi qayta
quradi. **Bazangizga tegilmaydi**, u alohida diskda turadi.

---

## Muammo bo'lsa

**Deployments → View Logs** dagi xato matnini nusxalab yuboring.
