import os
import shutil
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentResponse
from app.core.config import settings
from app.document_processing.pdf_processor import extract_text_from_pdf
from app.document_processing.docx_processor import extract_text_from_docx
from app.document_processing.txt_processor import extract_text_from_txt
from app.document_processing.chunker import chunk_text
from app.ai.llm import ai_provider

class DocumentService:
    def process_and_store_document(self, db: Session, filename: str, file_path: str, file_type: str) -> Document:
        # 1. extract text
        text = ""
        if file_type == "application/pdf":
            text = extract_text_from_pdf(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(file_path)
        elif file_type == "text/plain" or file_type == "text/markdown":
            text = extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # 2. create document record
        db_document = Document(filename=filename, file_type=file_type, file_path=file_path)
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        # 3. chunk text
        chunks = chunk_text(text)

        # 4. generate embeddings and store chunks
        for chunk in chunks:
            embedding = ai_provider.generate_embeddings(chunk)
            db_chunk = DocumentChunk(
                document_id=db_document.id,
                chunk_text=chunk,
                embedding=embedding
            )
            db.add(db_chunk)
        
        db.commit()
        return db_document

    def get_document(self, db: Session, document_id: str) -> Optional[Document]:
        return db.query(Document).filter(Document.id == document_id).first()

    def get_documents(self, db: Session) -> List[Document]:
        return db.query(Document).all()

    def create_document_from_text(self, db: Session, content: str, filename: str, format: str) -> Document:
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # currently only saving as txt/md
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        file_type = "text/plain"
        if format == "markdown":
            file_type = "text/markdown"
            
        return self.process_and_store_document(db, filename, file_path, file_type)

    def update_document(self, db: Session, document_id: str, instruction: str) -> Document:
        doc = self.get_document(db, document_id)
        if not doc:
            raise ValueError("Document not found")
        
        # 1. extract current text
        text = ""
        if doc.file_type == "application/pdf":
            text = extract_text_from_pdf(doc.file_path)
        elif doc.file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(doc.file_path)
        elif doc.file_type in ["text/plain", "text/markdown"]:
            text = extract_text_from_txt(doc.file_path)
        else:
            raise ValueError("Unsupported file type for update")

        # 2. ask LLM to rewrite based on instruction
        new_content = ai_provider.edit_document(text, instruction)
        
        # 3. Save as new text/markdown file
        base_name, _ = os.path.splitext(doc.filename)
        new_filename = f"{base_name}_updated.md"
        
        return self.create_document_from_text(db, new_content, new_filename, "markdown")

document_service = DocumentService()
