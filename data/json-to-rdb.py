import json
with open("./data/taipei-attractions.json", encoding="utf-8") as file:
  raw_data = json.load(file)
  raw_data = raw_data["result"]["results"]
  img_filter = {"jpg", "JPG", "png", "PNG"}
  data = []
  record = {}
  for item in raw_data:
    record["id"] = item["_id"]
    record["name"] = item["name"]
    record["category"] = item["CAT"]
    record["description"] = item["description"]
    record["address"] = item["address"].replace(" ", "")
    record["transport"] = item["direction"]
    record["mrt"] = item["MRT"]
    record["lat"] = item["latitude"]
    record["lng"] = item["longitude"]
    urls = item["file"]
    separator = "https://"
    images = urls.split(separator)
    images = [separator+image for image in images if image[-3:] in img_filter]
    record["images"] = images
    data.append(record.copy())
    record.clear()

from dotenv import load_dotenv
load_dotenv()
import os
import mysql.connector
cnx = mysql.connector.connect(
  user = os.getenv("DB_USER"),
  password = os.getenv("DB_PASSWORD"),
  host = "localhost",
  database = "taipei_day_trip"
)
cursor = cnx.cursor()

for item in data:
  cursor.execute(
    "INSERT INTO data VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    (item["id"], item["name"], item["category"], item["description"], item["address"], item["transport"], item["mrt"], item["lat"], item["lng"], json.dumps(item["images"]))
  )
cnx.commit()
cnx.close()