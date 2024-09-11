from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.utils import process_image
from app.models import Face
import json
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tasks/")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

@router.get("/tasks/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    crud.delete_task(db, task_id)
    return {"message": "Task deleted"}

@router.post("/tasks/{task_id}/images/")
async def upload_image(task_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Проверка типа файла
    if file.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="Only JPEG images are accepted")
    
    image_url = f"app/images/{file.filename}"

    with open(image_url, "wb") as buffer:
        buffer.write(await file.read())

    
    # Получение response от api
    faces_data = process_image(image_url)
    #print(faces_data['data'][1]['bbox'])
    #print(faces_data['data'][1]['demographics']['age']['mean'])
    #print(faces_data['data'][1]['demographics']['gender'])
    # Добавление изображения в БД
    image = models.Image(filename=file.filename, task_id=task_id)
    db.add(image)
    db.commit()
    
    image_id = image.id


    faces = faces_data.get('data', [])

    for face in faces:
        bbox = face.get('bbox', [])
        age = face.get('demographics', {}).get('age', {}).get('mean', None)
        gender = face.get('demographics', {}).get('gender', None)

        # Создание объекта Face и добавление его в базу данных
        face_entry = Face(
            image_id=image_id,
            bbox=str(bbox),
            age=age,
            gender=gender
        )
        db.add(face_entry)

    # Сохранение всех изменений в базе данных
    db.commit()
    
    return {"message": "Image uploaded and processed"}


