from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class EnquiryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    company: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=5000)
    # Honeypot field: real users never fill this in; bots often do.
    website: str = Field(default="", max_length=200)

    @field_validator("name", "company", "message", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class EnquiryOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    company: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
