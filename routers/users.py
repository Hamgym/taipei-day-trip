from fastapi import *
from fastapi.responses import JSONResponse
from models.rdb import *
from models.data import *
from utils.auth import *
router = APIRouter()

@router.post("/api/user")
async def post_user(user:SignUp):
  try:
    CRUD.create_user(user)
    return {"ok": True}
  except:
    return JSONResponse({"error":True, "message":"註冊失敗，重複的 Email"}, 400)
@router.put("/api/user/auth")
async def put_auth(user:SignIn):
  row = CRUD.read_user(user)
  if row==None:
    return JSONResponse({"error":True, "message":"登入失敗，帳號或密碼錯誤"}, 400)
  token = generate_token(row)
  return {"token": token}
@router.get("/api/user/auth")
async def get_auth(payload=Depends(jwt_payload)):
  return {"data": payload}