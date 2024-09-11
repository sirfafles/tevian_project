from sqlalchemy.orm import Session
from app import models, schemas
import json

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def delete_task(db: Session, task_id: int):
    db.query(models.Task).filter(models.Task.id == task_id).delete()
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
