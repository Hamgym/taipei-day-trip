import os
from mysql.connector.errors import PoolError
from mysql.connector.pooling import MySQLConnectionPool


dbconfig = {
  "user": os.getenv("DB_USER"),
  "password": os.getenv("DB_PASSWORD"),
  "host": "localhost",
  "database": "taipei_day_trip"
}
cnxpool = MySQLConnectionPool(pool_size=5, **dbconfig)


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


async def get_cnx():
  cnx = cnxpool.get_connection()
  try:
    yield cnx
  finally:
    cnx.close()