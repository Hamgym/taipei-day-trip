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
select_all = "SELECT attraction.id, attraction.name, category, description, address, transport, mrt.name, lat, lng, images FROM attraction LEFT JOIN mrt ON attraction.mrt=mrt.id "


async def get_cnx():
  cnx = cnxpool.get_connection()
  try:
    yield cnx
  finally:
    cnx.close()