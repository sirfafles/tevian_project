import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.models import Task


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

    total_faces_count = 0
    total_male_count = 0
    total_female_count = 0
    total_male_age = 0
    total_female_age = 0
    male_age_count = 0
    female_age_count = 0

    images_data = []

    for image in task.images:
        faces_data = []
        for face in image.faces:
            faces_data.append(
                {"bbox": face.bbox, "gender": face.gender, "age": face.age}
            )

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

        images_data.append({"filename": image.filename, "faces": faces_data})

    if male_age_count > 0:
        avg_male_age = total_male_age / male_age_count
    else:
        avg_male_age = None

    if female_age_count > 0:
        avg_female_age = total_female_age / female_age_count
    else:
        avg_female_age = None

    response = {
        "task_id": task.id,
        "images": images_data,
        "total_faces_count": total_faces_count,
        "total_male_count": total_male_count,
        "total_female_count": total_female_count,
        "avg_male_age": avg_male_age,
        "avg_female_age": avg_female_age,
    }

    return response


def delete_task(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    images = task.images

    IMAGE_FOLDER_PATH = os.getenv("IMAGE_FOLDER_PATH")

    for image in images:
        file_path = os.path.join(IMAGE_FOLDER_PATH, image.filename)

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"Файл {file_path} не найден.")

    db.delete(task)
    db.commit()


def add_image_to_task(db: Session, task_id: int, filename: str, faces_data: list[dict]):
    db_image = models.Image(task_id=task_id, filename=filename)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    for face in faces_data:
        db_face = models.Face(
            image_id=db_image.id,
            bbox=face["bbox"],
            gender=face.get("gender", ""),
            age=face.get("age", None),
        )
        db.add(db_face)

    db.commit()
