"""Gera o banner do perfil do GitHub (tema claro e escuro).

Uso:  python perfil-github/tools/banner.py

Sai em perfil-github/assets/banner-{dark,light}.png
Rode de novo depois de mexer em qualquer texto/ cor abaixo.
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- config
W, H = 2400, 600  # 4:1 — aparece com ~880x220 no README

FONT_DIR = os.path.join("tools", "fonts", "inter", "extras", "otf")
MONO = "C:/Windows/Fonts/consola.ttf"
MONO_BOLD = "C:/Windows/Fonts/consolab.ttf"

LABEL = "OPEN SOURCE  ·  ANDROID  ·  IA  ·  TOOLING"
NAME = "Jaíved Pereira"
SUB = "faço uns bagulho doido — e coloco em produção"
PILLS = ["Kotlin", "Jetpack Compose", "Python", "MCP", "Android", "TypeScript"]

TERM = [
    ("$ whoami", True),
    ("jaivedpereira", False),
    ("$ ls foco/", True),
    ("android   ia   tooling", False),
    ("$", True),  # linha do cursor
]

OUT_DIR = os.path.join("perfil-github", "assets")

THEMES = {
    "dark": dict(
        top="#0A0E14",
        bottom="#111C2C",
        glow_a=(34, 211, 238),   # ciano
        glow_b=(244, 114, 182),  # rosa
        accent="#22D3EE",
        label="#7DD3FC",
        name="#FFFFFF",
        sub="#93A4B8",
        pill_border=(255, 255, 255, 56),
        pill_text="#E4EBF5",
        bar=("#22D3EE", "#A78BFA", "#F472B6"),
        card_fill=(255, 255, 255, 9),
        card_border=(255, 255, 255, 34),
        dot="#334155",
        term_text="#CBD8E6",
        term_dim="#7C8B9C",
    ),
    "light": dict(
        top="#F8FAFD",
        bottom="#E8EFF8",
        glow_a=(56, 189, 248),
        glow_b=(251, 113, 133),
        accent="#0284C7",
        label="#0369A1",
        name="#0B1220",
        sub="#4A5A6E",
        pill_border=(2, 6, 23, 32),
        pill_text="#334155",
        bar=("#0EA5E9", "#8B5CF6", "#F43F5E"),
        card_fill=(255, 255, 255, 235),
        card_border=(2, 6, 23, 28),
        dot="#E2E8F0",
        term_text="#3C4A5A",
        term_dim="#7C8899",
    ),
}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def vertical_gradient(size, c1, c2) -> Image.Image:
    """Gradiente vertical barato: 1 coluna interpolada e depois resize."""
    w, h = size
    col = Image.new("RGB", (1, h))
    px = col.load()
    a, b = Image.new("RGB", (1, 1), c1).getpixel((0, 0)), Image.new("RGB", (1, 1), c2).getpixel((0, 0))
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return col.resize((w, h), Image.BILINEAR)


def glow(canvas: Image.Image, xy, radius: int, color, alpha: int) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = xy
    d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55))
    canvas.alpha_composite(layer)


def tracked_text(d: ImageDraw.ImageDraw, xy, text, f, fill, tracking: float):
    """Texto com espaçamento entre letras (PIL não tem letter-spacing)."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking
    return x


def rounded_bar(d, box, colors, radius):
    """Barra com gradiente horizontal (recortada no formato arredondado)."""
    x0, y0, x1, y1 = box
    grad = Image.new("RGB", (max(1, x1 - x0), 1))
    px = grad.load()
    stops = [Image.new("RGB", (1, 1), c).getpixel((0, 0)) for c in colors]
    n = x1 - x0
    for i in range(n):
        t = i / max(1, n - 1) * (len(stops) - 1)
        k = min(int(t), len(stops) - 2)
        f = t - k
        px[i, 0] = tuple(round(stops[k][j] + (stops[k + 1][j] - stops[k][j]) * f) for j in range(3))
    grad = grad.resize((n, y1 - y0), Image.BILINEAR)
    mask = Image.new("L", (n, y1 - y0), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, n - 1, y1 - y0 - 1], radius=radius, fill=255)
    d._image.paste(grad, (x0, y0), mask)


