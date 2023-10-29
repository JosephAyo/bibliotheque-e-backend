from fastapi import APIRouter


router = APIRouter(prefix="/user", tags=["Users"])


@router.post(
    "/dummy",
)
def dummy():
    return {"message": "success"}
