from pydantic import BaseModel, Field
from datetime import date
from typing import Literal
import json


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


def get_attractions_data(rows):
  data = []
  tmp = {}
  for row in rows:
    tmp["id"] = row[0]
    tmp["name"] = row[1]
    tmp["category"] = row[2]
    tmp["description"] = row[3]
    tmp["address"] = row[4]
    tmp["transport"] = row[5]
    tmp["mrt"] = row[6]
    tmp["lat"] = row[7]
    tmp["lng"] = row[8]
    tmp["images"] = json.loads(row[9])
    data.append(tmp.copy())
    tmp.clear()
  return data
def get_attraction_data(row):
  data = {}
  data["id"] = row[0]
  data["name"] = row[1]
  data["category"] = row[2]
  data["description"] = row[3]
  data["address"] = row[4]
  data["transport"] = row[5]
  data["mrt"] = row[6]
  data["lat"] = row[7]
  data["lng"] = row[8]
  data["images"] = json.loads(row[9])
  return data
def get_mrts_data(rows):
  data = []
  for row in rows:
    data.append(row[0])
  return data
def get_book_data(row):
  data = {
    "attraction": {
      "id": row[0],
      "name": row[1],
      "address": row[2],
      "image": json.loads(row[3])[0]
    },
    "date": row[4],
    "time": row[5],
    "price": row[6]
  }
  return data
def get_order_data(row):
  order = json.loads(row[3])["order"]
  data = {
    "number": row[0],
    "price": order["price"],
    "trip": {
      "attraction": {
        "id": order["trip"]["attraction"]["id"],
        "name": order["trip"]["attraction"]["name"],
        "address": order["trip"]["attraction"]["address"],
        "image": order["trip"]["attraction"]["image"]
      },
      "date": order["trip"]["date"],
      "time": order["trip"]["time"]
    },
    "contact": {
      "name": order["contact"]["name"],
      "email": order["contact"]["email"],
      "phone": order["contact"]["phone"]
    },
    "status": row[2]
  }
  return data