from PIL import Image, ImageDraw, ImageFont
import os
import math
import random

def create_gradient_background(width, height, color1, color2):
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(color1[1:3], 16) + (int(color2[1:3], 16) - int(color1[1:3], 16)) * y // height
        g = int(color1[3:5], 16) + (int(color2[3:5], 16) - int(color1[3:5], 16)) * y // height
        b = int(color1[5:7], 16) + (int(color2[5:7], 16) - int(color1[5:7], 16)) * y // height
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

def add_stars(draw, width, height, count=50):
    random.seed(42)
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=(brightness, brightness, brightness))

def get_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def get_font_bold(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return get_font(size)

def create_phone_screenshot(number, title, subtitle, features):
    width, height = 1080, 1920
    img = create_gradient_background(width, height, '#1a0b2e', '#2d1b4e')
    draw = ImageDraw.Draw(img)
    add_stars(draw, width, height, 80)
    
    font_title = get_font_bold(72)
    font_subtitle = get_font(42)
    font_feature = get_font(38)
    font_number = get_font_bold(120)
    
    draw.text((50, 30), f"#{number}", fill='#f4d35e', font=font_number)
    
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 200), title, fill='#ffffff', font=font_title)
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((width - subtitle_width) // 2, 300), subtitle, fill='#c9a8ff', font=font_subtitle)
    
    draw.line([(width//2 - 100, 380), (width//2 + 100, 380)], fill='#f4d35e', width=4)
    
    y_pos = 480
    icon_colors = ['#f4d35e', '#ff6b6b', '#764abc', '#4ecdc4']
    for i, feature in enumerate(features):
        draw.ellipse([80, y_pos, 140, y_pos+60], fill=icon_colors[i % len(icon_colors)])
        draw.text((170, y_pos+10), feature, fill='#ffffff', font=font_feature)
        y_pos += 100
    
    brand_text = "SeuFuturo Horóscopo"
    brand_bbox = draw.textbbox((0, 0), brand_text, font=font_subtitle)
    brand_width = brand_bbox[2] - brand_bbox[0]
    draw.text(((width - brand_width) // 2, height - 150), brand_text, fill='#f4d35e', font=font_subtitle)
    
    return img

def create_tablet_screenshot(number, title, subtitle, features, is_10inch=False):
    if is_10inch:
        width, height = 2560, 1600
    else:
        width, height = 1600, 900
    
    img = create_gradient_background(width, height, '#1a0b2e', '#2d1b4e')
    draw = ImageDraw.Draw(img)
    add_stars(draw, width, height, 100)
    
    font_title = get_font_bold(80)
    font_subtitle = get_font(48)
    font_feature = get_font(42)
    font_number = get_font_bold(140)
    
    draw.text((50, 30), f"#{number}", fill='#f4d35e', font=font_number)
    
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 150), title, fill='#ffffff', font=font_title)
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((width - subtitle_width) // 2, 260), subtitle, fill='#c9a8ff', font=font_subtitle)
    
    y_pos = 380
    col_width = width // 3
    icon_colors = ['#f4d35e', '#ff6b6b', '#764abc', '#4ecdc4']
    for i, feature in enumerate(features):
        col = i % 3
        row = i // 3
        x_pos = col * col_width + 80
        y_feat = 380 + row * 120
        draw.ellipse([x_pos, y_feat, x_pos+70, y_feat+70], fill=icon_colors[i % len(icon_colors)])
        draw.text((x_pos+90, y_feat+15), feature, fill='#ffffff', font=font_feature)
    
    brand_text = "SeuFuturo Horóscopo"
    brand_bbox = draw.textbbox((0, 0), brand_text, font=font_subtitle)
    brand_width = brand_bbox[2] - brand_bbox[0]
    draw.text(((width - brand_width) // 2, height - 120), brand_text, fill='#f4d35e', font=font_subtitle)
    
    return img

def create_chromebook_screenshot(number, title, subtitle, features):
    width, height = 1920, 1080
    
    img = create_gradient_background(width, height, '#1a0b2e', '#2d1b4e')
    draw = ImageDraw.Draw(img)
    add_stars(draw, width, height, 80)
    
    font_title = get_font_bold(72)
    font_subtitle = get_font(44)
    font_feature = get_font(40)
    font_number = get_font_bold(130)
    
    draw.text((50, 30), f"#{number}", fill='#f4d35e', font=font_number)
    
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 140), title, fill='#ffffff', font=font_title)
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((width - subtitle_width) // 2, 240), subtitle, fill='#c9a8ff', font=font_subtitle)
    
    y_positions = [380, 540, 380, 540]
    x_positions = [100, 100, width//2, width//2]
    icon_colors = ['#f4d35e', '#ff6b6b', '#764abc', '#4ecdc4']
    
    for i, feature in enumerate(features[:4]):
        x_pos = x_positions[i]
        y_pos = y_positions[i]
        draw.ellipse([x_pos, y_pos, x_pos+65, y_pos+65], fill=icon_colors[i % len(icon_colors)])
        draw.text((x_pos+80, y_pos+12), feature, fill='#ffffff', font=font_feature)
    
    brand_text = "SeuFuturo Horóscopo"
    brand_bbox = draw.textbbox((0, 0), brand_text, font=font_subtitle)
    brand_width = brand_bbox[2] - brand_bbox[0]
    draw.text(((width - brand_width) // 2, height - 110), brand_text, fill='#f4d35e', font=font_subtitle)
    
    return img

def create_app_icon(size):
    img = Image.new('RGB', (size, size), '#1a0b2e')
    draw = ImageDraw.Draw(img)
    
    gradient_img = Image.new('RGB', (size, size), '#764abc')
    gradient_draw = ImageDraw.Draw(gradient_img)
    for y in range(size):
        ratio = y / size
        r = int(118 + (45 - 118) * ratio)
        g = int(74 + (11 - 74) * ratio)
        b = int(188 + (46 - 188) * ratio)
        gradient_draw.line([(0, y), (size, y)], fill=(r, g, b))
    
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    margin = size // 8
    mask_draw.ellipse([margin, margin, size-margin, size-margin], fill=255)
    
    gradient_img.putalpha(mask)
    img.paste(gradient_img, (0, 0), gradient_img)
    
    draw = ImageDraw.Draw(img)
    center = size // 2
    star_size = size // 3
    
    draw.ellipse([center-star_size, center-star_size, center+star_size, center+star_size], 
                 fill='#f4d35e', outline='#ffffff', width=max(3, size//100))
    
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = star_size if i % 2 == 0 else star_size * 0.5
        x = center + radius * math.cos(angle)
        y = center - radius * math.sin(angle)
        points.append((x, y))
    
    draw.polygon(points, fill='#1a0b2e')
    
    small_star_positions = [
        (center, center - star_size - 40),
        (center, center + star_size + 40),
        (center - star_size - 40, center),
        (center + star_size + 40, center)
    ]
    
    for sx, sy in small_star_positions:
        s_size = star_size // 4
        s_points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            radius = s_size if i % 2 == 0 else s_size * 0.5
            x = sx + radius * math.cos(angle)
            y = sy - radius * math.sin(angle)
            s_points.append((x, y))
        draw.polygon(s_points, fill='#f4d35e')
    
    return img

# Dados das screenshots
phone_screenshots = [
    {"title": "Horóscopo Diário", "subtitle": "Previsões personalizadas todos os dias", "features": ["Amor, carreira e saúde", "Atualizações diárias", "Notificações personalizadas", "Leitura completa do dia"]},
    {"title": "Mapa Astral Completo", "subtitle": "Descubra seu potencial cósmico", "features": ["Posição dos planetas", "Casas astrológicas", "Aspectos planetários", "Interpretação detalhada"]},
    {"title": "Compatibilidade Amorosa", "subtitle": "Sinastria entre signos", "features": ["Análise de relacionamento", "Pontos de harmonia", "Desafios a superar", "Potencial romântico"]},
    {"title": "Tarô e Oráculos", "subtitle": "Conselhos imediatos", "features": ["Tiragens virtuais", "Múltiplos baralhos", "Interpretações profundas", "Salve suas leituras"]},
    {"title": "Fases da Lua", "subtitle": "Acompanhe os ciclos lunares", "features": ["Lua atual em tempo real", "Próximas fases", "Influência no seu signo", "Calendário lunar"]},
    {"title": "Previsões Mensais", "subtitle": "Planeje seu futuro", "features": ["Melhores períodos", "Alertas importantes", "Dicas por área da vida", "Relatório completo"]}
]

tablet_screenshots = [
    {"title": "Dashboard Completo", "subtitle": "Todas as ferramentas em um só lugar", "features": ["Visão geral do dia", "Acesso rápido", "Widgets personalizados", "Navegação intuitiva"]},
    {"title": "Mapa Astral Detalhado", "subtitle": "Visualização ampliada", "features": ["Gráfico completo", "Zoom nos detalhes", "Tabelas explicativas", "Exportar relatório"]},
    {"title": "Comparação de Signos", "subtitle": "Análise lado a lado", "features": ["Dois mapas simultâneos", "Aspectos destacados", "Porcentagem de compatibilidade", "Dicas de relacionamento"]},
    {"title": "Histórico de Leituras", "subtitle": "Acompanhe sua evolução", "features": ["Todas as tiragens salvas", "Busca por data", "Estatísticas pessoais", "Exportar dados"]}
]

chromebook_screenshots = [
    {"title": "Experiência Desktop", "subtitle": "Otimizado para telas grandes", "features": ["Layout responsivo", "Múltiplas janelas", "Atalhos de teclado", "Modo tela cheia"]},
    {"title": "Análises Profundas", "subtitle": "Conteúdo expandido", "features": ["Relatórios completos", "Gráficos interativos", "Comparativos avançados", "Exportação PDF"]},
    {"title": "Sincronização Total", "subtitle": "Seus dados em qualquer dispositivo", "features": ["Cloud backup", "Acesso multi-dispositivo", "Sincronização automática", "Segurança garantida"]},
    {"title": "Comunidade SeuFuturo", "subtitle": "Conecte-se com outros usuários", "features": ["Fóruns de discussão", "Compartilhar leituras", "Eventos ao vivo", "Conteúdo exclusivo"]}
]

print("Gerando ícones...")
icon_512 = create_app_icon(512)
icon_512.save('/workspace/store/assets/app-icon-playstore-512.png', 'PNG')
print("  OK Ícone 512x512 criado")

icon_1024 = create_app_icon(1024)
icon_1024.save('/workspace/store/assets/app-icon-playstore-1024.png', 'PNG')
print("  OK Ícone 1024x1024 criado")

print("\nGerando recurso gráfico...")
feature_graphic = create_gradient_background(1024, 500, '#1a0b2e', '#2d1b4e')
draw = ImageDraw.Draw(feature_graphic)
add_stars(draw, 1024, 500, 40)

font_fg_title = get_font_bold(72)
font_fg_subtitle = get_font(36)

fg_title = "SeuFuturo Horóscopo"
fg_title_bbox = draw.textbbox((0, 0), fg_title, font=font_fg_title)
fg_title_width = fg_title_bbox[2] - fg_title_bbox[0]
draw.text(((1024 - fg_title_width) // 2, 180), fg_title, fill='#ffffff', font=font_fg_title)

fg_subtitle = "Seu guia diário de astrologia"
fg_subtitle_bbox = draw.textbbox((0, 0), fg_subtitle, font=font_fg_subtitle)
fg_subtitle_width = fg_subtitle_bbox[2] - fg_subtitle_bbox[0]
draw.text(((1024 - fg_subtitle_width) // 2, 270), fg_subtitle, fill='#f4d35e', font=font_fg_subtitle)

draw.ellipse([850, 50, 950, 150], fill='#764abc', outline='#f4d35e', width=3)
draw.ellipse([50, 350, 150, 450], fill='#ff6b6b', outline='#f4d35e', width=3)

feature_graphic.save('/workspace/store/assets/feature-graphic-1024x500.png', 'PNG')
print("  OK Recurso gráfico 1024x500 criado")

print("\nGerando screenshots do telefone (1080x1920)...")
for i, screen in enumerate(phone_screenshots, 1):
    img = create_phone_screenshot(i, screen["title"], screen["subtitle"], screen["features"])
    img.save(f'/workspace/store/assets/screenshots/phone/screenshot_{i}.png', 'PNG')
    print(f"  OK Telefone #{i}: {screen['title']}")

print("\nGerando screenshots do tablet 7 (1600x900)...")
for i, screen in enumerate(tablet_screenshots[:4], 1):
    img = create_tablet_screenshot(i, screen["title"], screen["subtitle"], screen["features"], is_10inch=False)
    img.save(f'/workspace/store/assets/screenshots/tablet-7/screenshot_{i}.png', 'PNG')
    print(f"  OK Tablet 7 #{i}: {screen['title']}")

print("\nGerando screenshots do tablet 10 (2560x1600)...")
for i, screen in enumerate(tablet_screenshots[:4], 1):
    img = create_tablet_screenshot(i, screen["title"], screen["subtitle"], screen["features"], is_10inch=True)
    img.save(f'/workspace/store/assets/screenshots/tablet-10/screenshot_{i}.png', 'PNG')
    print(f"  OK Tablet 10 #{i}: {screen['title']}")

print("\nGerando screenshots do Chromebook (1920x1080)...")
for i, screen in enumerate(chromebook_screenshots, 1):
    img = create_chromebook_screenshot(i, screen["title"], screen["subtitle"], screen["features"])
    img.save(f'/workspace/store/assets/screenshots/chromebook/screenshot_{i}.png', 'PNG')
    print(f"  OK Chromebook #{i}: {screen['title']}")

print("\nTodos os elementos gráficos foram gerados com sucesso!")
print("\nResumo:")
print("  - Ícones: 512x512 e 1024x1024 pixels")
print("  - Recurso gráfico: 1024x500 pixels")
print("  - Telefone: 6 screenshots (1080x1920)")
print("  - Tablet 7: 4 screenshots (1600x900)")
print("  - Tablet 10: 4 screenshots (2560x1600)")
print("  - Chromebook: 4 screenshots (1920x1080)")
