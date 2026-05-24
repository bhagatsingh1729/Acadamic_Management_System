from typing import Optional, Any

from pydantic import BaseModel


class UserProfileSchema(BaseModel):

    data: Optional[Any] = None


class CurrentUserResponseSchema(BaseModel):

    id: int
    name: str
    email: str
    role: str

    profile: UserProfileSchema