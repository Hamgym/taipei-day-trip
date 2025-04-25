from fastapi import *
from fastapi.responses import JSONResponse
from utils.pay import *
from utils.auth import *
from models.rdb import *
from models.data import *
router = APIRouter()

@router.post("/api/orders")
async def post_orders(payload=Depends(jwt_auth), body:OrderBody=Body()):
  order_id = generate_order_number(payload)
  body_dict = body.model_dump()
  try:
    CRUD.create_order(order_id, payload, body_dict)
  except:
    return JSONResponse({
      "error": True,
      "message": "訂單建立失敗，請稍後再試"
    }, 400)
  res_data = pay_by_prime(body_dict)
  CRUD.create_payment(order_id, res_data)
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
  CRUD.update_order(order_id)
  CRUD.delete_book(payload)
  return JSONResponse({
    "data": {
      "number": order_id,
      "payment": {
        "status": res_data["status"],
        "message": "付款成功"
      }
    }
  })
@router.get("/api/order/{orderNumber}")
async def get_order(payload=Depends(jwt_auth), orderNumber:str=Path()):
  row = CRUD.read_order(orderNumber, payload)
  if row==None:
    return {"data": None}
  data = get_order_data(row)
  return {"data": data}