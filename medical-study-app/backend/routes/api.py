from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel
import os
import tempfile
from services.document_service import DocumentService

router = APIRouter()
doc_service = DocumentService()

class CompletePassRequest(BaseModel):
    lecture_id: int
    pass_number: int

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process documents.
    Files will be parsed, classified by Claude, and stored.
    """
    try:
        # Save uploaded files temporarily
        temp_paths = []
        for file in files:
            # Create temp file with original extension
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                temp_paths.append(tmp.name)

        # Process documents
        results = doc_service.process_documents(temp_paths)

        # Clean up temp files
        for path in temp_paths:
            try:
                os.unlink(path)
            except:
                pass

        return JSONResponse(content={
            "success": True,
            "message": f"Processed {results['processed']} documents, {results['failed']} failed",
            "details": results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subjects")
async def get_subjects():
    """Get all subjects with lectures and progress."""
    try:
        subjects = doc_service.get_all_subjects()
        return JSONResponse(content={"subjects": subjects})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{lecture_id}/{pass_number}")
async def get_summary(lecture_id: int, pass_number: int):
    """
    Get or generate summary for a lecture at a specific pass level.
    Summaries are cached after first generation.
    """
    try:
        if pass_number not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Pass number must be 1, 2, or 3")

        summary = doc_service.generate_summary_for_lecture(lecture_id, pass_number)

        return JSONResponse(content={
            "lecture_id": lecture_id,
            "pass_number": pass_number,
            "summary": summary
        })

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
