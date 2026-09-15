from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserLoginSchema(BaseModel):
    email: EmailStr
    password : str
    
