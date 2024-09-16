import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal
from app.models import Face
from app.utils import process_image

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
async def upload_image(
    task_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    IMAGE_FOLDER_PATH = os.getenv("IMAGE_FOLDER_PATH")
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if file.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="Only JPEG images are accepted")

    image_url = f"{IMAGE_FOLDER_PATH}/{file.filename}"

    with open(image_url, "wb") as buffer:
        buffer.write(await file.read())

    faces_data = process_image(image_url)
    image = models.Image(filename=file.filename, task_id=task_id)
    db.add(image)
    db.commit()

    image_id = image.id

    faces = faces_data.get("data", [])

    for face in faces:
        bbox = face.get("bbox", [])
        age = face.get("demographics", {}).get("age", {}).get("mean", None)
        gender = face.get("demographics", {}).get("gender", None)

        face_entry = Face(image_id=image_id, bbox=str(bbox), age=age, gender=gender)
        db.add(face_entry)

    db.commit()

    return {"message": "Image uploaded and processed"}
