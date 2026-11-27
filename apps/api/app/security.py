import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    try:
        return bool(_password_hasher.verify(stored_hash, password))
    except VerifyMismatchError:
        return False


def new_opaque_token() -> tuple[str, str]:
    raw = secrets.token_urlsafe(32)
    return raw, hash_token(raw)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_matches(raw: str | None, stored_hash: str) -> bool:
    if not raw:
        return False
    return hmac.compare_digest(hash_token(raw), stored_hash)
