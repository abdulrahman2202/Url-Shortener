from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.schemas import URLShortenRequest, URLShortenResponse
from app.crud import create_short_url, get_url_by_short_code

# Create database tables on application start
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A production-ready and minimal URL shortener REST API.",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/shorten", response_model=URLShortenResponse)
def shorten_url(payload: URLShortenRequest, request: Request, db: Session = Depends(get_db)):
    try:
        db_url = create_short_url(db, original_url=payload.url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while shortening the URL: {str(e)}"
        )
    
    # Dynamically build the short URL based on the request's host/port details
    base_url = str(request.base_url)
    if not base_url.endswith("/"):
        base_url += "/"
    short_url = f"{base_url}{db_url.short_code}"
    
    return URLShortenResponse(
        short_code=db_url.short_code,
        short_url=short_url,
        original_url=db_url.original_url
    )

@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    db_url = get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=db_url.original_url, status_code=307)
