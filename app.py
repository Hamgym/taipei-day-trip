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
from mysql.connector.errors import PoolError, IntegrityError
@app.exception_handler(PoolError)
async def pool_error(request:Request, exc:PoolError):
  return JSONResponse({"error":True,"message":"資料庫忙線中"}, 500)
@app.exception_handler(IntegrityError)
async def duplicate_error(request:Request, exc:IntegrityError):
  return JSONResponse({"error":True,"message":"註冊失敗，重複的 Email。"}, 400)
from fastapi.exceptions import RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse({"error":True,"message":"註冊失敗，資料格式不符。"}, 400)


import jwt
from datetime import datetime, timezone, timedelta
encoded_jwt = jwt.encode({"exp": datetime.now(timezone.utc)+timedelta(seconds=10)}, "secret", algorithm="HS256")
# print(jwt.decode(encoded_jwt, "secret", algorithms=["HS256"]))


from pydantic import BaseModel, Field
class SignUp(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=3)

class SignIn(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=3)


@app.post("/api/user")
async def post_user(user: SignUp):
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  cursor.execute("INSERT INTO user(name, email, password) VALUE(%s, %s, %s)", (user.name, user.email, user.password))
  cnx.commit()
  cnx.close()
  return {"ok": True}

@app.put("/api/user/auth")
async def put_auth(user: SignIn):
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  cursor.execute("SELECT * FROM user WHERE email=%s AND password=%s", (user.email, user.password))
  row = cursor.fetchone()
  if(not row):
    return {"error":True, "message": "登入失敗，帳號或密碼錯誤。"}
  payload = {"id":row[0], "name":row[1], "email":row[2]}
  payload["exp"] = datetime.now(timezone.utc) + timedelta(seconds=10)
  encoded_jwt = jwt.encode(payload, "secret", algorithm="HS256")
  cnx.close()
  return {"token": encoded_jwt}


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