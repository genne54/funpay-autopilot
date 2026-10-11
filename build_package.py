"""
Pack the FunPay Autopilot project into a distributable zip archive.

The archive excludes secrets (.env), caches (__pycache__), local database
and build output. Used by the Telegram bot to deliver the app as a file.
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(ROOT, "build")
ARCHIVE = os.path.join(BUILD_DIR, "FunPayAutopilot-windows.zip")
MOBILE_ARCHIVE = os.path.join(BUILD_DIR, "FunPayAutopilot-mobile-pwa.zip")

# Folders/files to pack
INCLUDE_DIRS = ["backend", "telegram_bot", "windows_app", "web_remote", "shared"]
INCLUDE_FILES = ["config.py", "requirements.txt", "test_all.py", "__init__.py", "README_INSTALL.txt"]

# Never include these
EXCLUDE_NAMES = {"__pycache__", ".env", "build", "funpay_autopilot.db", "*.pyc"}


def should_skip(name: str) -> bool:
    for ex in EXCLUDE_NAMES:
        if ex.startswith("*"):
            if name.endswith(ex[1:]):
                return True
        elif name == ex:
            return True
    return False


def build_package():
    os.makedirs(BUILD_DIR, exist_ok=True)
    if os.path.exists(ARCHIVE):
        os.remove(ARCHIVE)

    file_count = 0
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in INCLUDE_DIRS:
            base = os.path.join(ROOT, d)
            if not os.path.isdir(base):
                continue
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = [x for x in dirnames if not should_skip(x)]
                for fn in filenames:
                    if should_skip(fn):
                        continue
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, ROOT)
                    zf.write(full, rel)
                    file_count += 1

        for f in INCLUDE_FILES:
            full = os.path.join(ROOT, f)
            if os.path.isfile(full):
                zf.write(full, f)
                file_count += 1

    size_kb = os.path.getsize(ARCHIVE) // 1024
    print(f"Archive created: {ARCHIVE}")
    print(f"Files packed: {file_count}, size: {size_kb} KB")


MOBILE_README = (
    "FUNPAY AUTOPILOT - PWA (Android + iPhone)\r\n"
    "=========================================\r\n\r\n"
    "Eto ustanavlivaemoe mobil'noe prilozhenie (PWA) - stavitja na domashnij ekran kak obichnoe prilozhenie.\r\n\r\n"
    "CHTOBY ZAPUSTIT':\r\n"
    "1) Na kompjutere raskhante papku i zapustite backend:\r\n"
    "       python backend\\main.py\r\n"
    "2) Uznajte IP kompjutera (komanda ipconfig, napr. 192.168.1.50).\r\n"
    "3) Na telefone v brauzere otkroite:\r\n"
    "       http://<IP-kompjutera>:8000/app/\r\n\r\n"
    "ANDROOID (Chrome):\r\n"
    "   - Otkroyte adres, nazmite menju (3 tochki) -> 'Ustanovit' prilozhenie' / 'Nagl. ekran'.\r\n"
    "   - Znachok pojvitsja na rabochem stole.\r\n\r\n"
    "iPHONE (Safari):\r\n"
    "   - Otkroyte adres, nazmite 'Podelitsja' -> 'Na ekran Domoy'.\r\n"
    "   - Prilozhenie ustanovitsja kak ikonka.\r\n\r\n"
    "Dlja udalennogo dostupa vne domashnej seti probros'te port 8000 na routeru.\r\n"
)


def build_mobile():
    """Pack the web PWA dashboard into a mobile-ready zip."""
    os.makedirs(BUILD_DIR, exist_ok=True)
    if os.path.exists(MOBILE_ARCHIVE):
        os.remove(MOBILE_ARCHIVE)

    web_dir = os.path.join(ROOT, "web_remote")
    if not os.path.isdir(web_dir):
        print("web_remote not found, skipping mobile archive")
        return

    file_count = 0
    with zipfile.ZipFile(MOBILE_ARCHIVE, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(web_dir):
            dirnames[:] = [x for x in dirnames if not should_skip(x)]
            for fn in filenames:
                if should_skip(fn):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, web_dir)
                zf.write(full, rel)
                file_count += 1
        zf.writestr("README.txt", MOBILE_README.encode("utf-8"))

    size_kb = os.path.getsize(MOBILE_ARCHIVE) // 1024
    print(f"Mobile archive created: {MOBILE_ARCHIVE}")
    print(f"Files packed: {file_count}, size: {size_kb} KB")


def main():
    build_package()
    build_mobile()


if __name__ == "__main__":
    main()
