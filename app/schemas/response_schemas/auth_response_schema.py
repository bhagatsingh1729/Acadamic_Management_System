from typing import Optional, Any

from pydantic import BaseModel,EmailStr


class UserProfileSchema(BaseModel):

    data: Optional[Any] = None


class CurrentUserResponseSchema(BaseModel):

    id: int
    name: str
    email: EmailStr
    role: str

    profile: UserProfileSchema