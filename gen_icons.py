"""Generate PWA icons for the FunPay Autopilot web dashboard."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_remote")

BG = (108, 92, 231)  # accent purple
FG = (255, 255, 255)


def make_icon(size: int, maskable: bool = False) -> Image.Image:
    img = Image.new("RGBA", (size, size), BG + (255,))
    d = ImageDraw.Draw(img)

    # Draw a simple radar/autopilot mark: concentric rings + needle
    cx = cy = size // 2
    pad = size // 8 if not maskable else size // 4
    max_r = (size // 2) - pad

    for frac in (1.0, 0.66, 0.33):
        r = int(max_r * frac)
        bbox = [cx - r, cy - r, cx + r, cy + r]
        width = max(2, size // 40)
        d.ellipse(bbox, outline=FG + (int(180 * frac) if frac < 1 else 255,), width=width)

    # Needle
    import math
    ang = math.radians(-45)
    nx = cx + int(max_r * math.cos(ang))
    ny = cy + int(max_r * math.sin(ang))
    d.line([cx, cy, nx, ny], fill=FG + (255,), width=max(3, size // 30))

    # Center dot
    dr = max(3, size // 25)
    d.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill=FG + (255,))

    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    # Standard icons
    make_icon(192).save(os.path.join(OUT, "icon-192.png"))
    make_icon(512).save(os.path.join(OUT, "icon-512.png"))
    # Maskable (Android adaptive)
    make_icon(512, maskable=True).save(os.path.join(OUT, "icon-512-maskable.png"))
    make_icon(192, maskable=True).save(os.path.join(OUT, "icon-192-maskable.png"))
    # Apple touch icon (opaque, 180)
    apple = Image.new("RGBA", (180, 180), BG + (255,))
    apple.paste(make_icon(180), (0, 0), make_icon(180))
    apple.save(os.path.join(OUT, "apple-touch-icon.png"))
    print("Icons generated in", OUT)


if __name__ == "__main__":
    main()
