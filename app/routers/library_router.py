from fastapi import APIRouter


router = APIRouter(prefix="/library/books", tags=["Library"])


@router.post(
    "/dummy",
)
def dummy():
    return {"message": "success"}
