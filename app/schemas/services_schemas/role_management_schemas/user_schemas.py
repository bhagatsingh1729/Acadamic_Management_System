from pydantic import BaseModel, Field


# =============================================================
# USER SCHEMAS
# =============================================================

class PasswordChangeRequest(BaseModel):
    """
    FIX: new_password moved from query param to request body.
    Passwords must NEVER appear in URLs — they get logged
    by servers, proxies, and browsers.
    """
    new_password: str = Field(..., min_length=6)
