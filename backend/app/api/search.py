from fastapi import APIRouter
from app.services.search_service import search_service
from pydantic import BaseModel

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.post("/search")
def search(request: SearchRequest):
    results = search_service.search_web(request.query)
    return {"results": results}
