#SECURITY SCHEME
from passlib.context import CryptContext

pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashPassword(password: str) -> str:
    return pwdContext.hash(password)