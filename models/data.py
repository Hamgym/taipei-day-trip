from pydantic import BaseModel, Field
from datetime import date
from typing import Literal
class SignIn(BaseModel):
  email: str = Field(min_length=3)
  password: str = Field(min_length=3)
class SignUp(SignIn):
  name: str = Field(min_length=1)
class Booking(BaseModel):
  attractionId: int = Field(ge=1)
  date: date
  time: Literal["morning", "afternoon"]
  price: Literal[2000, 2500]