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
    """Генерирует изображение с текстом для панели комикса с автоматическим переносом"""
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

    # Параметры для текста
    side_padding = 50  # Отступы слева и справа
    line_spacing = 5  # Межстрочный интервал
    max_width = width - 2 * side_padding

    # Функция для разделения текста на строки с переносом
    def split_text_into_lines(text, font, max_width):
        lines = []
        words = text.split()
        current_line = []

        for word in words:
            # Проверяем ширину текущей линии с добавленным словом
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    # Обрабатываем исходный текст (учитываем уже существующие переносы)
    processed_lines = []
    original_lines = text.strip().split('\n')

    for line in original_lines:
        line = line.strip()
        if not line:
            continue

        # Если строка слишком длинная, разбиваем ее
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]

        if line_width > max_width:
            # Разбиваем длинную строку на несколько
            wrapped_lines = split_text_into_lines(line, font, max_width)
            processed_lines.extend(wrapped_lines)
        else:
            processed_lines.append(line)

    # Рассчитываем высоту всего текстового блока
    total_height = 0
    line_heights = []

    for line in processed_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_height += line_height + line_spacing

    # Убираем последний межстрочный интервал
    total_height -= line_spacing

    # Начальная позиция Y для центрирования
    y = (height - total_height) // 2
    if y < 10:  # Если текст не помещается по высоте, начинаем сверху
        y = 10

    # Рисуем каждую строку
    for i, line in enumerate(processed_lines):
        # Получаем размеры текущей строки
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]

        # Центрируем строку по горизонтали
        x = side_padding + (max_width - line_width) // 2

        # Рисуем текст
        draw.text((x, y), line, fill='black', font=font)

        # Переходим к следующей строке
        y += line_heights[i] + line_spacing

    return image