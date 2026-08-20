import urllib.parse
from pydantic import BaseModel, ConfigDict, field_validator

class URLShortenRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        try:
            parsed = urllib.parse.urlparse(v)
            if parsed.scheme not in ("http", "https"):
                raise ValueError("URL scheme must be http or https")
            if not parsed.netloc:
                raise ValueError("URL must contain a valid domain or host name")
        except Exception as e:
            # Re-raise as ValueError so Pydantic catches it and returns 422 Unprocessable Entity
            raise ValueError(f"Invalid URL: {str(e)}")
        return v

class URLShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str

    model_config = ConfigDict(from_attributes=True)
