from fastapi import *
from fastapi.responses import FileResponse
app=FastAPI()


# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
  return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
  return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
  return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
  return FileResponse("./static/thankyou.html", media_type="text/html")


from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")


from dotenv import load_dotenv
load_dotenv()
import os
from mysql.connector.pooling import MySQLConnectionPool
dbconfig = {
  "user": os.getenv("DB_USER"),
  "password": os.getenv("DB_PASSWORD"),
  "host": "localhost",
  "database": "taipei_day_trip"
}
cnxpool = MySQLConnectionPool(pool_size=5, **dbconfig)
select_all = "SELECT attraction.id, attraction.name, category, description, address, transport, mrt.name, lat, lng, images FROM attraction LEFT JOIN mrt ON attraction.mrt=mrt.id "


from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from mysql.connector.errors import PoolError
@app.exception_handler(PoolError)
async def pool_error(request:Request, exc:PoolError):
  return JSONResponse({"error":True, "message":"資料庫忙線中"}, 500)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
  return JSONResponse({"error":True, "message":"資料格式不符，請重新輸入"}, 400)


from pydantic import BaseModel, Field
from datetime import date
from typing import Literal
class SignIn(BaseModel):
  email: str = Field(min_length=3)
  password: str = Field(min_length=3)
class SignUp(SignIn):
  name: str = Field(min_length=1)
class Booking(BaseModel):
  attractionId: int
  date: date
  time: Literal["morning", "afternoon"]
  price: Literal[2000, 2500]


from fastapi.responses import RedirectResponse
@app.middleware("http")
async def check_signin_status(request:Request, call_next):
  if request.scope["path"].find("booking", 0, 12) != -1:
    pass
    # print("booking!!!")
    # return RedirectResponse("/")
    # print(request.headers.get("authorization"))
    # return JSONResponse("請登入", 401)
  response = await call_next(request)
  return response


import jwt
from datetime import datetime, timezone, timedelta
@app.post("/api/user")
async def post_user(user: SignUp):
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  try:
    cursor.execute("INSERT INTO user(name, email, password) VALUE(%s, %s, %s)", (user.name, user.email, user.password))
    cnx.commit()
    cnx.close()
    return {"ok": True}
  except:
    cnx.close()
    return JSONResponse({"error":True, "message":"註冊失敗，重複的 Email"}, 400)
@app.put("/api/user/auth")
async def put_auth(user: SignIn):
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  cursor.execute("SELECT * FROM user WHERE email=%s AND password=%s", (user.email, user.password))
  row = cursor.fetchone()
  if(row):
    payload = {"id":row[0], "name":row[1], "email":row[2]}
    payload["exp"] = datetime.now(timezone.utc) + timedelta(weeks=1)
    encoded_jwt = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
    cnx.close()
    return {"token": encoded_jwt}
  else:
    cnx.close()
    return JSONResponse({"error":True, "message":"登入失敗，帳號或密碼錯誤"}, 400)
@app.get("/api/user/auth")
async def get_auth(authorization: str = Header()):
  # if scheme != "Bearer":
  #   return {"data": None}
  try:
    [scheme, token] = authorization.split()
    payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    payload.pop("exp")
    return {"data": payload}
  except:
    return {"data": None}


import json
@app.get("/api/attractions")
async def get_attractions(page:int=Query(ge=0), keyword:str=Query(None)):
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  limit = 12
  offset = page * limit
  if keyword == None:
    cursor.execute(select_all+"LIMIT %s OFFSET %s", (limit, offset))
  else:
    name = "%"+keyword+"%"
    cursor.execute(select_all+"WHERE attraction.name LIKE %s OR mrt.name=%s LIMIT %s OFFSET %s", (name, keyword, limit, offset))
  records = cursor.fetchall()
  if len(records) < 12:
    next_page = None
  else:
    next_page = page + 1
  data = []
  tmp = {}
  for record in records:
    tmp["id"] = record[0]
    tmp["name"] = record[1]
    tmp["category"] = record[2]
    tmp["description"] = record[3]
    tmp["address"] = record[4]
    tmp["transport"] = record[5]
    tmp["mrt"] = record[6]
    tmp["lat"] = record[7]
    tmp["lng"] = record[8]
    tmp["images"] = json.loads(record[9])
    data.append(tmp.copy())
    tmp.clear()
  cnx.close()
  return {"nextPage": next_page, "data": data}
@app.get("/api/attraction/{attractionId}")
async def get_attraction_by_id(attractionId: int):
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  cursor.execute(select_all+"WHERE attraction.id=%s", (attractionId,))
  record = cursor.fetchone()
  if record == None:
    cnx.close()
    return JSONResponse({"error":True,"message":"景點編號不正確"}, 400)
  else:
    data = {}
    data["id"] = record[0]
    data["name"] = record[1]
    data["category"] = record[2]
    data["description"] = record[3]
    data["address"] = record[4]
    data["transport"] = record[5]
    data["mrt"] = record[6]
    data["lat"] = record[7]
    data["lng"] = record[8]
    data["images"] = json.loads(record[9])
    cnx.close()
    return {"data": data}
@app.get("/api/mrts")
async def get_mrts():
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  cursor.execute("SELECT name FROM mrt")
  records = cursor.fetchall()
  data = []
  for record in records:
    data.append(record[0])
  cnx.close()
  return {"data": data}


@app.post("/api/booking")
async def post_booking(authorization:str=Header(), body:Booking=Body()):
  payload = {}
  try:
    [scheme, token] = authorization.split()
    payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
  except:
    return JSONResponse({
      "error": True,
      "message": "未登入系統，拒絕存取"
    }, 403)
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  try:
    cursor.execute("DELETE FROM booking WHERE user_id=%s", (payload["id"],))
    cursor.execute("INSERT INTO booking(user_id, attraction_id, date, time, price) VALUES(%s, %s, %s, %s, %s)", (payload["id"], body.attractionId, body.date, body.time, body.price))
    cnx.commit()
  except:
    cnx.close()
    return JSONResponse({
      "error": True,
      "message": "建立失敗，輸入不正確或其他原因"
    }, 400)
  cnx.close()
  return {"ok": True}
