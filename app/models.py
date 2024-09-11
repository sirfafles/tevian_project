from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base,engine

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    images = relationship("Image", back_populates="task")

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    faces = relationship("Face", back_populates="image")  # Связь с таблицей лиц
    task = relationship("Task", back_populates="images")

class Face(Base):
    __tablename__ = "faces"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    bbox = Column(String)  # координаты bounding box
    gender = Column(String)  # пол
    age = Column(Integer)  # возраст
    image = relationship("Image", back_populates="faces")
Base.metadata.create_all(bind=engine)