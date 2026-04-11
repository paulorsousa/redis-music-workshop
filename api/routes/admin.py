from fastapi import APIRouter

router = APIRouter()


@router.post("/admin/load-embeddings")
def load_embeddings():
    """Compute song embeddings and load into Redis VectorSet (Module 6).

    TODO: Implement in the 'vectorsets' branch.
    """
    return {"message": "VectorSet support is available on the 'vectorsets' branch."}
