from fastapi import Header
import jwt, os


class AuthError(Exception):
	pass


async def jwt_payload(authorization:str=Header()):
  try:
    [scheme, token] = authorization.split()
    payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    payload.pop("exp")
    return payload
  except:
    return None
async def jwt_auth(authorization:str=Header()):
  try:
    [scheme, token] = authorization.split()
    payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    payload.pop("exp")
    return payload
  except:
    raise AuthError


