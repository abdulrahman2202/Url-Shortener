import random
import string
from sqlalchemy.orm import Session
from app.models import URL

def generate_short_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code of specified length."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

def get_url_by_short_code(db: Session, short_code: str) -> URL | None:
    """Retrieve record matching short code."""
    return db.query(URL).filter(URL.short_code == short_code).first()

def create_short_url(db: Session, original_url: str) -> URL:
    """
    Generate unique short code, check for conflicts,
    and save the record to PostgreSQL.
    """
    for _ in range(100):  # Safe upper limit to prevent infinite loops
        short_code = generate_short_code()
        existing = get_url_by_short_code(db, short_code)
        if not existing:
            db_url = URL(original_url=original_url, short_code=short_code)
            db.add(db_url)
            db.commit()
            db.refresh(db_url)
            return db_url
    
    db.rollback()
    raise RuntimeError("Failed to generate a unique short code after maximum retries.")
