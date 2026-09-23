from dotenv import load_dotenv
from fastapi import HTTPException, Header, Body, FastAPI, Response
import os
from fastapi.middleware.cors import CORSMiddleware
from auth import supabase
from pydantic import BaseModel
from typing import Dict, Any
import jwt
from jwt import PyJWKClient
from io import BytesIO
import pandas as pd
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from datetime import datetime


app = FastAPI()

app.add_middleware(
 CORSMiddleware,
 allow_origins=["http://localhost:5173"],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"]
)

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
 
class JsonData(BaseModel):
 email : str
 senha : str

@app.post("/login")
async def login(data : JsonData):
 try :

  email = data.email
  password = data.senha

  response = supabase.auth.sign_in_with_password({
   "email": email,
   "password": password
  })

  token = response.session.access_token
  user_data = response.user
  
  return {
   "token": token,
   "email" : user_data.email
  }
 except HTTPException:
  raise
 except Exception:
  raise HTTPException(status_code=500, detail="Erro interno ao efetuar login")
 
@app.get("/dados_user")
async def dados_user(authorization : str = Header(...)):
 id_usuário = id_user(authorization)

 if not id_usuário:
  raise HTTPException(status_code=400, detail="Usuário não cadastrado")
 
 user_data = supabase.table("usuarios").select("nome, email").eq("id", id_usuário).single().execute()

 return {
  "nome" : user_data.data["nome"],
  "email": user_data.data["email"]
 }

class DataCliente(BaseModel):
 nome : str
 cpf : str
 telefone : str
 email : str
 empresa : str
 cnpj : str
 segmento : str
 cep : str
 endereco : str
 estado : str
 cidade : str

@app.post("/clientes")
async def add_cliente(authorization : str = Header(...), dados : DataCliente = Body(...)):

 try :
  print("Data",dados)

  cliente = {"id_user": id_user(authorization),
   "nome": dados.nome,
   "cpf": dados.cpf,
   "telefone":dados.telefone,
   "email": dados.email,
   "empresa":dados.empresa,
   "cnpj" : dados.cnpj,
   "segmento" : dados.segmento,
   "cep" : dados.cep,
   "endereco" : dados.endereco,
   "estado" : dados.estado,
   "cidade" : dados.cidade,
   }
  
  print("Cliente", cliente)

  insert = supabase.table("lista_clientes").insert(
  [cliente]
  ).execute()
 
  return {"Status" : "OK",
  "Dados inseridos": insert.data}

 except HTTPException :
   raise
 except Exception as e :
   print("Erro Detalhado", type(e).__name__, str(e))
   raise HTTPException(status_code=500, detail="Erro interno no Sistema")
 
@app.get("/empresas")
async def get_empresas(authorization : str = Header(...)):
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=400, detail="Permissão negada, id inválido!")

 response = supabase.table("lista_clientes").select("empresa").eq("id_user", id).execute()

 empresas = [row["empresa"] for row in response.data]


 return {"empresas": empresas}

class Respostas(BaseModel):
 empresa : str
 notas : Dict[str,Any]

@app.post("/questionario")
async def post_respostas(authorization : str = Header(...), data : Respostas = Body(...)):
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail='Id de usuário inválida')

 insert_data = {
  "id_user" : id,
  "empresa" : data.empresa,
  "respostas" : data.notas
 }

 response_1 = supabase.table("questionarios").upsert([insert_data],on_conflict="empresa, id_user").execute()

 if not response_1.data :
  raise HTTPException(status_code=500, detail="Erro ao inserir no banco")

 return {"Dados Inseridos": response_1.data,
         "Status":"Dados inseridos com sucesso"
         }

@app.get("/dados_clientes")
async def get_dados(authorization : str = Header(...)):
 
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").select("*").eq("id_user",id).execute()

 if response.data is None :
  raise HTTPException(status_code=500, detail="Erro ao buscar dados no banco")

 data_clientes = [
   {
       "nome": row["nome"],
       "cpf": row["cpf"],
       "telefone" : row["telefone"],
       "email" : row["email"],
       "empresa":row["empresa"],
       "segmento": row["segmento"],
       "cnpj": row["cnpj"],
       "cep" : row["cep"],
       "estado" : row["estado"],
       "cidade" : row["cidade"],
       "endereco" : row["endereco"],
       "status" : row["status"]
    }
    for row in response.data
  ]
 
 return {"clientes": data_clientes}

@app.delete("/clientes/{cpf}")
async def deleteClient( cpf : str, authorization : str = Header(...)):
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").delete().eq("cpf",cpf).eq("id_user",id).execute()

 if response.data is None :
  raise HTTPException(status_code=500, detail="Erro ao deletar cliente")
 
 return {"Status": "Cliente deletado com sucesso do banco de dados"}

@app.put("/update_cliente/{cpf}")
async def updateCliente(cpf : str, authorization : str = Header(...), dados : DataCliente = Body(...)):
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").update(dados.model_dump()).eq("cpf", cpf).eq("id_user",id).execute()

 if response.data is None :
  raise HTTPException(status_code=500, detail="Erro ao executar update dos dados")
 
 return {"status":"Dados atualizados com sucesso"}

class Status (BaseModel):
 status : str

