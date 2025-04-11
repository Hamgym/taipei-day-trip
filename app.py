from dotenv import load_dotenv
load_dotenv()


from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


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


import os, json, jwt
from datetime import datetime, timezone, timedelta
from models.mysql import PoolError, cnxpool, select_all
from models.data import SignIn, SignUp, Booking
@app.exception_handler(PoolError)
async def pool_error(request:Request, exc:PoolError):
  return JSONResponse({"error":True, "message":"資料庫忙線中"}, 500)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
  return JSONResponse({"error":True, "message":"資料格式不符，請重新輸入"}, 400)


@app.get("/api/attractions")
async def get_attractions(page:int=Query(ge=0), keyword:str=Query(None)):
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  limit = 12
  offset = page * limit
  if keyword==None:
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
async def get_attraction_by_id(attractionId:int):
  cnx = cnxpool.get_connection()
  cursor = cnx.cursor()
  cursor.execute(select_all+"WHERE attraction.id=%s", (attractionId,))
  record = cursor.fetchone()
  if record==None:
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


@app.post("/api/user")
async def post_user(user:SignUp):
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
async def put_auth(user:SignIn):
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
async def get_auth(authorization:str=Header()):
  try:
    [scheme, token] = authorization.split()
    payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    payload.pop("exp")
    return {"data": payload}
  except:
    return {"data": None}


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
    cnx.close()
    return {"ok": True}
  except:
    cnx.close()
    return JSONResponse({
      "error": True,
      "message": "建立失敗，輸入不正確或其他原因"
    }, 400)
@app.get("/api/booking")
async def get_booking(authorization:str=Header()):
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
  cursor.execute("SELECT attraction.id, attraction.name, attraction.address, attraction.images, booking.date, booking.time, booking.price FROM booking JOIN attraction ON booking.attraction_id=attraction.id WHERE booking.user_id=%s", (payload["id"],))
  row = cursor.fetchone()
  if(row == None):
    cnx.close()
    return {"data": None}
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
  cnx.close()
  return {"data": data}
@app.delete("/api/booking")
async def delete_booking(authorization:str=Header()):
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
  cursor.execute("DELETE FROM booking WHERE user_id=%s", (payload["id"],))
  cnx.commit()
  cnx.close()
  return JSONResponse({"ok": True})