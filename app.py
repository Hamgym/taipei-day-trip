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


from models.mysql import *
from models.data import SignIn, SignUp, Booking
from models.auth import AuthError, jwt_payload, jwt_auth, generate_token
from models.tappay import pay_by_prime
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
async def get_attractions(page:int=Query(ge=0), keyword:str=Query(None)):
  rows = CRUD.read_attractions(page, keyword)
  next_page = get_next_page(page, rows)
  data = get_attractions_data(rows)
  return {"nextPage":next_page, "data":data}
@app.get("/api/attraction/{attractionId}")
async def get_attraction_by_id(attractionId:int):
  row = CRUD.read_attraction(attractionId)
  if row==None:
    return JSONResponse({"error":True, "message":"景點編號不正確"}, 400)
  data = get_attraction_data(row)
  return {"data": data}
@app.get("/api/mrts")
async def get_mrts():
  rows = CRUD.read_mrts()
  data = get_mrts_data(rows)
  return {"data": data}


@app.post("/api/user")
async def post_user(user:SignUp):
  try:
    CRUD.create_user(user)
    return {"ok": True}
  except:
    return JSONResponse({"error":True, "message":"註冊失敗，重複的 Email"}, 400)
@app.put("/api/user/auth")
async def put_auth(user:SignIn):
  row = CRUD.read_user(user)
  if row==None:
    return JSONResponse({"error":True, "message":"登入失敗，帳號或密碼錯誤"}, 400)
  token = generate_token(row)
  return {"token": token}
@app.get("/api/user/auth")
async def get_auth(payload=Depends(jwt_payload)):
  return {"data": payload}


@app.post("/api/booking")
async def post_booking(payload=Depends(jwt_auth), body:Booking=Body()):
  try:
    CRUD.delete_book(payload)
    CRUD.create_book(payload, body)
    return {"ok": True}
  except:
    return JSONResponse({
      "error": True,
      "message": "建立失敗，輸入不正確或其他原因"
    }, 400)
@app.get("/api/booking")
async def get_booking(payload=Depends(jwt_auth)):
  row = CRUD.read_book(payload)
  if row==None:
    return {"data": None}
  data = get_book_data(row)
  return {"data": data}
@app.delete("/api/booking")
async def delete_booking(payload=Depends(jwt_auth)):
  CRUD.delete_book(payload)
  return JSONResponse({"ok": True})


@app.post("/api/orders")
async def post_orders(payload=Depends(jwt_auth), body=Body(), cnx=Depends(get_cnx)):
  cursor = cnx.cursor()
  order_id = generate_order_number(cnx, payload)
  try:
    cursor.execute(insert_order, (order_id, payload["id"], 0, json.dumps(body)))
    cnx.commit()
  except:
    return JSONResponse({
      "error": True,
      "message": "訂單建立失敗，請稍後再試"
    }, 400)
  res_data = pay_by_prime(body)
  cursor.execute(insert_payment, (order_id, json.dumps(res_data)))
  cnx.commit()
  if res_data["status"]!=0:
    return JSONResponse({
      "data": {
        "number": order_id,
        "payment": {
          "status": res_data["status"],
          "message": "付款失敗"
        }
      }
    })
  cursor.execute(update_order, (order_id,))
  cursor.execute(delete_book, (payload["id"],))
  cnx.commit()
  return JSONResponse({
    "data": {
      "number": order_id,
      "payment": {
        "status": res_data["status"],
        "message": "付款成功"
      }
    }
  })
@app.get("/api/order/{orderNumber}")
async def get_order(payload=Depends(jwt_auth), orderNumber:str=Path(), cnx=Depends(get_cnx)):
  cursor = cnx.cursor()
  cursor.execute(select_order_strict, (orderNumber, payload["id"]))
  row = cursor.fetchone()
  if row==None:
    return {"data": None}
  order = json.loads(row[3])["order"]
  return {
    "data": {
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
  }