@app.patch("/status_cliente/{empresa}")
async def updateStatus(empresa : str, authorization : str = Header(...), cliente : Status = Body(...)):
 id = id_user(authorization)

 if not id : 
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").update(cliente.model_dump()).eq("id_user",id).eq("empresa",empresa).execute()

 if response.data is None :
  raise HTTPException(status_code=500, detail="Erro ao alterar status do cliente")
 
 return {"status":"Status do cliente atualizado com sucesso"}

class Contrato (BaseModel) :
 cpf : str
 valor_mensal : str
 forma_pagamento : str
 tempo_contrato : str

@app.delete("/delete_contrato/{cpf}")
async def delete_contrato(cpf : str, authorization : str = Header(...)) :
 user_id = id_user(authorization)

 if not user_id :
  raise HTTPException(status_code=404, detail="Usuário não autorizado")

 response = supabase.table("contratos").delete().eq("cpf_cliente", cpf).execute()

 if response.data is None :
  raise HTTPException(status_code=500, detail="Contrato não encontrado na tabela")

 return { "status" : "Contrato Deletado com sucesso"}

@app.post("/contrato_cliente")
async def att_contrato(authorization : str = Header(...), contrato : Contrato = Body(...)):
 
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 
 data_contrato = {
  "id_user" : id,
  "cpf_cliente" : contrato.cpf,
  "valor_mensal" : contrato.valor_mensal,
 "forma_pagamento" : contrato.forma_pagamento,
 "tempo_contrato" : contrato.tempo_contrato
 }


 response = supabase.table("contratos").upsert([data_contrato],on_conflict="cpf_cliente").execute()

 if response.data is None :
  raise HTTPException(status_code=500, detail="Erro ao inserir contrato na tabela")
 
 return {"status":"Contrato Inserido com Sucesso"}

@app.get("/dados_contrato")
async def data_contrato(authorization : str = Header(...)):
 
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("contratos").select("*").eq("id_user",id).execute()

 if response.data is None :
  raise HTTPException(status_code=500, detail="Erro ao inserir contrato na tabela")
 

 data = [
  {
   "cpf_cliente": row["cpf_cliente"],
   "valor_mensal": row["valor_mensal"],
   "tempo_contrato": row["tempo_contrato"],
   "forma_pagamento": row["forma_pagamento"],
   "created_at" : row["created_at"]
  }
  for row in response.data
 ]

 return {"contrato": data}

class Dados_Validacao (BaseModel):
 empresa : str
 validacao : Dict[str, Any]

@app.post("/gerar_excel")
async def gerar_excel(authorization : str = Header(...), dados : Dados_Validacao = Body(...)) :
 
 id = id_user(authorization)

 if not id :
   raise HTTPException(status_code=404, detail="Usuário não encontrado")

 estrutura_final = {}

 for pilar, data in dados.validacao.items() :
  estrutura_final[pilar] = []

  for bloco, dado in data.items() :
   if type(dado) == str :
    continue
   for pergunta, resposta in dado.items():
    estrutura_final[pilar].append({"Bloco": bloco, "Pergunta" : pergunta, "Resposta" : resposta})

 buffer = BytesIO()

 with pd.ExcelWriter(buffer, engine='openpyxl') as writer :
  for pilar, data in estrutura_final.items():
   df = pd.DataFrame(data)
   df.to_excel(writer, index=False, sheet_name=pilar)

 return Response(
  content=buffer.getvalue(),
  media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  headers={"Content-Disposition": f"attachment; filename=diagnostico_{dados.empresa}.xlsx"}
)
 
@app.get("/clientes_fechados")
async def get_dados(authorization : str = Header(...)):
 
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").select("*").eq("id_user",id).eq("status","contratado").execute()

 if response.data is None :
  raise HTTPException(status_code=500, detail="Erro ao buscar dados no banco")

 data_clientes = [
   {
       "nome": row["nome"],
       "cpf": row["cpf"],
       "telefone" : row["telefone"],
       "email" : row["email"],
       "empresa":row["empresa"],
       "segmento": row["segmento"],
       "cnpj": row["cnpj"],
       "cep" : row["cep"],
       "estado" : row["estado"],
       "cidade" : row["cidade"],
       "endereco" : row["endereco"],
       "status" : row["status"]
    }
    for row in response.data
  ]
 
 return {"clientes": data_clientes}

@app.get("/notas_questionario/{empresa}")
async def get_notas (empresa : str, authorization : str = Header(...)) :
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Usuário não encontrado")

 response = supabase.table("questionarios").select("respostas, conclusao, updated_at").eq("id_user", id).eq("empresa", empresa).execute()

 if not response.data:
  raise HTTPException(status_code=500, detail="Erro ao consultar respostas da empresa na tabela")


 notas_pilares = response.data[0]["respostas"]
 conclusao = response.data[0]["conclusao"]
 data_update = response.data[0]["updated_at"]

 return {
  "notas" : notas_pilares,
  "conclusao" : conclusao,
  "updated_at": data_update
 }

class Conclusao (BaseModel) : 
 conclusao : str

@app.patch("/data_conclusao/{empresa}")
async def insert_conclusao(empresa : str, authorization : str = Header(...), data : Conclusao = Body(...) ) :
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Usuário não encontrado")


 response = supabase.table("questionarios").update({"conclusao" : data.conclusao, "updated_at" : str(datetime.now())}).eq("empresa", empresa).eq("id_user", id).execute()

 if not response.data:
  raise HTTPException(status_code=409, detail="Erro ao inserir conclusão na tabela")

 return {"status" : "Conclusão inserida com sucesso"}



 


 
 

