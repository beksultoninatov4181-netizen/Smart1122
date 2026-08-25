"""Mini App uchun kichik veb-server.

Faqat standart kutubxona ishlatiladi — qo'shimcha o'rnatish shart emas.
Bot ishga tushganda alohida oqimda (thread) ko'tariladi.

Kompyuterda sinash:   http://localhost:8080/?dev=1
Serverda (https):     Telegram ichida Mini App bo'lib ochiladi.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import logging
import mimetypes
import threading
import urllib.parse
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

log = logging.getLogger("miniapp")
BASE = Path(__file__).resolve().parent
# Odatda miniapp/ papkasida. Ba'zan (masalan brauzerdan yuklashda) fayllar
# to'g'ridan-to'g'ri ildizga tushib qoladi — o'sha holatni ham qo'llab-quvvatlaymiz.
STATIC = BASE / "miniapp"
if not (STATIC / "index.html").exists() and (BASE / "index.html").exists():
    STATIC = BASE

# bot moduli (start() da beriladi)
B = None
TOKEN = ""
DEV = False              # sinov rejimi — faqat aniq yoqilganda
BIND = "127.0.0.1"       # server: 0.0.0.0 (proksi orqasida)
MAX_AGE = 24 * 3600      # initData shu muddatdan eski bo'lsa qabul qilinmaydi


# ────────────────────────────────────────────────── Telegram initData
def verify_init_data(init_data: str) -> int | None:
    """Telegram yuborgan initData ni tekshiradi va user_id qaytaradi."""
    if not init_data or not TOKEN:
        return None
    try:
        pairs = urllib.parse.parse_qsl(init_data, keep_blank_values=True)
        data = dict(pairs)
        received = data.pop("hash", "")
        check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
        secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
        calc = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, received):
            return None
        # eski imzo qayta ishlatilmasin
        try:
            auth_date = int(data.get("auth_date", "0"))
        except ValueError:
            return None
        if auth_date and time.time() - auth_date > MAX_AGE:
            log.info("initData eskirgan")
            return None
        user = json.loads(data.get("user", "{}"))
        return int(user.get("id")) if user.get("id") else None
    except Exception as e:
        log.warning("initData xatosi: %s", e)
        return None


# ────────────────────────────────────────────────── ma'lumot yig'ish
def _biz_rang(i: int) -> list[str]:
    palitra = [
        ["#FF0F6B", "#FF9A00"],   # pushti → to'q sariq
        ["#6A00FF", "#00E0F0"],   # binafsha → firuza
        ["#00C853", "#B2FF59"],   # yashil → lime
        ["#FF6D00", "#FFD600"],   # sariq
        ["#0091EA", "#64FFDA"],   # ko'k
        ["#D500F9", "#FF4081"],   # siyoh pushti
    ]
    return palitra[i % len(palitra)]


def state_for(uid: int) -> dict:
    u = B.user_get(uid)
    admin = B.is_admin(uid)
    bizlar = B.my_businesses(uid)
    ids = [b["id"] for b in bizlar]
    bugun = B.bugun()
    iso = bugun.isoformat()
    oy_boshi = bugun.replace(day=1).isoformat()

    bizneslar = []
    for i, b in enumerate(bizlar):
        rows = B.tx_period(iso, iso, b["id"])
        inc, exp = B.totals(rows)
        m_inc, m_exp = B.totals(B.tx_period(oy_boshi, iso, b["id"]))
        item = {
            "id": b["id"], "nomi": b["nomi"], "emoji": b["emoji"],
            "rang": _biz_rang(b["id"] - 1),
            "bugun": {"kirim": inc, "chiqim": exp},
            "oy": {"kirim": m_inc, "chiqim": m_exp},
        }
        if admin:
            item["kassa"] = B.kassa_holati(b["id"])

        oy = B.oy_kaliti(bugun)
        plan = B.reja_get(b["id"], oy)
        jami_chiqim, toifalar = B.chiqim_oylik(b["id"], oy)
        item["reja"] = {
            "chegara": plan.get("", 0),
            "sarflandi": jami_chiqim,
            "toifalar": [
                {"nomi": t, "reja": plan[t], "sarf": toifalar.get(t, 0)}
                for t in B.TOIFALAR if t in plan
            ],
        }
        item["xodimlar"] = [
            {"nomi": u["nomi"], "rol": u["rol"]}
            for u in B.users_all()
            if u["rol"] == "admin" or u["biznes_id"] in (None, b["id"])
        ]
        bizneslar.append(item)

    # oxirgi 7 kun — grafik uchun
    kunlar = []
    for i in range(6, -1, -1):
        d = (bugun - timedelta(days=i)).isoformat()
        kun = {"sana": d, "kun": d[8:10] + "." + d[5:7], "biz": {}}
        for b in bizlar:
            inc, exp = B.totals(B.tx_period(d, d, b["id"]))
            kun["biz"][str(b["id"])] = {"kirim": inc, "chiqim": exp}
        kunlar.append(kun)

    # har bir yozuvdan keyingi kassa qoldig'i (o'sha biznes bo'yicha)
    joriy = {}
    if admin:
        for b in bizlar:
            k = B.kassa_holati(b["id"])
            joriy[b["id"]] = k["Naqd"] + k["Karta"]

    oxirgi = []
    for r in B.tx_last(40, ids):
        oxirgi.append({
            "id": r["id"], "biznes_id": r["biznes_id"], "sana": r["sana"],
            "vaqt": r["vaqt"], "tur": r["tur"], "izoh": r["izoh"],
            "tolov": r["tolov"], "valyuta": r["valyuta"],
            "karta": B.karta_nomi(r["karta_id"]) if (
                r["tolov"] == "Karta" and (r["karta_id"] or 0)) else "",
            "summa": r["summa"], "summa_uzs": r["summa_uzs"],
            "toifa": r["toifa"] or "",
            "kim": r["user_nomi"],
            "qoldiq": joriy.get(r["biznes_id"]) if admin else None,
        })
        # keyingi (eskiroq) yozuv uchun shu amalning ta'sirini olib tashlaymiz
        if admin and r["biznes_id"] in joriy and r["tolov"] in ("Naqd", "Karta"):
            joriy[r["biznes_id"]] -= (r["summa_uzs"] if r["tur"] == "Kirim"
                                      else -r["summa_uzs"])

    qarzlar = []
    for d in B.debts_all(only_open=True):
        if d["biznes_id"] in ids:
            qarzlar.append({
                "id": d["id"], "biznes_id": d["biznes_id"], "kim": d["kim"],
                "turi": d["turi"], "qoldiq": d["summa_uzs"] - d["qaytarilgan"],
                "sana": d["sana"], "izoh": d["izoh"],
            })

    muddatlar = []
    for m in B.muddat_all(ids):
        try:
            kuni = date.fromisoformat(m["sana"])
        except ValueError:
            continue
        muddatlar.append({
            "id": m["id"], "biznes_id": m["biznes_id"], "nomi": m["nomi"],
            "summa": m["summa"], "sana": m["sana"],
            "kun": (kuni - bugun).days,
        })

    kartalar = []
    if admin:
        for k in B.karta_all():
            q = B.karta_qoldiq(k["id"])
            kartalar.append({
                "id": k["id"], "nomi": k["nomi"],
                "oxiri": (k["raqam"] or "")[-4:],
                "qoldiq": q,
            })

    return {
        "user": {"id": uid, "nomi": u["nomi"] if u else "", "admin": admin},
        "bizneslar": bizneslar,
        "kartalar": kartalar,
        "muddatlar": muddatlar,
        "toifalar": B.TOIFALAR,
        "kunlar": kunlar,
        "oxirgi": oxirgi,
        "qarzlar": qarzlar,
        "kurs": B.rate(),
        "sana": bugun.strftime("%d.%m.%Y"),
        "bugun_iso": iso,
    }


def add_tx(uid: int, body: dict) -> dict:
    bizlar = [b["id"] for b in B.my_businesses(uid)]
    biz = int(body.get("biznes_id", 0))
    if biz not in bizlar:
        return {"error": "Bu biznesga ruxsatingiz yo'q"}
    try:
        summa = float(body.get("summa", 0))
    except (TypeError, ValueError):
        return {"error": "Summa noto'g'ri"}
    if summa <= 0:
        return {"error": "Summani kiriting"}
    tur = "Kirim" if body.get("tur") == "Kirim" else "Chiqim"
    valyuta = "USD" if body.get("valyuta") == "USD" else "UZS"
    tolov = body.get("tolov") if body.get("tolov") in ("Naqd", "Karta", "Qarzga") else "Naqd"
    uzs = summa * B.rate() if valyuta == "USD" else summa
    u = B.user_get(uid)
    now = B.hozir()
    tx_id = B.tx_add(
        biznes_id=biz, sana=now.strftime("%Y-%m-%d"), vaqt=now.strftime("%H:%M"),
        user_id=uid, user_nomi=(u["nomi"] if u else str(uid)), tur=tur,
        izoh=(body.get("izoh") or "").strip()[:200], tolov=tolov, valyuta=valyuta,
        summa=round(summa, 2), summa_uzs=round(uzs),
    )
    out = {"ok": True, "id": tx_id}
    if B.is_admin(uid):
        out["kassa"] = B.kassa_holati(biz)
    return out


def add_karta(uid: int, body: dict) -> dict:
    if not B.is_admin(uid):
        return {"error": "Faqat bot egasi karta qo'sha oladi"}
    nomi = (body.get("nomi") or "").strip()[:40]
    raqam = "".join(ch for ch in (body.get("raqam") or "") if ch.isdigit())[:20]
    if not nomi:
        return {"error": "Karta nomini kiriting"}
    return {"ok": True, "id": B.karta_add(nomi, raqam)}


def del_karta(uid: int, body: dict) -> dict:
    if not B.is_admin(uid):
        return {"error": "Faqat bot egasi"}
    B.karta_ochir(int(body.get("id", 0)))
    return {"ok": True}


def add_muddat(uid: int, body: dict) -> dict:
    if not B.is_admin(uid):
        return {"error": "Faqat bot egasi qo'sha oladi"}
    ids = [b["id"] for b in B.my_businesses(uid)]
    biz = int(body.get("biznes_id", 0))
    if biz not in ids:
        return {"error": "Bu biznesga ruxsatingiz yo'q"}
    nomi = (body.get("nomi") or "").strip()[:60]
    try:
        summa = float(body.get("summa", 0))
        sana = date.fromisoformat((body.get("sana") or "").strip())
    except (TypeError, ValueError):
        return {"error": "Summa yoki sana noto'g'ri"}
    if not nomi or summa <= 0:
        return {"error": "Nomi va summani kiriting"}
    return {"ok": True, "id": B.muddat_add(biz, nomi, summa, sana.isoformat())}


def yop_muddat(uid: int, body: dict) -> dict:
    if not B.is_admin(uid):
        return {"error": "Faqat bot egasi"}
    ids = [b["id"] for b in B.my_businesses(uid)]
    mid = int(body.get("id", 0))
    if not any(m["id"] == mid for m in B.muddat_all(ids, ochiq=False)):
        return {"error": "Topilmadi"}
    if body.get("ochir"):
        B.muddat_ochir(mid)
    else:
        B.muddat_yop(mid)
    return {"ok": True}


def set_reja(uid: int, body: dict) -> dict:
    if not B.is_admin(uid):
        return {"error": "Faqat bot egasi rejani o'zgartira oladi"}
    ids = [b["id"] for b in B.my_businesses(uid)]
    biz = int(body.get("biznes_id", 0))
    if biz not in ids:
        return {"error": "Bu biznesga ruxsatingiz yo'q"}
    toifa = (body.get("toifa") or "").strip()
    if toifa and toifa not in B.TOIFALAR:
        return {"error": "Bunday toifa yo'q"}
    try:
        summa = float(body.get("summa", 0))
    except (TypeError, ValueError):
        return {"error": "Summa noto'g'ri"}
    B.reja_set(biz, B.oy_kaliti(), toifa, max(0.0, summa))
    return {"ok": True}


def del_tx(uid: int, body: dict) -> dict:
    ids = [b["id"] for b in B.my_businesses(uid)]
    ok = B.tx_delete(int(body.get("id", 0)), ids)
    return {"ok": ok}


# ────────────────────────────────────────────────── HTTP
class Handler(BaseHTTPRequestHandler):
    server_version = "HisobotMiniApp"

    def log_message(self, fmt, *args):        # tinch turishi uchun
        pass

    # -- yordamchilar --
    def _send(self, code: int, body: bytes, ctype: str = "application/json",
              extra: dict | None = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode())

    def _uid(self) -> int | None:
        uid = verify_init_data(self.headers.get("X-Init-Data", ""))
        if uid:
            return uid if B.allowed(uid) else None

        # ── sinov rejimi (faqat kompyuterda) ──
        if not DEV:
            return None
        # proksi orqali kelgan so'rov "localhost" hisoblanmaydi
        if any(self.headers.get(h) for h in
               ("X-Forwarded-For", "X-Real-IP", "Forwarded", "X-Forwarded-Host")):
            return None
        if self.client_address[0] not in ("127.0.0.1", "::1"):
            return None
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "u" in params and self.command == "GET":     # boshqa xodim ko'rinishi
            try:
                test = int(params["u"][0])
            except ValueError:
                return None
            return test if B.allowed(test) else None
        adminlar = [u["user_id"] for u in B.users_all() if u["rol"] == "admin"]
        return adminlar[0] if adminlar else None

    # -- GET --
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html"):
            f = STATIC / "index.html"
            if not f.exists():
                self._send(404, b"index.html topilmadi", "text/plain; charset=utf-8")
                return
            self._send(200, f.read_bytes(), "text/html; charset=utf-8")
            return

        if path == "/api/state":
            uid = self._uid()
            if not uid:
                self._json({"error": "auth"}, 401)
                return
            try:
                self._json(state_for(uid))
            except Exception as e:
                log.exception("state xatosi")
                self._json({"error": str(e)}, 500)
            return

        if path == "/api/excel":
            uid = self._uid()
            if not uid:
                self._json({"error": "auth"}, 401)
                return
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            davr = (q.get("davr", ["hammasi"])[0] or "hammasi")
            if davr not in ("oy", "otgan", "chorak", "yil", "hammasi"):
                davr = "hammasi"
            ids = [b["id"] for b in B.my_businesses(uid)]
            biz_q = q.get("biz", [""])[0]
            if biz_q.isdigit() and int(biz_q) in ids:
                ids = [int(biz_q)]
            data = B.build_excel(ids, B.is_admin(uid), davr)
            nom = f"Hisob-kitob-{davr}-{B.bugun():%Y-%m-%d}.xlsx"
            self._send(200, data,
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       {"Content-Disposition": f'attachment; filename="{nom}"'})
            return

        # statik fayllar (rasm, ikonka va h.k.)
        rel = path.lstrip("/")
        f = (STATIC / rel).resolve()
        if rel and f.is_relative_to(STATIC.resolve()) and f.is_file():
            ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
            self._send(200, f.read_bytes(), ctype)
            return
        self._send(404, b"topilmadi", "text/plain; charset=utf-8")

    # -- POST --
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        uid = self._uid()
        if not uid:
            self._json({"error": "auth"}, 401)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._json({"error": "noto'g'ri so'rov"}, 400)
            return

        try:
            if path == "/api/tx":
                self._json(add_tx(uid, body))
            elif path == "/api/tx/delete":
                self._json(del_tx(uid, body))
            elif path == "/api/karta":
                self._json(add_karta(uid, body))
            elif path == "/api/karta/delete":
                self._json(del_karta(uid, body))
            elif path == "/api/muddat":
                self._json(add_muddat(uid, body))
            elif path == "/api/muddat/yop":
                self._json(yop_muddat(uid, body))
            elif path == "/api/reja":
                self._json(set_reja(uid, body))
            else:
                self._json({"error": "topilmadi"}, 404)
        except Exception as e:
            log.exception("POST xatosi")
            self._json({"error": str(e)}, 500)


_server: ThreadingHTTPServer | None = None


def start(bot_module, token: str, port: int = 8080,
          dev: bool = True, bind: str = "127.0.0.1") -> str:
    """Veb-serverni alohida oqimda ishga tushiradi. Manzilni qaytaradi.

    dev=True  — kompyuterda sinash (faqat 127.0.0.1 dan, proksisiz)
    bind      — serverda "0.0.0.0" qilinadi va dev=False bo'ladi
    """
    global B, TOKEN, DEV, BIND, _server
    B, TOKEN, DEV, BIND = bot_module, token, dev, bind
    _server = ThreadingHTTPServer((bind, port), Handler)
    t = threading.Thread(target=_server.serve_forever, daemon=True, name="miniapp")
    t.start()
    return f"http://localhost:{port}/?dev=1"


def stop() -> None:
    if _server:
        _server.shutdown()
