import os, json
from mysql.connector.errors import PoolError
from mysql.connector.pooling import MySQLConnectionPool
from datetime import datetime, timezone, timedelta


dbconfig = {
  "user": os.getenv("DB_USER"),
  "password": os.getenv("DB_PASSWORD"),
  "host": "localhost",
  "database": "taipei_day_trip"
}
cnxpool = MySQLConnectionPool(pool_size=5, **dbconfig)
def get_cnx():
  cnx = cnxpool.get_connection()
  try:
    yield cnx
  finally:
    cnx.close()


select_attractions = "SELECT attraction.id, attraction.name, category, description, address, transport, mrt.name, lat, lng, images FROM attraction LEFT JOIN mrt ON attraction.mrt=mrt.id "
select_one_page = select_attractions+"LIMIT %s OFFSET %s"
select_by_keyword = select_attractions+"WHERE attraction.name LIKE %s OR mrt.name=%s LIMIT %s OFFSET %s"
select_attraction = select_attractions+"WHERE attraction.id=%s"
select_mrts = "SELECT name FROM mrt"
insert_user = "INSERT INTO user(name, email, password) VALUE(%s, %s, %s)"
select_user = "SELECT * FROM user WHERE email=%s AND password=%s"
delete_book = "DELETE FROM booking WHERE user_id=%s"
insert_book = "INSERT INTO booking(user_id, attraction_id, date, time, price) VALUES(%s, %s, %s, %s, %s)"
select_book = "SELECT attraction.id, attraction.name, attraction.address, attraction.images, booking.date, booking.time, booking.price FROM booking JOIN attraction ON booking.attraction_id=attraction.id WHERE booking.user_id=%s"
select_order = "SELECT * FROM orders WHERE id=%s"
select_order_strict = "SELECT * FROM orders WHERE id=%s AND user_id=%s"
insert_order = "INSERT INTO orders VALUES(%s, %s, %s, %s)"
update_order = "UPDATE orders SET status=1 WHERE id=%s"
insert_payment = "INSERT INTO payment VALUES(%s, %s)"


def get_next_page(records, page):
  if len(records) < 12:
    return None
  return page + 1
def fetch_attractions(cnx, page, keyword):
  cursor = cnx.cursor()
  limit = 12
  offset = page * limit
  if keyword==None:
    cursor.execute(select_one_page, (limit, offset))
  else:
    name = "%"+keyword+"%"
    cursor.execute(select_by_keyword, (name, keyword, limit, offset))
  records = cursor.fetchall()
  return records
def get_attractions_data(records):
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
  return data
def fetch_attraction(cnx, attractionId):
  cursor = cnx.cursor()
  cursor.execute(select_attraction, (attractionId,))
  record = cursor.fetchone()
  return record
def get_attraction_data(record):
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
  return data
def fetch_mrts(cnx):
  cursor = cnx.cursor()
  cursor.execute(select_mrts)
  records = cursor.fetchall()
  return records
def get_mrts_data(records):
  data = []
  for record in records:
    data.append(record[0])
  return data
def fetch_user(cnx, user):
  cursor = cnx.cursor()
  cursor.execute(select_user, (user.email, user.password))
  row = cursor.fetchone()
  return row
def fetch_book(cnx, payload):
  cursor = cnx.cursor()
  cursor.execute(select_book, (payload["id"],))
  row = cursor.fetchone()
  return row


def generate_serial_number() -> str:
  return datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d%H%M%S")
def generate_order_number(cnx, payload) -> str:
  cursor = cnx.cursor()
  order_id = generate_serial_number()
  cursor.execute(select_order, (order_id,))
  row = cursor.fetchone()
  if row!=None:
    appended = f"-{payload["id"]%1000:03}"
    order_id += appended
  return order_id