from fastapi import *
from fastapi.responses import JSONResponse
from models.rdb import *
from models.data import *
router = APIRouter()

@router.get("/api/attractions")
async def get_attractions(page:int=Query(ge=0), keyword:str=Query(None)):
  rows = CRUD.read_attractions(page, keyword)
  next_page = get_next_page(page, rows)
  data = get_attractions_data(rows)
  return {"nextPage":next_page, "data":data}
@router.get("/api/attraction/{attractionId}")
async def get_attraction_by_id(attractionId:int):
  row = CRUD.read_attraction(attractionId)
  if row==None:
    return JSONResponse({"error":True, "message":"景點編號不正確"}, 400)
  data = get_attraction_data(row)
  return {"data": data}
@router.get("/api/mrts")
async def get_mrts():
  rows = CRUD.read_mrts()
  data = get_mrts_data(rows)
  return {"data": data}