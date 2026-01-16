from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Course(Base):
    """Courses are manually created by the user (e.g., Anatomy, Physiology)"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    lectures = relationship("Lecture", back_populates="course", cascade="all, delete-orphan")

class Lecture(Base):
    """Lectures are manually created under courses (e.g., 'Brainstem Anatomy')"""
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="lectures")
    documents = relationship("Document", back_populates="lecture", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="lecture", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="lecture", cascade="all, delete-orphan")

class Document(Base):
    """Documents uploaded for a specific lecture (multiple per lecture)"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, pptx, docx
    created_at = Column(DateTime, default=datetime.utcnow)

    lecture = relationship("Lecture", back_populates="documents")
    images = relationship("Image", back_populates="document", cascade="all, delete-orphan")

class Image(Base):
    """Images extracted from documents"""
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    page_number = Column(Integer)  # Which page/slide it came from
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="images")

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    pass_number = Column(Integer, nullable=False)  # 1, 2, or 3
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lecture = relationship("Lecture", back_populates="summaries")

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    pass_number = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    lecture = relationship("Lecture", back_populates="progress")

# Database setup
DATABASE_PATH = os.getenv("DATABASE_PATH", "../data/study_app.db")

def get_engine():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", DATABASE_PATH))
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    return engine

def get_session():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
