from PIL import Image, ImageDraw, ImageFont


def add_text_to_panel(text, panel_image):
    """Добавляет текст к панели комикса"""
    text_image = generate_text_image(text)

    # Создаем новое изображение, объединяющее панель и текст
    result_image = Image.new('RGB',
                             (panel_image.width, panel_image.height + text_image.height),
                             color='white')

    # Вставляем панель
    result_image.paste(panel_image, (0, 0))
    # Вставляем текст под панелью
    result_image.paste(text_image, (0, panel_image.height))

    return result_image


def generate_text_image(text):
    """Генерирует изображение с текстом для панели комикса"""
    # Размеры изображения
    width = 1024
    height = 200  # Увеличиваем высоту для многострочного текста

    # Создаем белое изображение
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    try:
        # Загружаем шрифт
        font = ImageFont.truetype(font="manga-temple.ttf", size=24)
    except:
        # Если шрифт не найден, используем стандартный
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

    # Разделяем текст на строки
    lines = text.strip().split('\n')

    # Рассчитываем высоту всего текстового блока
    total_height = 0
    line_heights = []

    for line in lines:
        bbox = draw.textbbox((0, 0), line.strip(), font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_height += line_height + 5  # +5 для межстрочного интервала

    # Начальная позиция Y для центрирования
    y = (height - total_height) // 2

    # Рисуем каждую строку
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Получаем размеры текущей строки
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]

        # Центрируем строку по горизонтали
        x = (width - line_width) // 2

        # Рисуем текст
        draw.text((x, y), line, fill='black', font=font)

        # Переходим к следующей строке
        y += line_heights[i] + 5

    return image