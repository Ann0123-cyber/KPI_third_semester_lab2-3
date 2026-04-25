from calendar import timegm
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60

def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "exp": timegm(expire.utctimetuple())},
        SECRET_KEY, algorithm=ALGORITHM,
    )

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise ValueError("Invalid or expired token")
