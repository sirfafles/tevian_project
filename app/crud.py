from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models, schemas
from app.models import Task, Image, Face
import json

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Инициализация данных для ответа
    total_faces_count = 0
    total_male_count = 0
    total_female_count = 0
    total_male_age = 0
    total_female_age = 0
    male_age_count = 0
    female_age_count = 0

    images_data = []

    # Проход по всем изображениям задания
    for image in task.images:
        faces_data = []
        for face in image.faces:
            faces_data.append({
                "bbox": face.bbox,
                "gender": face.gender,
                "age": face.age
            })

            # Обновление статистики
            total_faces_count += 1
            if face.gender == "male":
                total_male_count += 1
                if face.age is not None:
                    total_male_age += face.age
                    male_age_count += 1
            elif face.gender == "female":
                total_female_count += 1
                if face.age is not None:
                    total_female_age += face.age
                    female_age_count += 1

        images_data.append({
            "filename": image.filename,
            "faces": faces_data
        })

    # Вычисление среднего возраста мужчин и женщин
    avg_male_age = total_male_age / male_age_count if male_age_count > 0 else None
    avg_female_age = total_female_age / female_age_count if female_age_count > 0 else None

    # Формирование финального ответа
    response = {
        "task_id": task.id,
        "images": images_data,
        "total_faces_count": total_faces_count,
        "total_male_count": total_male_count,
        "total_female_count": total_female_count,
        "avg_male_age": avg_male_age,
        "avg_female_age": avg_female_age
    }

    return response

def delete_task(db: Session, task_id: int):
    # Получение задачи через ORM
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Удаление через ORM, каскадное удаление сработает
    db.delete(task)
    db.commit()

def add_image_to_task(db: Session, task_id: int, filename: str, faces_data: list[dict]):
    # Сначала создаем запись об изображении
    db_image = models.Image(task_id=task_id, filename=filename)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    # Затем создаем записи для каждого лица
    for face in faces_data:
        db_face = models.Face(
            image_id=db_image.id,
            bbox=face['bbox'],
            gender=face.get('gender', ''),  # Обработка отсутствующих значений
            age=face.get('age', None)       # Обработка отсутствующих значений
        )
        db.add(db_face)

    db.commit()
