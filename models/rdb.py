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


def get_next_page(page, rows):
  if len(rows) < 12:
    return None
  return page + 1
def generate_serial_number() -> str:
  return datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d%H%M%S")
def generate_order_number(payload) -> str:
  with cnxpool.get_connection() as cnx:
    cursor = cnx.cursor()
    order_id = generate_serial_number()
    select = "SELECT * FROM orders WHERE id=%s"
    cursor.execute(select, (order_id,))
    row = cursor.fetchone()
    if row!=None:
      appended = f"-{payload["id"]%1000:03}"
      order_id += appended
    return order_id


class CRUD:
  def create_user(user):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      insert = "INSERT INTO user(name, email, password) VALUE(%s, %s, %s)"
      cursor.execute(insert, (user.name, user.email, user.password))
      cnx.commit()
  def create_book(payload, body):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      insert = "INSERT INTO booking(user_id, attraction_id, date, time, price) VALUES(%s, %s, %s, %s, %s)"
      cursor.execute(insert, (payload["id"], body.attractionId, body.date, body.time, body.price))
      cnx.commit()
  def create_order(order_id, payload, body):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      insert = "INSERT INTO orders VALUES(%s, %s, %s, %s)"
      cursor.execute(insert, (order_id, payload["id"], 0, json.dumps(body)))
      cnx.commit()
  def create_payment(order_id, res_data):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      insert = "INSERT INTO payment VALUES(%s, %s)"
      cursor.execute(insert, (order_id, json.dumps(res_data)))
      cnx.commit()
  def read_attractions(page, keyword):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      limit = 12
      offset = page * limit
      select_all = "SELECT attraction.id, attraction.name, category, description, address, transport, mrt.name, lat, lng, images FROM attraction LEFT JOIN mrt ON attraction.mrt=mrt.id "
      if keyword==None:
        select = select_all+"LIMIT %s OFFSET %s"
        cursor.execute(select, (limit, offset))
      else:
        name = "%"+keyword+"%"
        select = select_all+"WHERE attraction.name LIKE %s OR mrt.name=%s LIMIT %s OFFSET %s"
        cursor.execute(select, (name, keyword, limit, offset))
      rows = cursor.fetchall()
      return rows
  def read_attraction(attractionId):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      select_all = "SELECT attraction.id, attraction.name, category, description, address, transport, mrt.name, lat, lng, images FROM attraction LEFT JOIN mrt ON attraction.mrt=mrt.id "
      select = select_all+"WHERE attraction.id=%s"
      cursor.execute(select, (attractionId,))
      row = cursor.fetchone()
      return row
  def read_mrts():
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      cursor.execute("SELECT name FROM mrt")
      rows = cursor.fetchall()
      return rows
  def read_user(user):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      select = "SELECT * FROM user WHERE email=%s AND password=%s"
      cursor.execute(select, (user.email, user.password))
      row = cursor.fetchone()
      return row
  def read_book(payload):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      select = "SELECT attraction.id, attraction.name, attraction.address, attraction.images, booking.date, booking.time, booking.price FROM booking JOIN attraction ON booking.attraction_id=attraction.id WHERE booking.user_id=%s"
      cursor.execute(select, (payload["id"],))
      row = cursor.fetchone()
      return row
  def read_order(orderNumber, payload):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      select = "SELECT * FROM orders WHERE id=%s AND user_id=%s"
      cursor.execute(select, (orderNumber, payload["id"]))
      row = cursor.fetchone()
      return row
  def update_order(order_id):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      update = "UPDATE orders SET status=1 WHERE id=%s"
      cursor.execute(update, (order_id,))
      cnx.commit()
  def delete_book(payload):
    with cnxpool.get_connection() as cnx:
      cursor = cnx.cursor()
      delete = "DELETE FROM booking WHERE user_id=%s"
      cursor.execute(delete, (payload["id"],))
      cnx.commit()