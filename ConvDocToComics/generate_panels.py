
import re

import requests

template = """
You are a professional comic book creator. Your task is to turn a boring document into an interesting story that illustrates the content of the document.
You need to:
create a story so that it is holistically correct, detailed, and actually consistent with the document.
come up with characters that will fit well into the story.

Next, you need to divide the story into several parts so that each part fits on one page of 6 pictures. I repeat: the story is divided into n equal parts, each of these parts is divided into exactly 6 frames.
Each frame will be a separate cartoon panel.
For each cartoon panel, you:
- Describe the characters on that panel each time.
 - you describe the background of the panel.
The description should consist only of a word or a group of words separated by a comma, without a sentence.
Always use character descriptions instead of their names in the description of the cartoon panel.
You can't use the same description twice.
You will also write the text for the panel.

Important rule: For each panel, create ONE general description that applies to all characters and the background in a single instance. 
Do not provide a description for each character separately.
MAKE WITHOUT PAGES
The text should consist of no more than two small sentences.
Each sentence must begin with the character's name.

Input example:
Characters: Adrian is a blond guy with glasses. Vincent is a black-haired guy with a hat.
Adrian and Vincent want to launch a new product, and they create it overnight before presenting it to the board of directors.

Example output:

# Panel 1
description: 2 guys, a blond hair guy wearing glasses, a dark hair guy wearing hat, sitting at the office, with computers
text:
```
Vincent: I think Generative AI are the future of the company.
Adrien: Let's create a new product with it.
```
# end


Short Scenario:
{scenario}

"""


def generate_panels(scenario):
    """Генерирует комикс панели на основе сценария"""

    BASE_URL = "https://mywebservice-q40s.onrender.com"

    # Правильное формирование промпта
    prompt = template.format(scenario=scenario)

    try:
        print("Sending request to API...")
        response = requests.get(f"{BASE_URL}/flash", params={"prompt": prompt}, timeout=120)

        if response.status_code == 200:
            data = response.json()
            result_content = data["response"]

            print("API Response received:")
            print("=" * 50)
            print(result_content)
            print("=" * 50)

            panels = extract_panel_info(result_content)

            # Проверяем результат
            if panels:
                print(f"Successfully extracted {len(panels)} panels")
                for panel in panels:
                    print(f"Panel {panel['number']}: {panel['description'][:50]}...")
            else:
                print("No panels were extracted from the response")

            return panels

        else:
            print(f"API Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("Error: Request timed out after 120 seconds")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the API server")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def extract_panel_info(text):
    """Извлекает информацию о панелях из текста ответа"""

    panel_info_list = []

    # Удаляем лишние пробелы в начале и конце
    text = text.strip()

    # Ищем все панели с помощью регулярного выражения
    # Этот шаблон ищет структуру: # Panel X, затем description, затем text между ```
    panel_pattern = r'# Panel\s*(\d+)\s*description:\s*(.*?)\s*text:\s*```\s*(.*?)\s*```'

    matches = re.findall(panel_pattern, text, re.DOTALL | re.IGNORECASE)

    print(f"Found {len(matches)} panels using regex pattern")

    for match in matches:
        panel_number, description, text_content = match

        # Очищаем текст от лишних пробелов
        description = description.strip()
        text_content = text_content.strip()

        # Удаляем возможные префиксы "end" если они есть
        description = re.sub(r'^end\s*', '', description, flags=re.IGNORECASE)
        text_content = re.sub(r'^end\s*', '', text_content, flags=re.IGNORECASE)

        panel_info = {
            'number': panel_number.strip(),
            'description': description,
            'text': text_content
        }

        panel_info_list.append(panel_info)

    # Если регулярное выражение не сработало, пробуем альтернативный метод
    if not panel_info_list:
        print("Trying alternative parsing method...")
        panel_info_list = alternative_parse_panels(text)

    # Сортируем панели по номеру
    panel_info_list.sort(key=lambda x: int(x['number']))

    return panel_info_list


def alternative_parse_panels(text):
    """Альтернативный метод парсинга панелей"""

    panel_info_list = []

    # Разделяем текст по разделителю панелей
    panels_raw = re.split(r'# Panel\s*\d+', text)

    # Первый элемент обычно пустой или содержит текст до первой панели
    for i, panel_block in enumerate(panels_raw[1:], 1):
        if not panel_block.strip():
            continue

        panel_info = {'number': str(i)}

        # Ищем description
        desc_match = re.search(r'description:\s*(.*?)(?=text:|$)', panel_block, re.DOTALL | re.IGNORECASE)
        if desc_match:
            panel_info['description'] = desc_match.group(1).strip()
        else:
            panel_info['description'] = "Description not found"

        # Ищем text
        text_match = re.search(r'text:\s*```\s*(.*?)\s*```', panel_block, re.DOTALL)
        if text_match:
            panel_info['text'] = text_match.group(1).strip()
        else:
            # Пробуем найти текст без ```
            text_match_alt = re.search(r'text:\s*(.*?)(?=# Panel|$)', panel_block, re.DOTALL | re.IGNORECASE)
            if text_match_alt:
                panel_info['text'] = text_match_alt.group(1).strip()
            else:
                panel_info['text'] = "Text not found"

        panel_info_list.append(panel_info)

    return panel_info_list


def print_panels_debug(panels):
    """Выводит отладочную информацию о панелях"""

    if not panels:
        print("No panels to display")
        return

    print("\n" + "=" * 60)
    print("EXTRACTED PANELS DEBUG INFO")
    print("=" * 60)

    for panel in panels:
        print(f"\n--- Panel {panel['number']} ---")
        print(f"Description: {panel['description']}")
        print(f"Text: {panel['text']}")
        print("-" * 40)