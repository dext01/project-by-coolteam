import requests
import base64
import time

def yandex_art_request(prompt, seed):
    # Используем другое имя для данных запроса
    request_data = {
        "modelUri": "art://b1guk8a9hg741ssab6ba/yandex-art/latest",
        "generationOptions": {
            "seed": seed,
            "aspectRatio": {
                "widthRatio": "1",
                "heightRatio": "1"
            }
        },
        "messages": [
            {
                "weight": 1,  # Исправлено: число вместо строки
                "text": prompt
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN0Ue86BCv7kA3CyK1oCsEDWy-uJdopl-w1eTh",  # Исправлен формат
        "x-folder-id": "b1guk8a9hg741ssab6ba"  # Добавлен folder-id
    }
    
    try:
        # Создаем запрос на генерацию
        create_request = requests.post(
            'https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync', 
            headers=headers, 
            json=request_data  # Исправлено: передаем request_data вместо prompt
        )
        
        # Проверяем успешность запроса
        if create_request.status_code != 200:
            print(f"Ошибка создания запроса: {create_request.status_code}")
            print(create_request.text)
            return None
            
        operation_id = create_request.json()["id"]
        print(f"Запущена генерация. Operation ID: {operation_id}")
        
        # Проверяем статус операции
        while True:
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
                    # Сохраняем изображение
                    filename = f"{operation_id}.jpeg"
                    with open(filename, 'wb') as file:
                        file.write(base64.b64decode(operation_data['response']['image']))
                    print(f"Изображение сохранено как: {filename}")
                    return filename
                else:
                    print("Ошибка: изображение не получено в ответе")
                    print(operation_data)
                    return None
                    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

if __name__ == "__main__":
    # Генерация изображения
    prompt = "Красивый закат над горами, цифровое искусство"
    seed = 12345
    
    result = yandex_art_request(prompt, seed)
    if result:
        print(f"Успешно создано: {result}")
    else:
        print("Не удалось создать изображение")