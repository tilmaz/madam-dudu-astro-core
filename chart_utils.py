    # --- LEJAND (ASPECT AÇIKLAMALARI, EN ALTA VE %50 KÜÇÜK) ---
    legend = [
        ("Conjunction", "#FFD400"),
        ("Sextile", "#1DB954"),
        ("Square", "#E63946"),
        ("Trine", "#1E88E5"),
        ("Opposition", "#7B1FA2"),
    ]

    # Yazı boyutunu %50 küçült
    try:
        legend_font_size = max(12, int(small_font.size * 0.5))
        legend_font = ImageFont.truetype(font_text, legend_font_size)
    except Exception:
        legend_font = ImageFont.load_default()

    # Sayfanın en altına hizala
    yL = bg.height - 50
    xL = 50
    spacing = 180

    for i, (label, col) in enumerate(legend):
        lx = xL + i * spacing
        # Küçük renk kutusu
        draw.rectangle([lx, yL + 8, lx + 18, yL + 18], fill=col)
        # Etiket yazısı
        draw.text((lx + 26, yL + 2), label, fill=col, font=legend_font)

    logging.info("✅ Legend açıklamaları alt hizalı ve küçültülmüş olarak çizildi.")
