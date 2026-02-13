
from groq import BaseModel
from pydantic import EmailStr


class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str