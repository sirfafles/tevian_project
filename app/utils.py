import requests

# Настройка переменных
FACE_CLOUD_API_URL = "https://backend.facecloud.tevian.ru/api/v1/detect"
FACE_CLOUD_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3MjU5ODg0NDcsIm5iZiI6MTcyNTk4ODQ0NywianRpIjoiYmFkZTJmODAtMWY2OC00MTFiLWFjNDItZWU5YjkwOWI4ZDYxIiwic3ViIjo0NjksImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.g6PDwLeqJuxLNuP4XFB5Z5x2ZWT-rk_isNMT29bnaOY"

def process_image(image_path: str):
    # Параметры запроса
    params = {
        'fd_min_size': 0,
        'fd_max_size': 0,
        'fd_threshold': 0.8,
        'rotate_until_faces_found': 'false',
        'orientation_classifier': 'false',
        'demographics': 'true',
        'attributes': 'true',
        'landmarks': 'false',
        'liveness': 'false',
        'quality': 'false',
        'masks': 'false'
    }

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {FACE_CLOUD_TOKEN}',
        'Content-Type': 'image/jpeg'
    }

    # Открываем изображение как бинарные данные
    with open(image_path, 'rb') as image_file:
        response = requests.post(
            FACE_CLOUD_API_URL,
            headers=headers,
            params=params,
            data=image_file
        )
    
    #print("Status Code:", response.status_code)
    #print("Response Text:", response.text)
    
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("Ошибка при обработке JSON-ответа.")
        return None
