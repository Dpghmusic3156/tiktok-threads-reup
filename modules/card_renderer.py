"""Card Rendering & Visual Overlay Module."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


def render_card_overlay(
    card_path: Path,
    output_path: Path,
    label: str = "",
    width: int = 1080,
    height: int = 1920,
    scale_w: float = 0.92,
    radius: int = 24,
    shadow_blur: int = 24,
    shadow_alpha: int = 140,
    shadow_offset_y: int = 12,
    vertical_ratio: float = 0.42,
    font_path: Path | None = None
) -> Path:
    """Render a single high-definition Threads card with rounded corners, drop shadow, and index label."""
    with Image.open(card_path) as src:
        card_raw = src.convert("RGBA")
        
    target_w = round(width * scale_w)
    
    # 1. Apply rounded corner mask to source card
    mask = Image.new("L", (card_raw.width * 2, card_raw.height * 2), 0)
    draw_m = ImageDraw.Draw(mask)
    draw_m.rounded_rectangle((0, 0, mask.width - 1, mask.height - 1), radius=radius * 2, fill=255)
    mask = mask.resize(card_raw.size, Image.Resampling.LANCZOS)
    
    card_rounded = card_raw.copy()
    orig_a = card_rounded.getchannel("A")
    card_rounded.putalpha(ImageChops.multiply(mask, orig_a))
    
    # 2. Scale to target width while keeping aspect ratio
    target_h = round(card_rounded.height * target_w / card_raw.width)
    card_scaled = card_rounded.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 3. Create canvas and soft drop-shadow
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    card_x = (width - target_w) // 2
    card_y = round((height - target_h) * vertical_ratio)
    
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle(
        (card_x, card_y + shadow_offset_y, card_x + target_w, card_y + target_h + shadow_offset_y),
        radius=radius,
        fill=(0, 0, 0, shadow_alpha)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(card_scaled, (card_x, card_y))
    
    # 4. Optional pagination label (e.g. '01 / 05')
    if label:
        draw_c = ImageDraw.Draw(canvas)
        if font_path and font_path.is_file():
            font_ind = ImageFont.truetype(str(font_path), 32)
        else:
            font_ind = ImageFont.load_default()
        draw_c.text((card_x + 8, height - 90), label, font=font_ind, fill=(255, 255, 255, 190))
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    return output_path


def batch_render_overlays(
    cards_config: list[dict],
    output_dir: Path,
    width: int = 1080,
    height: int = 1920,
    font_path: Path | None = None
) -> list[Path]:
    """Batch render a list of cards into full 1080x1920 overlays."""
    rendered_overlays = []
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for c in cards_config:
        card_file = Path(c["card_file"])
        out_file = output_dir / f"overlay_card_{c['id']}.png"
        label = c.get("label", "")
        scale_w = c.get("scale_w", 0.92)
        
        render_card_overlay(
            card_path=card_file,
            output_path=out_file,
            label=label,
            width=width,
            height=height,
            scale_w=scale_w,
            font_path=font_path
        )
        rendered_overlays.append(out_file)
        print(f"  [OK] Rendered overlay {c['id']}: {out_file.name}")
        
    return rendered_overlays


def render_stacked_card_overlays(
    comment_paths: list[Path],
    output_dir: Path,
    width: int = 1080,
    height: int = 1920,
    scale_w: float = 0.92,
    radius: int = 24,
    shadow_blur: int = 24,
    shadow_alpha: int = 130,
    shadow_offset_y: int = 12,
    gap: int = 28
) -> list[Path]:
    """Render progressive stacked comment overlays (e.g. comment 1, then 1+2, then 1+2+3).
    
    Guarantees:
    - Zero bleed of old background between cards (pure transparent gaps)
    - Consistent anchor positions so earlier comments never jitter or shift when new comments appear
    - Individual rounded corners and soft drop shadows per comment
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    target_w = round(width * scale_w)
    card_x = (width - target_w) // 2
    
    # 1. Prepare rounded & scaled comment cards
    prepared_cards: list[Image.Image] = []
    for cp in comment_paths:
        with Image.open(cp) as src:
            im = src.convert("RGBA")
        
        # Round corners
        mask = Image.new("L", (im.width * 2, im.height * 2), 0)
        d = ImageDraw.Draw(mask)
        d.rounded_rectangle((0, 0, mask.width - 1, mask.height - 1), radius=radius * 2, fill=255)
        mask = mask.resize(im.size, Image.Resampling.LANCZOS)
        im.putalpha(mask)
        
        target_h = round(im.height * target_w / im.width)
        scaled = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        prepared_cards.append(scaled)
        
    # 2. Compute fixed vertical positions based on full stack
    total_h = sum(c.height for c in prepared_cards) + gap * (len(prepared_cards) - 1)
    base_y = (height - total_h) // 2
    
    card_positions = []
    curr_y = base_y
    for c in prepared_cards:
        card_positions.append(curr_y)
        curr_y += c.height + gap
        
    # 3. Render progressive steps (1 card, 1+2 cards, ..., 1+2+N cards)
    result_paths = []
    for step in range(1, len(prepared_cards) + 1):
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        
        # Draw shadows for all active cards in current step
        for idx in range(step):
            c = prepared_cards[idx]
            y_pos = card_positions[idx]
            s_draw.rounded_rectangle(
                (card_x, y_pos + shadow_offset_y, card_x + target_w, y_pos + c.height + shadow_offset_y),
                radius=radius,
                fill=(0, 0, 0, shadow_alpha)
            )
        shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        canvas.alpha_composite(shadow)
        
        # Composite active cards
        for idx in range(step):
            c = prepared_cards[idx]
            y_pos = card_positions[idx]
            canvas.alpha_composite(c, (card_x, y_pos))
            
        out_p = output_dir / f"overlay_stack_step_{step}.png"
        canvas.save(out_p)
        result_paths.append(out_p)
        print(f"  [OK] Rendered stack step {step}/{len(prepared_cards)}: {out_p.name}")
        
    return result_paths
