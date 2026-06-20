from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter


def _hex_to_rgb(value: str) -> Tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        return (249, 250, 251)
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class CardRenderer:
    def render(
        self,
        background_path: Path,
        output_path: Path,
        index: int,
        total: int,
        title: str,
        headline: str,
        body: str,
        palette: List[str],
        brand_name: str,
    ) -> Path:
        image = Image.open(background_path).convert("RGB").resize((1080, 1350))
        image = image.filter(ImageFilter.GaussianBlur(radius=0.2))

        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        dark = _hex_to_rgb(palette[0] if palette else "#111827")
        accent = _hex_to_rgb(palette[1] if len(palette) > 1 else "#F97316")
        light = _hex_to_rgb(palette[2] if len(palette) > 2 else "#F9FAFB")

        draw.rectangle((0, 0, 1080, 1350), fill=(*dark, 98))
        draw.rounded_rectangle((58, 760, 1022, 1236), radius=42, fill=(*dark, 214))
        draw.rectangle((58, 0, 72, 1350), fill=(*accent, 255))
        draw.rounded_rectangle((812, 76, 1018, 140), radius=28, fill=(*accent, 235))

        image = Image.alpha_composite(image.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(image)

        title_font = _font(34, bold=True)
        index_font = _font(34, bold=True)
        headline_font = _font(72, bold=True)
        body_font = _font(39, bold=False)
        brand_font = _font(28, bold=True)

        draw.text((92, 82), title[:42], font=title_font, fill=(*light, 235))
        draw.text((850, 91), f"{index:02d}/{total:02d}", font=index_font, fill=(*dark, 255))

        headline_lines = _wrap_text(draw, headline, headline_font, 840)
        if len(headline_lines) > 3:
            headline_lines = headline_lines[:3]
            headline_lines[-1] = headline_lines[-1].rstrip(".,;:") + "..."

        y = 812
        for line in headline_lines:
            draw.text((104, y), line, font=headline_font, fill=(*light, 255))
            y += 82

        y += 18
        body_lines = _wrap_text(draw, body, body_font, 820)
        if len(body_lines) > 4:
            body_lines = body_lines[:4]
            body_lines[-1] = body_lines[-1].rstrip(".,;:") + "..."

        for line in body_lines:
            draw.text((106, y), line, font=body_font, fill=(*light, 232))
            y += 50

        if brand_name:
            draw.text((104, 1264), brand_name[:34], font=brand_font, fill=(*accent, 255))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(output_path, quality=95)
        return output_path
