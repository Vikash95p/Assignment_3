import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.document import DocumentResponse
from app.services.document_service import document_service
from app.core.config import settings

router = APIRouter()

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        doc = document_service.process_and_store_document(db, file.filename, file_path, file.content_type)
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("/documents", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return document_service.get_documents(db)

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = document_service.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/documents/{doc_id}/content")
def get_document_content(doc_id: str, db: Session = Depends(get_db)):
    doc = document_service.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(doc.file_path, filename=doc.filename, media_type=doc.file_type)

@router.post("/documents/create", response_model=DocumentResponse)
def create_document(content: str = Form(...), filename: str = Form(...), format: str = Form("txt"), db: Session = Depends(get_db)):
    return document_service.create_document_from_text(db, content, filename, format)

@router.post("/documents/{doc_id}/update", response_model=DocumentResponse)
def update_document(doc_id: str, instruction: str = Form(...), db: Session = Depends(get_db)):
    try:
        return document_service.update_document(db, doc_id, instruction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
