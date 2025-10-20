import os
from io import BytesIO
from math import sin, cos, radians
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


def draw_chart(planets):
    try:
        # 🔧 Template path'i tam belirle
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "chart_template.png")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template bulunamadı: {template_path}")

        # 🔹 Template görselini aç
        base_image = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(base_image)

        # 🔹 Görsel merkez ve daire yarıçapını belirle
        center_x, center_y = base_image.size[0] // 2, base_image.size[1] // 2
        radius = min(center_x, center_y) - 60

        # 🔹 Font ayarla (fallback: default)
        try:
            font_path = os.path.join(base_dir, "AstroGadget.ttf")
            font = ImageFont.truetype(font_path, 16)
        except Exception:
            font = ImageFont.load_default()

        # 🔹 Her gezegen için noktaları çiz
        for planet in planets:
            angle_deg = float(planet["ecliptic_long"])
            angle_rad = radians(angle_deg - 90)  # 0° Koç burcu (sağdan başlasın)
            x = center_x + radius * cos(angle_rad)
            y = center_y + radius * sin(angle_rad)

            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill="yellow", outline="black", width=2)
            draw.text((x + 10, y - 10), planet["name"], fill="white", font=font)

        # 🔹 Çıktı klasörünü hazırla
        charts_dir = os.path.join(base_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)

        # 🔹 Dosya adı oluştur
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = os.path.join(charts_dir, filename)
        base_image.save(file_path, format="PNG")

        # 🔹 URL oluştur (Render için)
        chart_url = f"https://madam-dudu-astro-core-1.onrender.com/charts/{filename}"

        print(f"[draw_chart] ✅ Chart created: {chart_url}")
        return {"chart_url": chart_url}

    except Exception as e:
        print(f"[draw_chart] ⚠️ Hata oluştu: {e}")
        return {"error": str(e)}
