from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.document import DocumentChunk, Document
from app.ai.llm import ai_provider

class RAGService:
    def retrieve_relevant_chunks(self, db: Session, query: str, top_k: int = 3, document_ids: List[str] = None) -> List[Dict[str, Any]]:
        query_embedding = ai_provider.generate_embeddings(query)
        
        # Convert embedding to string format for pgvector
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # SQLAlchemy pgvector similarity search using L2 distance (<->) or Cosine distance (<=>)
        # Using cosine distance
        
        base_query = db.query(DocumentChunk, Document).join(Document)
        
        if document_ids:
            base_query = base_query.filter(DocumentChunk.document_id.in_(document_ids))
            
        # Order by cosine distance
        results = base_query.order_by(DocumentChunk.embedding.cosine_distance(embedding_str)).limit(top_k).all()
        
        formatted_results = []
        for chunk, doc in results:
            formatted_results.append({
                "chunk_text": chunk.chunk_text,
                "document_name": doc.filename,
                "document_id": doc.id,
                "page": chunk.page_number
            })
            
        return formatted_results

rag_service = RAGService()