def alpha_shape(canvas: Image.Image, fn) -> None:
    """Desenha formas com cor RGBA de verdade.

    ImageDraw grava o pixel cru (RGB + alpha) em vez de compor, então uma cor
    branca com alpha 26 vira branco sólido depois do convert('RGB'). Desenhar
    numa camada separada e compor resolve.
    """
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer))
    canvas.alpha_composite(layer)


def build(theme_name: str) -> Image.Image:
    t = THEMES[theme_name]
    canvas = vertical_gradient((W, H), t["top"], t["bottom"]).convert("RGBA")

    # brilhos de fundo
    glow(canvas, (150, 40), 620, t["glow_a"], 46 if theme_name == "dark" else 30)
    glow(canvas, (2280, 620), 700, t["glow_b"], 40 if theme_name == "dark" else 26)

    d = ImageDraw.Draw(canvas)

    f_label = font("Inter-SemiBold.otf", 27)
    f_name = font("InterDisplay-Bold.otf", 132)
    f_sub = font("Inter-Regular.otf", 42)
    f_pill = font("Inter-Medium.otf", 30)
    f_mono = ImageFont.truetype(MONO, 30)

    x = 130

    # -------- etiqueta
    tracked_text(d, (x, 96), LABEL, f_label, t["label"], 5.2)
    small_w = sum(d.textlength(c, font=f_label) + 5.2 for c in LABEL)
    d.rounded_rectangle([x, 150, x + small_w - 5, 154], radius=2, fill=t["accent"])

    # -------- nome
    d.text((x, 176), NAME, font=f_name, fill=t["name"])
    name_w = d.textlength(NAME, font=f_name)

    # barra gradiente sob o nome
    rounded_bar(d, (x, 336, x + round(name_w * 0.62), 346), t["bar"], 5)

    # -------- subtítulo
    d.text((x, 380), SUB, font=f_sub, fill=t["sub"])

    # -------- pílulas de stack
    px_, py_ = x, 470
    boxes = []
    for p in PILLS:
        w = d.textlength(p, font=f_pill) + 52
        boxes.append((px_, py_ + 62, px_ + w, p))
        px_ += w + 16

    pill_fill = (255, 255, 255, 26) if theme_name == "dark" else (255, 255, 255, 210)
    alpha_shape(canvas, lambda dd: [
        dd.rounded_rectangle([bx0, py_, bx1, by1], radius=31, outline=t["pill_border"], width=2, fill=pill_fill)
        for bx0, by1, bx1, _ in boxes
    ])
    for bx0, _, _, label in boxes:
        d.text((bx0 + 26, py_ + 12), label, font=f_pill, fill=t["pill_text"])

    # -------- terminal (lado direito)
    cx0, cy0, cx1, cy1 = 1500, 130, 2290, 470
    alpha_shape(canvas, lambda dd: (
        dd.rounded_rectangle([cx0, cy0, cx1, cy1], radius=26, fill=t["card_fill"],
                             outline=t["card_border"], width=2),
        dd.line([cx0 + 2, cy0 + 66, cx1 - 2, cy0 + 66], fill=t["card_border"], width=2),
    ))
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        d.ellipse([cx0 + 34 + i * 38, cy0 + 24, cx0 + 52 + i * 38, cy0 + 42], fill=c)

    ty = cy0 + 108
    for line, isprompt in TERM:
        if line == "$":  # cursor piscando (desenhado estático)
            cw = d.textlength("$", font=f_mono)
            d.text((cx0 + 46, ty), "$", font=f_mono, fill=t["accent"])
            d.rectangle([cx0 + 46 + cw + 16, ty + 4, cx0 + 46 + cw + 34, ty + 36], fill=t["accent"])
        else:
            d.text((cx0 + 46, ty), line, font=f_mono, fill=t["accent"] if isprompt else t["term_text"])
        ty += 62

    return canvas


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in THEMES:
        img = build(name)
        out = os.path.join(OUT_DIR, f"banner-{name}.png")
        img.convert("RGB").save(out, "PNG", optimize=True)
        print(f"{out}  {img.size[0]}x{img.size[1]}  {os.path.getsize(out) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
