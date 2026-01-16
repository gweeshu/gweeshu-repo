from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pydantic import BaseModel
import os
import tempfile
from services.document_service import DocumentService

router = APIRouter()
doc_service = DocumentService()

# Request models
class CreateCourseRequest(BaseModel):
    name: str
    description: Optional[str] = None

class CreateLectureRequest(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None

class CompletePassRequest(BaseModel):
    lecture_id: int
    pass_number: int

# Course endpoints
@router.post("/courses")
async def create_course(request: CreateCourseRequest):
    """Create a new course."""
    try:
        course = doc_service.create_course(request.name, request.description)
        return JSONResponse(content={"success": True, "course": course})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/courses")
async def get_courses():
    """Get all courses with their lectures."""
    try:
        courses = doc_service.get_all_courses()
        return JSONResponse(content={"courses": courses})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/courses/{course_id}")
async def delete_course(course_id: int):
    """Delete a course and all its lectures."""
    try:
        success = doc_service.delete_course(course_id)
        if success:
            return JSONResponse(content={"success": True})
        else:
            raise HTTPException(status_code=404, detail="Course not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lecture endpoints
@router.post("/lectures")
async def create_lecture(request: CreateLectureRequest):
    """Create a new lecture under a course."""
    try:
        lecture = doc_service.create_lecture(
            request.course_id,
            request.title,
            request.description
        )
        return JSONResponse(content={"success": True, "lecture": lecture})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/lectures/{lecture_id}")
async def delete_lecture(lecture_id: int):
    """Delete a lecture and all its documents."""
    try:
        success = doc_service.delete_lecture(lecture_id)
        if success:
            return JSONResponse(content={"success": True})
        else:
            raise HTTPException(status_code=404, detail="Lecture not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lectures/{lecture_id}/documents")
async def get_lecture_documents(lecture_id: int):
    """Get all documents for a specific lecture."""
    try:
        documents = doc_service.get_lecture_documents(lecture_id)
        return JSONResponse(content={"documents": documents})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document upload endpoints
@router.post("/lectures/{lecture_id}/upload")
async def upload_documents(lecture_id: int, files: List[UploadFile] = File(...)):
    """Upload multiple documents for a specific lecture."""
    try:
        uploaded = []
        failed = []

        for file in files:
            try:
                # Save to temporary file
                suffix = os.path.splitext(file.filename)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    content = await file.read()
                    tmp.write(content)
                    tmp_path = tmp.name

                # Upload to document service
                result = doc_service.upload_document(lecture_id, tmp_path, file.filename)
                uploaded.append(result)

                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass

            except Exception as e:
                failed.append({"filename": file.filename, "error": str(e)})

        return JSONResponse(content={
            "success": True,
            "uploaded": len(uploaded),
            "failed": len(failed),
            "details": {
                "uploaded_files": uploaded,
                "failed_files": failed
            }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Summary endpoint
@router.get("/summary/{lecture_id}/{pass_number}")
async def get_summary(lecture_id: int, pass_number: int):
    """
    Get or generate summary for a lecture at a specific pass level.
    Returns summary content and associated images.
    """
    try:
        if pass_number not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Pass number must be 1, 2, or 3")

        result = doc_service.generate_summary_for_lecture(lecture_id, pass_number)

        return JSONResponse(content={
            "lecture_id": lecture_id,
            "pass_number": pass_number,
            "summary": result["content"],
            "images": result["images"]
        })

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image serving endpoint
@router.get("/images/{lecture_id}/{doc_id}/{filename}")
async def get_image(lecture_id: int, doc_id: int, filename: str):
    """Serve an image file."""
    try:
        images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "images"))
        image_path = os.path.join(images_dir, f"lecture_{lecture_id}", f"doc_{doc_id}", filename)

        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")

        return FileResponse(image_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Progress endpoint
@router.post("/complete")
async def complete_pass(request: CompletePassRequest):
    """Mark a pass as completed for a lecture."""
    try:
        success = doc_service.mark_pass_complete(request.lecture_id, request.pass_number)

        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"Pass {request.pass_number} marked complete"
            })
        else:
            raise HTTPException(status_code=404, detail="Progress entry not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
