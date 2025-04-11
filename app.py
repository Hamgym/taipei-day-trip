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
from models.mysql import *
from models.data import SignIn, SignUp, Booking
from models.auth import AuthError, jwt_payload, jwt_auth
@app.exception_handler(PoolError)
async def pool_error(request:Request, exc:PoolError):
  return JSONResponse({"error":True, "message":"資料庫忙線中"}, 500)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
  return JSONResponse({"error":True, "message":"資料格式不符，請重新輸入"}, 400)
@app.exception_handler(AuthError)
async def auth_error(request, exc):
  return JSONResponse({"error":True, "message":"未登入系統，拒絕存取"}, 403)


@app.get("/api/attractions")
async def get_attractions(page:int=Query(ge=0), keyword:str=Query(None), cnx=Depends(get_cnx)):
  rows = fetch_attractions(cnx, page, keyword)
  next_page = get_next_page(rows, page)
  data = get_attractions_data(rows)
  return {"nextPage":next_page, "data":data}
@app.get("/api/attraction/{attractionId}")
async def get_attraction_by_id(attractionId:int, cnx=Depends(get_cnx)):
  row = fetch_attraction(cnx, attractionId)
  if row==None:
    return JSONResponse({"error":True, "message":"景點編號不正確"}, 400)
  data = get_attraction_data(row)
  return {"data": data}
@app.get("/api/mrts")
async def get_mrts(cnx=Depends(get_cnx)):
  rows = fetch_mrts(cnx)
  data = get_mrts_data(rows)
  return {"data": data}


@app.post("/api/user")
async def post_user(user:SignUp, cnx=Depends(get_cnx)):
  cursor = cnx.cursor()
  try:
    cursor.execute(insert_user, (user.name, user.email, user.password))
    cnx.commit()
    return {"ok": True}
  except:
    return JSONResponse({"error":True, "message":"註冊失敗，重複的 Email"}, 400)
@app.put("/api/user/auth")
async def put_auth(user:SignIn, cnx=Depends(get_cnx)):
  cursor = cnx.cursor()
  cursor.execute(select_user, (user.email, user.password))
  row = cursor.fetchone()
  if row==None:
    return JSONResponse({"error":True, "message":"登入失敗，帳號或密碼錯誤"}, 400)
  payload = {"id":row[0], "name":row[1], "email":row[2]}
  payload["exp"] = datetime.now(timezone.utc) + timedelta(weeks=1)
  token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
  return {"token": token}
@app.get("/api/user/auth")
async def get_auth(payload=Depends(jwt_payload)):
  return {"data": payload}


@app.post("/api/booking")
async def post_booking(payload=Depends(jwt_auth), body:Booking=Body(), cnx=Depends(get_cnx)):
  cursor = cnx.cursor()
  try:
    cursor.execute(delete_book, (payload["id"],))
    cursor.execute(insert_book, (payload["id"], body.attractionId, body.date, body.time, body.price))
    cnx.commit()
    return {"ok": True}
  except:
    return JSONResponse({
      "error": True,
      "message": "建立失敗，輸入不正確或其他原因"
    }, 400)
@app.get("/api/booking")
async def get_booking(payload=Depends(jwt_auth), cnx=Depends(get_cnx)):
  cursor = cnx.cursor()
  cursor.execute(select_book, (payload["id"],))
  row = cursor.fetchone()
  if row==None:
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
  return {"data": data}
@app.delete("/api/booking")
async def delete_booking(payload=Depends(jwt_auth), cnx=Depends(get_cnx)):
  cursor = cnx.cursor()
  cursor.execute(delete_book, (payload["id"],))
  cnx.commit()
  return JSONResponse({"ok": True})