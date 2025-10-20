import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def draw_chart(planets):
    try:
        # 🔧 Template path'i mutlak olarak belirt
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "chart_template.png")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template bulunamadı: {template_path}")

        # 🔹 Template görselini aç
        base_image = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(base_image)

        # 🔹 Her gezegen için pozisyon noktaları çiz
        center_x, center_y = base_image.size[0] // 2, base_image.size[1] // 2
        radius = min(center_x, center_y) - 40

        for planet in planets:
            angle_deg = planet["ecliptic_long"]
            angle_rad = (angle_deg - 90) * 3.14159 / 180
            x = center_x + radius * 0.9 * (1.0 * cos(angle_rad))
            y = center_y + radius * 0.9 * (1.0 * sin(angle_rad))
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="yellow", outline="black")
            draw.text((x + 10, y - 10), planet["name"], fill="white")

        # 🔹 PNG olarak buffer’a yaz
        output = BytesIO()
        base_image.save(output, format="PNG")
        output.seek(0)
        return output

    except Exception as e:
        print(f"[draw_chart] ⚠️ Hata oluştu: {e}")
        return None


# 🔹 Sin, cos importlarını unutma
from math import sin, cos
