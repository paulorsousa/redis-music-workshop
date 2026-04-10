from fastapi import APIRouter
from services.admin import load_embeddings as _load_embeddings

router = APIRouter()


@router.post("/admin/load-embeddings")
def load_embeddings():
    """Compute song embeddings and load into Redis VectorSet (Module 6)."""
    return _load_embeddings()
