import os
import shutil
from typing import List
from models.database import get_session, Subject, Lecture, Summary, Progress
from utils.document_parser import DocumentParser
from services.claude_service import ClaudeService

class DocumentService:
    def __init__(self):
        self.claude = ClaudeService()
        self.parser = DocumentParser()
        self.upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))
        os.makedirs(self.upload_dir, exist_ok=True)

    def process_documents(self, file_paths: List[str]) -> dict:
        """
        Process multiple documents: parse, classify, and store in database.
        Returns summary of what was processed.
        """
        session = get_session()
        results = {
            "processed": 0,
            "failed": 0,
            "subjects_created": [],
            "lectures_created": []
        }

        try:
            # Parse all documents
            parsed_docs = []
            for file_path in file_paths:
                try:
                    text = self.parser.parse_document(file_path)
                    filename = os.path.basename(file_path)
                    parsed_docs.append({
                        "filename": filename,
                        "text": text,
                        "original_path": file_path
                    })
                except Exception as e:
                    print(f"Failed to parse {file_path}: {str(e)}")
                    results["failed"] += 1

            # Classify documents with Claude
            classifications = self.claude.batch_classify_documents(parsed_docs)

            # Store in database
            for i, classification in enumerate(classifications):
                try:
                    doc = parsed_docs[i]

                    # Get or create subject
                    subject = session.query(Subject).filter_by(name=classification["subject"]).first()
                    if not subject:
                        subject = Subject(name=classification["subject"])
                        session.add(subject)
                        session.commit()
                        results["subjects_created"].append(classification["subject"])

                    # Copy file to uploads directory
                    new_filename = f"{subject.id}_{len(subject.lectures) + 1}_{doc['filename']}"
                    new_path = os.path.join(self.upload_dir, new_filename)
                    shutil.copy2(doc["original_path"], new_path)

                    # Create lecture
                    lecture = Lecture(
                        title=classification["title"],
                        subject_id=subject.id,
                        original_filename=doc["filename"],
                        file_path=new_path
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
                    results["processed"] += 1
                    results["lectures_created"].append({
                        "subject": classification["subject"],
                        "title": classification["title"]
                    })

                except Exception as e:
                    print(f"Failed to store {classification['filename']}: {str(e)}")
                    session.rollback()
                    results["failed"] += 1

        finally:
            session.close()

        return results

    def generate_summary_for_lecture(self, lecture_id: int, pass_number: int) -> str:
        """
        Generate a summary for a specific lecture and pass.
        Caches the result in the database.
        """
        session = get_session()
        try:
            # Check if summary already exists
            existing = session.query(Summary).filter_by(
                lecture_id=lecture_id,
                pass_number=pass_number
            ).first()

            if existing:
                return existing.content

            # Get lecture
            lecture = session.query(Lecture).filter_by(id=lecture_id).first()
            if not lecture:
                raise ValueError(f"Lecture {lecture_id} not found")

            # Parse document
            text = self.parser.parse_document(lecture.file_path)

            # Generate summary with Claude
            summary_content = self.claude.generate_summary(text, pass_number, lecture.title)

            # Store summary
            summary = Summary(
                lecture_id=lecture_id,
                pass_number=pass_number,
                content=summary_content
            )
            session.add(summary)
            session.commit()

            return summary_content

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

    def get_all_subjects(self) -> List[dict]:
        """Get all subjects with their lectures and progress."""
        session = get_session()
        try:
            subjects = session.query(Subject).all()
            result = []

            for subject in subjects:
                lectures = []
                for lecture in subject.lectures:
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
                        "filename": lecture.original_filename,
                        "progress": sorted(progress_data, key=lambda x: x["pass_number"])
                    })

                result.append({
                    "id": subject.id,
                    "name": subject.name,
                    "description": subject.description,
                    "lectures": lectures
                })

            return result
        finally:
            session.close()
