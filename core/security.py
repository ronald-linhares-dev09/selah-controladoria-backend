import os
from fastapi import HTTPException, Header
from jwt import PyJWKClient
from fastapi.security import HTTPBasicCredentials, HTTPBearer
import jwt

SUPABASE_URL = os.environ.get("URL_SUPABASE")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
jwks_client = PyJWKClient(JWKS_URL, cache_keys=True)
schema_security = HTTPBearer()

def id_user(authorization: str = Header(...)):
 
  if not authorization.startswith("Bearer "):
     raise HTTPException(status_code=401, detail='Token Inválido')
   
  token = authorization.split(" ")[1]

  try:
   signing_assinature_key = jwks_client.get_signing_key_from_jwt(token)


   payload = jwt.decode(
     token,
     algorithms=['ES256'],
     key=signing_assinature_key,
     audience='authenticated'
   )

  except jwt.PyJWKClientError :
        raise HTTPException(status_code=401, detail='Formato de token inválido')

  except jwt.ExpiredSignatureError :
        raise HTTPException(status_code=401, detail='Token Expirado')
    
  except jwt.InvalidTokenError :
         raise HTTPException(status_code=401, detail='Token Expirado ou inválido')

  user_id = payload.get("sub")

  if not user_id :
     raise HTTPException(status_code=401, detail='Token sem id de usuário')
 
  return user_id