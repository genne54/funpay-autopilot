FUNPAY AUTOPILOT - INSTALACIJA I ZAPUSK
========================================

Trebosvanija:
  - Python 3.10+ (stahlkaja, ne Microsoft Store versija)
  - pip

1. USTANOVIT' ZAVISIMOSTI
   Otkroite terminal v papke s proektom i vypolnite:

       pip install -r requirements.txt

2. ZAPUSTIT' BACKEND (API + baza dannih)
   Pervoe okno terminala:

       python backend\main.py

   Server podnimetsja na http://localhost:8000
   Dokumentacija API: http://localhost:8000/docs

3. ZAPUSTIT' PRILOZENIE (okno na Windows)
   Vtoroe okno terminala:

       python windows_app\main.py

4. ZAPUSTIT' TELEGRAM-BOTA (esli nuzhen bot)
   Tret'e okno terminala:

       python telegram_bot\main.py

   Pered etim vdite token bota v fail .env:
       FPA_TELEGRAM_BOT_TOKEN=<vasi_token>

5. UDALENNOE UPRAVLENIE S TELEFONA
   Otkroite fail web_remote\index.html v brauzere telefona
   (ili razdajte papku web_remote kak web-sajt).

----------------------------------------
Dlja ostanovki: nazmite Ctrl+C v nuznom okne.
