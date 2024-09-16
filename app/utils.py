import os

import requests
from dotenv import load_dotenv


load_dotenv()
FACE_CLOUD_API_URL = os.getenv("FACE_CLOUD_API_URL")
FACE_CLOUD_TOKEN = os.getenv("FACE_CLOUD_TOKEN")


def process_image(image_path: str):
    params = {
        "fd_min_size": 0,
        "fd_max_size": 0,
        "fd_threshold": 0.8,
        "rotate_until_faces_found": "false",
        "orientation_classifier": "false",
        "demographics": "true",
        "attributes": "true",
        "landmarks": "false",
        "liveness": "false",
        "quality": "false",
        "masks": "false",
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {FACE_CLOUD_TOKEN}",
        "Content-Type": "image/jpeg",
    }

    with open(image_path, "rb") as image_file:
        response = requests.post(
            FACE_CLOUD_API_URL,
            headers=headers,
            params=params,
            data=image_file,
            timeout=10,
        )

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("Ошибка при обработке JSON-ответа.")
        return None
