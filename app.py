from dotenv import load_dotenv
load_dotenv()


from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from utils.auth import *
from models.rdb import *
from routers import attractions, bookings, orders, users
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


@app.exception_handler(PoolError)
async def pool_error(request:Request, exc:PoolError):
  return JSONResponse({"error":True, "message":"資料庫忙線中"}, 500)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
  return JSONResponse({"error":True, "message":"資料格式不符，請重新輸入"}, 400)
@app.exception_handler(AuthError)
async def auth_error(request, exc):
  return JSONResponse({"error":True, "message":"未登入系統，拒絕存取"}, 403)


app.include_router(attractions.router)
app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(orders.router)