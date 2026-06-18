"""
Generates Greed Island trading card images using PIL.
Pure vector graphics (no emoji rendering needed) - avoids copyright issues
since no real anime artwork is used, only original geometric icon designs.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math
import io

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")
FONT_BOLD = os.path.join(ASSET_DIR, "Poppins-Bold.ttf")
FONT_SEMI = os.path.join(ASSET_DIR, "Poppins-SemiBold.ttf")
FONT_REG = os.path.join(ASSET_DIR, "Poppins-Regular.ttf")

W, H = 640, 896  # card canvas size (~2.5:3.5 ratio scaled up)

RARITY_COLORS = {
    "Common":    {"bg1": (90, 96, 105),   "bg2": (54, 58, 64),   "accent": (200, 205, 210), "glow": (160, 165, 170)},
    "Rare":      {"bg1": (40, 110, 200),  "bg2": (20, 50, 100),  "accent": (120, 190, 255), "glow": (60, 140, 230)},
    "Epic":      {"bg1": (140, 60, 200),  "bg2": (70, 25, 100),  "accent": (210, 150, 255), "glow": (170, 80, 230)},
    "Legendary": {"bg1": (230, 170, 30),  "bg2": (120, 75, 10),  "accent": (255, 225, 130), "glow": (255, 195, 60)},
}

def _font(path, size):
    return ImageFont.truetype(path, size)

def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def _vertical_gradient(draw, w, h, top_color, bottom_color, y_offset=0):
    for y in range(h):
        t = y / max(h - 1, 1)
        color = _lerp(top_color, bottom_color, t)
        draw.line([(0, y_offset + y), (w, y_offset + y)], fill=color)

def _radial_glow(size, color, intensity=180):
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = size // 2, size // 2
    for r in range(size // 2, 0, -2):
        alpha = int(intensity * (1 - r / (size / 2)) ** 2)
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, alpha))
    return glow

# ─── ICON DRAWING (pure vector, original geometric designs) ──────────────────

def icon_sword(draw, cx, cy, scale, color, dark):
    s = scale
    # blade
    draw.polygon([(cx, cy-s*0.9), (cx+s*0.12, cy+s*0.25), (cx-s*0.12, cy+s*0.25)], fill=color)
    draw.polygon([(cx-s*0.06, cy-s*0.85), (cx+s*0.06, cy-s*0.85), (cx+s*0.1, cy+s*0.2), (cx-s*0.1, cy+s*0.2)], fill=_lerp(color,(255,255,255),0.3))
    # crossguard
    draw.rectangle([cx-s*0.35, cy+s*0.2, cx+s*0.35, cy+s*0.32], fill=dark)
    # hilt
    draw.rectangle([cx-s*0.08, cy+s*0.32, cx+s*0.08, cy+s*0.62], fill=dark)
    draw.ellipse([cx-s*0.13, cy+s*0.58, cx+s*0.13, cy+s*0.74], fill=dark)

def icon_shield(draw, cx, cy, scale, color, dark):
    s = scale
    pts = [(cx, cy-s*0.85), (cx+s*0.65, cy-s*0.55), (cx+s*0.65, cy+s*0.15),
           (cx, cy+s*0.85), (cx-s*0.65, cy+s*0.15), (cx-s*0.65, cy-s*0.55)]
    draw.polygon(pts, fill=color)
    pts_in = [(cx, cy-s*0.6), (cx+s*0.42, cy-s*0.4), (cx+s*0.42, cy+s*0.05),
              (cx, cy+s*0.58), (cx-s*0.42, cy+s*0.05), (cx-s*0.42, cy-s*0.4)]
    draw.polygon(pts_in, fill=dark)

def icon_bow(draw, cx, cy, scale, color, dark):
    s = scale
    bbox = [cx-s*0.5, cy-s*0.9, cx+s*0.5, cy+s*0.9]
    draw.arc(bbox, 250, 110, fill=color, width=int(s*0.09))
    draw.line([(cx-s*0.42, cy-s*0.78), (cx-s*0.42, cy+s*0.78)], fill=dark, width=int(s*0.025))
    draw.line([(cx-s*0.75, cy), (cx+s*0.55, cy)], fill=color, width=int(s*0.07))
    draw.polygon([(cx+s*0.55, cy), (cx+s*0.35, cy-s*0.12), (cx+s*0.35, cy+s*0.12)], fill=color)

def icon_axe(draw, cx, cy, scale, color, dark):
    s = scale
    draw.rectangle([cx-s*0.06, cy-s*0.7, cx+s*0.06, cy+s*0.8], fill=dark)
    pts = [(cx+s*0.05, cy-s*0.65), (cx+s*0.6, cy-s*0.45), (cx+s*0.55, cy-s*0.05),
           (cx+s*0.05, cy-s*0.15)]
    draw.polygon(pts, fill=color)
    pts2 = [(cx-s*0.05, cy-s*0.65), (cx-s*0.6, cy-s*0.45), (cx-s*0.55, cy-s*0.05),
            (cx-s*0.05, cy-s*0.15)]
    draw.polygon(pts2, fill=color)

def icon_gem(draw, cx, cy, scale, color, dark):
    s = scale
    draw.polygon([(cx-s*0.5, cy-s*0.15), (cx-s*0.22, cy-s*0.6), (cx+s*0.22, cy-s*0.6), (cx+s*0.5, cy-s*0.15), (cx, cy+s*0.7)], fill=color)
    draw.polygon([(cx-s*0.22, cy-s*0.6), (cx+s*0.22, cy-s*0.6), (cx, cy-s*0.15)], fill=_lerp(color,(255,255,255),0.4))
    draw.line([(cx-s*0.5, cy-s*0.15), (cx, cy+s*0.7)], fill=dark, width=2)
    draw.line([(cx+s*0.5, cy-s*0.15), (cx, cy+s*0.7)], fill=dark, width=2)

def icon_flask(draw, cx, cy, scale, color, dark):
    s = scale
    draw.rectangle([cx-s*0.12, cy-s*0.85, cx+s*0.12, cy-s*0.55], fill=dark)
    pts = [(cx-s*0.12, cy-s*0.55), (cx+s*0.12, cy-s*0.55), (cx+s*0.45, cy+s*0.6),
           (cx, cy+s*0.85), (cx-s*0.45, cy+s*0.6)]
    draw.polygon(pts, fill=_lerp(color, (255,255,255), 0.15))
    draw.polygon([(cx-s*0.35, cy+s*0.2), (cx+s*0.35, cy+s*0.2), (cx+s*0.3, cy+s*0.6),
                  (cx, cy+s*0.78), (cx-s*0.3, cy+s*0.6)], fill=color)

def icon_scroll(draw, cx, cy, scale, color, dark):
    s = scale
    draw.rectangle([cx-s*0.5, cy-s*0.55, cx+s*0.5, cy+s*0.55], fill=color)
    draw.ellipse([cx-s*0.5-s*0.08, cy-s*0.62, cx-s*0.5+s*0.08, cy-s*0.48], fill=dark)
    draw.ellipse([cx+s*0.5-s*0.08, cy-s*0.62, cx+s*0.5+s*0.08, cy-s*0.48], fill=dark)
    draw.ellipse([cx-s*0.5-s*0.08, cy+s*0.48, cx-s*0.5+s*0.08, cy+s*0.62], fill=dark)
    draw.ellipse([cx+s*0.5-s*0.08, cy+s*0.48, cx+s*0.5+s*0.08, cy+s*0.62], fill=dark)
    for i in range(3):
        yy = cy - s*0.28 + i*s*0.28
        draw.line([(cx-s*0.32, yy), (cx+s*0.32, yy)], fill=dark, width=int(s*0.05))

def icon_bomb(draw, cx, cy, scale, color, dark):
    s = scale
    draw.ellipse([cx-s*0.5, cy-s*0.35, cx+s*0.5, cy+s*0.65], fill=dark)
    draw.ellipse([cx-s*0.25, cy-s*0.6, cx+s*0.05, cy-s*0.3], fill=_lerp(dark,(255,255,255),0.25))
    draw.line([(cx+s*0.05, cy-s*0.55), (cx+s*0.35, cy-s*0.85)], fill=color, width=int(s*0.06))
    draw.ellipse([cx+s*0.28, cy-s*0.95, cx+s*0.45, cy-s*0.78], fill=color)

def icon_staff(draw, cx, cy, scale, color, dark):
    s = scale
    draw.line([(cx, cy-s*0.6), (cx, cy+s*0.85)], fill=dark, width=int(s*0.07))
    _star(draw, cx, cy-s*0.75, s*0.32, color)

def icon_boot(draw, cx, cy, scale, color, dark):
    s = scale
    pts = [(cx-s*0.3, cy-s*0.7), (cx+s*0.15, cy-s*0.7), (cx+s*0.15, cy+s*0.15),
           (cx+s*0.55, cy+s*0.35), (cx+s*0.55, cy+s*0.6), (cx-s*0.3, cy+s*0.6)]
    draw.polygon(pts, fill=color)
    draw.rectangle([cx-s*0.3, cy-s*0.7, cx+s*0.15, cy-s*0.5], fill=dark)

def icon_glove(draw, cx, cy, scale, color, dark):
    s = scale
    draw.ellipse([cx-s*0.45, cy-s*0.1, cx+s*0.45, cy+s*0.7], fill=color)
    for i in range(4):
        xx = cx - s*0.32 + i * s*0.21
        draw.rounded_rectangle([xx, cy-s*0.65, xx+s*0.16, cy+s*0.05], radius=int(s*0.08), fill=color)

def icon_rope(draw, cx, cy, scale, color, dark):
    s = scale
    draw.arc([cx-s*0.5, cy-s*0.6, cx+s*0.5, cy+s*0.2], 0, 360, fill=color, width=int(s*0.14))
    draw.arc([cx-s*0.3, cy, cx+s*0.3, cy+s*0.7], 0, 360, fill=color, width=int(s*0.14))

def icon_crown(draw, cx, cy, scale, color, dark):
    s = scale
    pts = [(cx-s*0.55, cy+s*0.4), (cx-s*0.55, cy-s*0.1), (cx-s*0.25, cy+s*0.15),
           (cx, cy-s*0.55), (cx+s*0.25, cy+s*0.15), (cx+s*0.55, cy-s*0.1), (cx+s*0.55, cy+s*0.4)]
    draw.polygon(pts, fill=color)
    draw.rectangle([cx-s*0.55, cy+s*0.4, cx+s*0.55, cy+s*0.6], fill=color)
    for dx in (-0.55, 0, 0.55):
        draw.ellipse([cx+s*dx-s*0.08, cy-s*0.65, cx+s*dx+s*0.08, cy-s*0.49], fill=_lerp(color,(255,255,255),0.5))

def icon_book(draw, cx, cy, scale, color, dark):
    s = scale
    draw.polygon([(cx, cy-s*0.6), (cx-s*0.55, cy-s*0.4), (cx-s*0.55, cy+s*0.6), (cx, cy+s*0.4)], fill=color)
    draw.polygon([(cx, cy-s*0.6), (cx+s*0.55, cy-s*0.4), (cx+s*0.55, cy+s*0.6), (cx, cy+s*0.4)], fill=_lerp(color,(0,0,0),0.15))
    draw.line([(cx, cy-s*0.6), (cx, cy+s*0.4)], fill=dark, width=2)

def icon_hammer(draw, cx, cy, scale, color, dark):
    s = scale
    draw.rectangle([cx-s*0.07, cy-s*0.2, cx+s*0.07, cy+s*0.85], fill=dark)
    draw.rounded_rectangle([cx-s*0.5, cy-s*0.65, cx+s*0.5, cy-s*0.15], radius=int(s*0.08), fill=color)

def icon_lamp(draw, cx, cy, scale, color, dark):
    s = scale
    draw.polygon([(cx-s*0.4, cy-s*0.1), (cx+s*0.4, cy-s*0.1), (cx+s*0.25, cy+s*0.4), (cx-s*0.25, cy+s*0.4)], fill=color)
    draw.ellipse([cx-s*0.12, cy-s*0.55, cx+s*0.12, cy-s*0.05], fill=_lerp(color,(255,255,255),0.6))
    draw.rectangle([cx-s*0.08, cy+s*0.4, cx+s*0.08, cy+s*0.6], fill=dark)

def icon_star(draw, cx, cy, scale, color, dark=None):
    _star(draw, cx, cy, scale, color)

def _star(draw, cx, cy, s, color):
    pts = []
    for i in range(10):
        ang = math.pi/2 + i * math.pi / 5
        r = s if i % 2 == 0 else s * 0.4
        pts.append((cx + r * math.cos(ang), cy - r * math.sin(ang)))
    draw.polygon(pts, fill=color)

def icon_egg(draw, cx, cy, scale, color, dark):
    s = scale
    draw.ellipse([cx-s*0.45, cy-s*0.6, cx+s*0.45, cy+s*0.7], fill=color)
    draw.ellipse([cx-s*0.18, cy-s*0.35, cx+s*0.1, cy-s*0.05], fill=_lerp(color,(255,255,255),0.4))

def icon_chain(draw, cx, cy, scale, color, dark):
    s = scale
    for i, dy in enumerate([-0.55, -0.1, 0.35]):
        offset = s*0.18 if i % 2 else -s*0.18
        draw.ellipse([cx+offset-s*0.22, cy+s*dy-s*0.22, cx+offset+s*0.22, cy+s*dy+s*0.22], outline=color, width=int(s*0.09))

def icon_default(draw, cx, cy, scale, color, dark):
    _star(draw, cx, cy, scale, color)

ICON_MAP = [
    (["sword", "blade", "knife", "dagger", "excalibur"], icon_sword),
    (["shield", "armor", "scale", "robe", "wall", "barrier", "perfect nen"], icon_shield),
    (["bow", "arrow", "spear"], icon_bow),
    (["axe", "cleave", "hammer", "mjolnir"], icon_hammer),
    (["gem", "crystal", "echo", "fate", "stone", "diamond", "world map", "complete world"], icon_gem),
    (["flask", "potion", "vial", "elixir", "pot"], icon_flask),
    (["map", "scroll", "tablet", "book", "compass"], icon_scroll),
    (["bomb", "smoke"], icon_bomb),
    (["wand", "staff"], icon_staff),
    (["boot"], icon_boot),
    (["glove", "gauntlet", "fist", "hand", "godhand"], icon_glove),
    (["rope", "whip", "net", "chain", "cage", "trap", "snare"], icon_rope),
    (["crown", "king"], icon_crown),
    (["egg"], icon_egg),
    (["lamp", "lantern", "candle", "torch"], icon_lamp),
]

def get_icon_fn(name):
    n = name.lower()
    for keywords, fn in ICON_MAP:
        if any(k in n for k in keywords):
            return fn
    return icon_default

# ─── MAIN CARD RENDERER ───────────────────────────────────────────────────────

def render_card(card_id, card, save_path=None):
    """
    card: dict with keys name, rarity, atk, def, spd, ability, ability_desc
    Returns PIL Image. If save_path given, also saves to disk.
    """
    rc = RARITY_COLORS[card["rarity"]]
    img = Image.new("RGB", (W, H), rc["bg2"])
    draw = ImageDraw.Draw(img)

    # Background gradient
    _vertical_gradient(draw, W, H, rc["bg1"], rc["bg2"])

    # Subtle glow behind icon
    glow = _radial_glow(420, rc["glow"], intensity=140)
    img.paste(glow, (W//2 - 210, 170), glow)
    draw = ImageDraw.Draw(img)

    # Outer border
    border_w = 10
    draw.rectangle([border_w//2, border_w//2, W-border_w//2, H-border_w//2],
                   outline=rc["accent"], width=border_w)
    draw.rectangle([22, 22, W-22, H-22], outline=rc["accent"], width=2)

    # Top bar: card number + rarity label
    f_num = _font(FONT_BOLD, 30)
    f_rarity = _font(FONT_SEMI, 26)
    draw.rounded_rectangle([34, 34, 150, 80], radius=12, fill=(0,0,0,80))
    draw.text((92, 57), f"#{card_id:03d}", font=f_num, fill=(255,255,255), anchor="mm")

    rarity_text = card["rarity"].upper()
    bbox = draw.textbbox((0,0), rarity_text, font=f_rarity)
    rw = bbox[2]-bbox[0]
    draw.rounded_rectangle([W-34-rw-32, 34, W-34, 80], radius=12, fill=rc["accent"])
    draw.text((W-34-rw/2-16, 57), rarity_text, font=f_rarity, fill=rc["bg2"], anchor="mm")

    # Icon
    icon_fn = get_icon_fn(card["name"])
    icon_color = _lerp(rc["accent"], (255,255,255), 0.1)
    icon_dark = rc["bg2"]
    icon_fn(draw, W//2, 290, 150, icon_color, icon_dark)

    # Card name
    f_name = _font(FONT_BOLD, 42)
    name = card["name"]
    # auto-shrink long names
    while draw.textbbox((0,0), name, font=f_name)[2] > W - 80 and f_name.size > 26:
        f_name = _font(FONT_BOLD, f_name.size - 2)
    draw.text((W//2, 450), name, font=f_name, fill=(255,255,255), anchor="mm")

    # Divider
    draw.line([(50, 495), (W-50, 495)], fill=rc["accent"], width=2)

    # Stats row
    f_stat_label = _font(FONT_SEMI, 22)
    f_stat_val = _font(FONT_BOLD, 38)
    stats = [("ATK", card["atk"], (235,90,90)), ("DEF", card["def"], (90,170,235)), ("SPD", card["spd"], (235,210,90))]
    stat_w = (W - 100) // 3
    for i, (label, val, color) in enumerate(stats):
        sx = 50 + stat_w * i + stat_w // 2
        draw.ellipse([sx-34, 525, sx+34, 593], fill=color)
        draw.text((sx, 559), str(val), font=f_stat_val, fill=(255,255,255), anchor="mm")
        draw.text((sx, 612), label, font=f_stat_label, fill=rc["accent"], anchor="mm")

    # Divider
    draw.line([(50, 650), (W-50, 650)], fill=rc["accent"], width=2)

    # Ability box
    f_ability_name = _font(FONT_BOLD, 28)
    f_ability_desc = _font(FONT_REG, 22)
    draw.text((W//2, 685), card['ability'].upper(), font=f_ability_name, fill=rc["accent"], anchor="mm")

    # Wrap ability description
    desc = card["ability_desc"]
    words = desc.split()
    lines = []
    cur = ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if draw.textbbox((0,0), test, font=f_ability_desc)[2] > W - 90:
            lines.append(cur)
            cur = w_
        else:
            cur = test
    if cur:
        lines.append(cur)

    y = 730
    for line in lines[:3]:
        draw.text((W//2, y), line, font=f_ability_desc, fill=(235,235,235), anchor="mm")
        y += 30

    # Bottom branding
    f_brand = _font(FONT_SEMI, 20)
    draw.text((W//2, H-40), "GREED ISLAND", font=f_brand, fill=rc["accent"], anchor="mm")

    if save_path:
        img.save(save_path, "PNG")
    return img

def render_card_bytes(card_id, card):
    """Render and return as bytes buffer (for sending directly to Telegram)."""
    img = render_card(card_id, card)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf
