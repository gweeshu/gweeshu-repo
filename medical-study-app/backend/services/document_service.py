import os
import shutil
from typing import List, Optional
from models.database import get_session, Course, Lecture, Document, Image, Summary, Progress
from utils.document_parser import DocumentParser
from utils.image_extractor import ImageExtractor
from services.claude_service import ClaudeService

class DocumentService:
    def __init__(self):
        self.claude = ClaudeService()
        self.parser = DocumentParser()
        self.image_extractor = ImageExtractor()
        self.upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))
        self.images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "images"))
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    # Course Management
    def create_course(self, name: str, description: Optional[str] = None) -> dict:
        """Create a new course."""
        session = get_session()
        try:
            course = Course(name=name, description=description)
            session.add(course)
            session.commit()
            session.refresh(course)

            return {
                "id": course.id,
                "name": course.name,
                "description": course.description,
                "created_at": course.created_at.isoformat()
            }
        finally:
            session.close()

    def get_all_courses(self) -> List[dict]:
        """Get all courses with their lectures."""
        session = get_session()
        try:
            courses = session.query(Course).all()
            result = []

            for course in courses:
                lectures = []
                for lecture in course.lectures:
                    # Count documents
                    doc_count = len(lecture.documents)

                    # Get progress
                    progress_data = []
                    for progress in lecture.progress:
                        progress_data.append({
                            "pass_number": progress.pass_number,
                            "completed": progress.completed,
                            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
                        })

                    lectures.append({
                        "id": lecture.id,
                        "title": lecture.title,
                        "description": lecture.description,
                        "document_count": doc_count,
                        "progress": sorted(progress_data, key=lambda x: x["pass_number"])
                    })

                result.append({
                    "id": course.id,
                    "name": course.name,
                    "description": course.description,
                    "lectures": lectures
                })

            return result
        finally:
            session.close()

    def delete_course(self, course_id: int) -> bool:
        """Delete a course and all its lectures."""
        session = get_session()
        try:
            course = session.query(Course).filter_by(id=course_id).first()
            if course:
                session.delete(course)
                session.commit()
                return True
            return False
        finally:
            session.close()

    # Lecture Management
    def create_lecture(self, course_id: int, title: str, description: Optional[str] = None) -> dict:
        """Create a new lecture under a course."""
        session = get_session()
        try:
            # Verify course exists
            course = session.query(Course).filter_by(id=course_id).first()
            if not course:
                raise ValueError(f"Course {course_id} not found")

            lecture = Lecture(
                title=title,
                course_id=course_id,
                description=description
            )
            session.add(lecture)
            session.commit()

            # Create progress entries for 3 passes
            for pass_num in [1, 2, 3]:
                progress = Progress(
                    lecture_id=lecture.id,
                    pass_number=pass_num,
                    completed=False
                )
                session.add(progress)

            session.commit()
            session.refresh(lecture)

            return {
                "id": lecture.id,
                "title": lecture.title,
                "description": lecture.description,
                "course_id": lecture.course_id,
                "created_at": lecture.created_at.isoformat()
            }
        finally:
            session.close()

    def delete_lecture(self, lecture_id: int) -> bool:
        """Delete a lecture and all its documents."""
        session = get_session()
        try:
            lecture = session.query(Lecture).filter_by(id=lecture_id).first()
            if lecture:
                session.delete(lecture)
                session.commit()
                return True
            return False
        finally:
            session.close()

    # Document Management
    def upload_document(self, lecture_id: int, file_path: str, filename: str) -> dict:
        """Upload a document for a specific lecture."""
        session = get_session()
        try:
            # Verify lecture exists
            lecture = session.query(Lecture).filter_by(id=lecture_id).first()
            if not lecture:
                raise ValueError(f"Lecture {lecture_id} not found")

            # Determine file type
            ext = os.path.splitext(filename)[1].lower()
            file_type = ext[1:]  # Remove the dot

            # Copy file to uploads directory
            new_filename = f"lecture_{lecture_id}_{len(lecture.documents) + 1}_{filename}"
            new_path = os.path.join(self.upload_dir, new_filename)
            shutil.copy2(file_path, new_path)

            # Create document record
            document = Document(
                lecture_id=lecture_id,
                filename=filename,
                file_path=new_path,
                file_type=file_type
            )
            session.add(document)
            session.commit()
            session.refresh(document)

            # Extract images from document
            image_output_dir = os.path.join(self.images_dir, f"lecture_{lecture_id}", f"doc_{document.id}")
            extracted_images = self.image_extractor.extract_images(new_path, image_output_dir)

            # Store image records
            for img_path, page_num in extracted_images:
                img_filename = os.path.basename(img_path)
                image = Image(
                    document_id=document.id,
                    filename=img_filename,
                    file_path=img_path,
                    page_number=page_num
                )
                session.add(image)

            session.commit()

            return {
                "id": document.id,
                "filename": document.filename,
                "file_type": document.file_type,
                "images_extracted": len(extracted_images)
            }
        finally:
            session.close()

    def get_lecture_documents(self, lecture_id: int) -> List[dict]:
        """Get all documents for a lecture."""
        session = get_session()
        try:
            lecture = session.query(Lecture).filter_by(id=lecture_id).first()
            if not lecture:
                return []

            result = []
            for doc in lecture.documents:
                result.append({
                    "id": doc.id,
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "image_count": len(doc.images),
                    "created_at": doc.created_at.isoformat()
                })

            return result
        finally:
            session.close()

    # Summary Generation
    def generate_summary_for_lecture(self, lecture_id: int, pass_number: int) -> dict:
        """
        Generate a summary for a lecture by collating all its documents.
        Returns the summary content and associated images.
        """
        session = get_session()
        try:
            # Check if summary already exists
            existing = session.query(Summary).filter_by(
                lecture_id=lecture_id,
                pass_number=pass_number
            ).first()

            if existing:
                # Get images for this lecture
                lecture = session.query(Lecture).filter_by(id=lecture_id).first()
                images = []
                for doc in lecture.documents:
                    for img in doc.images:
                        images.append({
                            "filename": img.filename,
                            "path": img.file_path,
                            "page_number": img.page_number,
                            "document": doc.filename
                        })

                return {
                    "content": existing.content,
                    "images": images
                }

            # Get lecture and all its documents
            lecture = session.query(Lecture).filter_by(id=lecture_id).first()
            if not lecture:
                raise ValueError(f"Lecture {lecture_id} not found")

            if not lecture.documents:
                raise ValueError(f"No documents uploaded for lecture {lecture_id}")

            # Parse all documents
            all_text = []
            all_images = []

            for doc in lecture.documents:
                try:
                    text = self.parser.parse_document(doc.file_path)
                    all_text.append(f"\n\n=== From: {doc.filename} ===\n\n{text}")

                    # Collect images
                    for img in doc.images:
                        all_images.append({
                            "filename": img.filename,
                            "path": img.file_path,
                            "page_number": img.page_number,
                            "document": doc.filename
                        })
                except Exception as e:
                    print(f"Error parsing document {doc.filename}: {e}")

            combined_text = "\n".join(all_text)

            # Generate summary with Claude
            summary_content = self.claude.generate_summary(
                combined_text,
                pass_number,
                lecture.title,
                len(all_images)
            )

            # Store summary
            summary = Summary(
                lecture_id=lecture_id,
                pass_number=pass_number,
                content=summary_content
            )
            session.add(summary)
            session.commit()

            return {
                "content": summary_content,
                "images": all_images
            }

        finally:
            session.close()

    def mark_pass_complete(self, lecture_id: int, pass_number: int) -> bool:
        """Mark a pass as completed for a lecture."""
        session = get_session()
        try:
            from datetime import datetime
            progress = session.query(Progress).filter_by(
                lecture_id=lecture_id,
                pass_number=pass_number
            ).first()

            if progress:
                progress.completed = True
                progress.completed_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
