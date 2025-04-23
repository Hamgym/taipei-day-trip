from fastapi import *
from fastapi.responses import JSONResponse
from utils.auth import *
from models.rdb import *
from models.data import *
router = APIRouter()

@router.post("/api/booking")
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
@router.get("/api/booking")
async def get_booking(payload=Depends(jwt_auth)):
  row = CRUD.read_book(payload)
  if row==None:
    return {"data": None}
  data = get_book_data(row)
  return {"data": data}
@router.delete("/api/booking")
async def delete_booking(payload=Depends(jwt_auth)):
  CRUD.delete_book(payload)
  return JSONResponse({"ok": True})