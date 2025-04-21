import os, json
import urllib.request as req
PARTNER_KEY = os.getenv("PARTNER_KEY")
MERCHANT_ID = "threeseven21_FUBON_POS_2"
PAYMENT_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"


def pay_by_prime(body:dict) -> dict:
	PRIME = body["prime"]
	payload = {
    "prime": PRIME,
    "partner_key": PARTNER_KEY,
    "merchant_id": MERCHANT_ID,
    "details":"Taipei Day Trip",
    "amount": body["order"]["price"],
    "cardholder": {
      "phone_number": body["order"]["contact"]["phone"],
      "name": body["order"]["contact"]["name"],
      "email": body["order"]["contact"]["email"],
    }
  }
	request = req.Request(
    PAYMENT_URL,
    headers={
      "Content-Type": "application/json",
      "x-api-key": PARTNER_KEY,
    },
    data=json.dumps(payload).encode(),
  )
	with req.urlopen(request) as res:
		res_data = json.load(res)
	return res_data