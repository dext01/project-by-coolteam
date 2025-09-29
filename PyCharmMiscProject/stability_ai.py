import io
import os
import warnings
import random
import requests
import base64
import time
from PIL import Image

# Настройки Яндекс Арт
YANDEX_API_KEY = "AQVN0Ue86BCv7kA3CyK1oCsEDWy-uJdopl-w1eTh"  # Замени на свой API ключ
YANDEX_FOLDER_ID = "b1guk8a9hg741ssab6ba"  # Замени на свой folder-id

seed = random.randint(0, 1000000000)


def yandex_art_request(prompt, seed, width=1024, height=1024, operation_timeout=300):
    """
    Функция для генерации изображения через Яндекс Арт
    """
    # Определяем соотношение сторон
    aspect_ratio = {
        "widthRatio": "1",
        "heightRatio": "1"
    }

    # Для не квадратных изображений можно настроить другие соотношения
    if width != height:
        if width > height:
            aspect_ratio = {"widthRatio": "16", "heightRatio": "9"}
        else:
            aspect_ratio = {"widthRatio": "9", "heightRatio": "16"}

    request_data = {
        "modelUri": f"art://{YANDEX_FOLDER_ID}/yandex-art/latest",
        "generationOptions": {
            "seed": seed,
            "aspectRatio": aspect_ratio
        },
        "messages": [
            {
                "weight": 1,
                "text": prompt
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "x-folder-id": YANDEX_FOLDER_ID
    }

    try:
        # Создаем запрос на генерацию
        create_request = requests.post(
            'https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync',
            headers=headers,
            json=request_data
        )

        # Проверяем успешность запроса
        if create_request.status_code != 200:
            print(f"Ошибка создания запроса: {create_request.status_code}")
            print(create_request.text)
            return None

        operation_id = create_request.json()["id"]
        print(f"Запущена генерация. Operation ID: {operation_id}")

        # Проверяем статус операции с таймаутом
        start_time = time.time()
        while time.time() - start_time < operation_timeout:
            time.sleep(5)
            done_request = requests.get(
                f'https://llm.api.cloud.yandex.net/operations/{operation_id}',
                headers=headers
            )

            if done_request.status_code != 200:
                print(f"Ошибка проверки статуса: {done_request.status_code}")
                continue

            operation_data = done_request.json()

            if operation_data.get('done') == True:
                if 'response' in operation_data and 'image' in operation_data['response']:
                    # Декодируем изображение и возвращаем как PIL Image
                    image_data = base64.b64decode(operation_data['response']['image'])
                    return Image.open(io.BytesIO(image_data))
                else:
                    print("Ошибка: изображение не получено в ответе")
                    print(operation_data)
                    return None

        print("Таймаут ожидания генерации изображения")
        return None

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


def text_to_image(prompt, width=1024, height=1024):
    """
    Генерация изображения по текстовому описанию
    """
    print(f"Генерация изображения: {prompt}")
    img = yandex_art_request(prompt, seed, width, height)

    if img is None:
        warnings.warn("Не удалось сгенерировать изображение. Пожалуйста, попробуйте другой промпт.")

    return img


def edit_image(input_image_path, prompt, output_image_name, strength=0.6):
    """
    Функция для редактирования изображения
    ВАЖНО: Яндекс Арт не поддерживает прямое редактирование изображений как Stability AI.
    Эта функция создает новое изображение на основе промпта.
    """
    print(f"Создание изображения на основе: {prompt}")

    # Генерируем новое изображение на основе промпта
    img = yandex_art_request(prompt, seed, 512, 512)

    if img is not None:
        # Сохраняем результат
        output_path = f"{output_image_name}.png"
        img.save(output_path)
        print(f"Изображение сохранено как: {output_path}")
        return img
    else:
        warnings.warn("Не удалось создать изображение. Пожалуйста, попробуйте другой промпт.")
        return None


def save_image(image, filename):
    """
    Вспомогательная функция для сохранения изображения
    """
    if image:
        image.save(filename)
        print(f"Изображение сохранено как: {filename}")
        return True
    return False


# Пример использования
