from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_hash(plain_text, hashed_text):
    return pwd_context.verify(plain_text, hashed_text)

def create_hash(plain_text: str):
    return pwd_context.hash(plain_text)
