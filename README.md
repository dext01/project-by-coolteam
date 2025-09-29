
# Генератор комиксов из PDF/текста

Создаёт комикс по загружаемому документу: извлекаем текст из PDF (нативный и через OCR), превращаем его в сценарий, генерируем кадры через **Яндекс.Арт**, добавляем реплики и собираем страницы/ PDF-комикс.

```
Парсер (PyMuPDF + Tesseract OCR)
        ↓
   Gemini (сюжет/сцены и реплики)
        ↓
  Яндекс.Арт (картинки)
        ↓
   Python-сборка (панели → страницы → PDF)
```

## Содержание
- [Возможности](#возможности)
- [Архитектура](#архитектура)
- [Быстрый старт в Colab](#быстрый-старт-в-colab)
- [Локальный запуск](#локальный-запуск)
- [Переменные окружения](#переменные-окружения)
- [Структура проекта](#структура-проекта)
- [Как это работает](#как-это-работает)
- [Параметры и тюнинг](#параметры-и-тюнинг)
- [Советы по демо](#советы-по-демо)
- [Устранение неполадок](#устранение-неполадок)
- [Лицензия и оговорки](#лицензия-и-оговорки)

---

## Возможности
- Поддержка **русскоязычных PDF** (нативный текст + OCR Tesseract).
- Автоматическое формирование **панелей комикса** (описание сцены + реплики).
- Генерация изображений через **Яндекс.Арт** (асинхронная операция API).
- Встраивание текста под панелью, сборка страниц и итогового **PDF**.
- Конфигурируемые **стили** (например, *american comic, colored*).

> ⚠️ Генерацию сюжетов делает внешняя LLM (в коде она представлена функцией `generate_panels`). Подключите свой провайдер (Gemini/иное) внутри этого модуля.

---

## Архитектура

Модули и поток данных:
- `parser.py` — извлекает текст из `pdfres/document.pdf`:
  - `extract_native_text` (PyMuPDF) — нативный текст;
  - `ocr_pdf` (pdf2image + Tesseract) — текст со сканов;
  - `parse_pdf` — объединяет, приоритет у нативного текста;
  - `work()` — сохраняет итог в `output.txt`.
- `generate_panels.py` — превращает сырой текст в список панелей:
  ```python
  [
    {"number": 1, "description": "что в кадре", "text": "реплика/текст"},
    ...
  ]
  ```
- `yandexart.py` — обёртка над **Yandex Art** (imageGenerationAsync → polling → base64 → PIL.Image).
- `add_text.py` — рендерит реплики под изображением.
- `create_strip.py` — собирает 1–6 панелей в одну полоску (страницу).
- Оркестрация (пример в `run_pipeline.py`) — соединяет всё и формирует `output/comics.pdf`.

---

## Быстрый старт в Colab

Минимальный ноутбук (из вашего `parser.ipynb`):

```python
!apt update
!apt install -y tesseract-ocr tesseract-ocr-rus poppler-utils
!pip install pymupdf pytesseract pdf2image pillow

from google.colab import files
uploaded = files.upload()             # загрузите PDF
pdf_path = list(uploaded.keys())[0]

# --- парсинг ---
from parser import parse_pdf
pages = parse_pdf(pdf_path)
full_text = "\n\n".join(pages)
open("output.txt","w",encoding="utf-8").write(full_text)
files.download("output.txt")
```

Далее можно запускать оркестрацию генерации панелей/изображений и сборки PDF прямо в Colab (см. раздел «Локальный запуск» — код идентичен).

---

## Локальный запуск

### 1) Зависимости

- **Системные**: `tesseract-ocr`, `tesseract-ocr-rus`, `poppler-utils`  
  - macOS: `brew install tesseract poppler`  
  - Ubuntu/Debian: `sudo apt install tesseract-ocr tesseract-ocr-rus poppler-utils`  
  - Windows: установите Tesseract и Poppler, пропишите путь в `PATH` (см. [Устранение неполадок](#устранение-неполадок)).

- **Python-пакеты**:
  ```bash
  pip install -r requirements.txt
  ```

  Пример `requirements.txt`:
  ```txt
  pymupdf
  pytesseract
  pdf2image
  pillow
  requests
  ```

### 2) Подготовка данных
```
pdfres/
  └─ document.pdf        # ваш исходный документ
```

### 3) Переменные окружения
См. раздел ниже — требуются ключи для Яндекс.Арт.

### 4) Запуск
```bash
python run_pipeline.py
```
Итоги будут в `output/`: панели `panel-*.png`, страницы `strip-*.png`, финальный `comics.pdf`.

---

## Переменные окружения

Для `yandexart.py` задайте:

```bash
export YANDEX_API_KEY="ваш_api_ключ"
export YANDEX_FOLDER_ID="ваш_folder_id"
```

или создайте `.env` и загрузите переменные через `python-dotenv` (по желанию).  
В коде `yandexart.py` замените плейсхолдеры `YOUR_API_KEY` и `YOUR_FOLDER_ID` на реальные значения, если не используете переменные окружения.

---

## Структура проекта

```
.
├─ pdfres/
│   └─ document.pdf
├─ output/                 # создаётся автоматически
├─ parser.py
├─ generate_panels.py      # ВАЖНО: подключите вашу LLM (Gemini/иное)
├─ yandexart.py
├─ add_text.py
├─ create_strip.py
├─ run_pipeline.py         # оркестрация (пример ниже)
├─ requirements.txt
└─ README.md
```

**Пример `run_pipeline.py` (на базе вашего фрагмента):**
```python
import json, os, shutil
from pathlib import Path
from generate_panels import generate_panels
from yandexart import text_to_image
from add_text import add_text_to_panel
from create_strip import create_strip
from parser import work

def clear_folder_pathlib(folder_path):
    folder = Path(folder_path)
    for p in folder.iterdir():
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)

os.makedirs("output", exist_ok=True)
clear_folder_pathlib("output")

# 1) парсим PDF → output.txt
work()

# 2) читаем сценарий (добавьте персонажей/установки по вкусу)
with open('output.txt', 'r', encoding='utf-8') as f:
    SCENARIO = f.read().strip()

SCENARIO += "\nCharacters: Peter is a tall guy with blond hair. Steven is a small guy with black hair."
STYLE = "american comic, colored"

print(f"Generate panels with style '{STYLE}'")
panels = generate_panels(SCENARIO)
with open('output/panels.json', 'w', encoding='utf-8') as out:
    json.dump(panels, out, ensure_ascii=False, indent=2)

# 3) рендер панелей
panel_images = []
for panel in panels:
    prompt = f"{panel['description']}, cartoon box, {STYLE}"
    img = text_to_image(prompt)             # PIL.Image
    img_with_text = add_text_to_panel(panel["text"], img)
    path = f"output/panel-{panel['number']}.png"
    img_with_text.save(path)
    panel_images.append(img_with_text)

# 4) сборка страниц и PDF
pages = []
for i in range(0, len(panel_images), 6):
    batch = panel_images[i:i+6]
    strip_img = create_strip(batch)
    strip_path = f"output/strip-{i//6 + 1}.png"
    strip_img.save(strip_path)
    pages.append(strip_img)

if pages:
    pages[0].save("output/comics.pdf", "PDF", save_all=True, append_images=pages[1:])
print("PDF создан: output/comics.pdf")
```

---

## Как это работает

1. **Парсер PDF** (`parser.py`)
   - Пытается вытащить нативный текст через `PyMuPDF`.
   - Для сканов рендерит страницы в изображения (`pdf2image`) и прогоняет через `Tesseract` (русский язык).
   - Объединяет результаты: если на странице есть нативный текст — берём его, иначе — OCR.

2. **Генерация панелей** (`generate_panels.py`)
   - Принимает сырой текст (из `output.txt`) и возвращает массив панелей c полями `number`, `description`, `text`.
   - Здесь интегрируется LLM (например, **Gemini**) — продумайте промптинг для качества сцен.

3. **Генерация изображений** (`yandexart.py`)
   - Отправляет запрос `imageGenerationAsync`, опрашивает операцию `/operations/{id}` до готовности.
   - Декодирует `base64` в `PIL.Image`.
   - Поддерживает квадрат/портрет/альбом через `aspectRatio` (упрощённо).

4. **Текст и сборка** (`add_text.py`, `create_strip.py`)
   - Отрисовка реплик под кадром с авто-переносами.
   - Склейка 1–6 панелей в страницу, затем объединение страниц в `comics.pdf`.

---

## Параметры и тюнинг

- **Стиль картинки**: изменяйте переменную `STYLE` (напр. `manga style, b&w`, `retro newspaper`, `pixel art`).
- **Seed**: в `yandexart.py` сид фиксируется при запуске — для воспроизводимости можно захардкодить/передавать параметром.
- **Размеры**: `text_to_image(prompt, width, height)` — управляет соотношением сторон.
- **Батчинг**: число панелей на страницу (`6`) можно менять под ваш формат.
- **Шрифты**: `add_text.py` пытается загрузить `manga-temple.ttf` → `arial.ttf` → системный. Добавьте нужный TTF рядом с кодом.

---

## Советы по демо

- Возьмите **короткий PDF** (1–3 страницы) — быстрее прогон и меньше ожидания.
- Заранее прогоните пайплайн и положите `output/` как fallback.
- Покажите **панели.json** → затем картинки → итоговый PDF — путь преобразования будет нагляден.
- Дайте зрителям выбрать стиль (несколько предустановок).

---

## Устранение неполадок

- **`TesseractNotFoundError` / `pytesseract.pytesseract.TesseractNotFoundError`**  
  Проверьте, что tesseract установен и доступен в `PATH`.  
  Windows: укажите путь вручную в `pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"`.

- **`pdf2image` требует Poppler**  
  Установите `poppler-utils` (Linux/macOS) или скачайте Poppler for Windows и добавьте `bin` в `PATH`.

- **Яндекс.Арт возвращает ошибку/таймаут**  
  Проверьте `YANDEX_API_KEY` и `YANDEX_FOLDER_ID`. Увеличьте `operation_timeout`. Сократите промпт/размер. Учитывайте лимиты квот.

- **Низкое качество/несоответствие картинок**  
  Улучшайте описания сцен в `generate_panels`. Добавляйте контекст: стиль, персонажи, эмоции, композицию.

---

## Лицензия и оговорки

- Код — под вашей лицензией (добавьте `LICENSE`, при необходимости укажите MIT/Apache-2.0 и т.п.).
- Соблюдайте условия использования API Яндекс Облака и выбранной LLM.
- Убедитесь, что исходные PDF не нарушают авторских прав.
