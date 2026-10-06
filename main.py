from dotenv import load_dotenv
from fastapi import HTTPException, Header, Body, FastAPI, Response, Request
from postgrest import APIError
from fastapi.responses import JSONResponse
import os
from fastapi.middleware.cors import CORSMiddleware
from auth import supabase
from pydantic import BaseModel
from typing import Dict, Any, List
import jwt
from jwt import PyJWKClient
from io import BytesIO
import pandas as pd
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from datetime import datetime, date
from fpdf import FPDF


app = FastAPI()

app.add_middleware(
 CORSMiddleware,
 allow_origins=[
    "https://www.selahconsultoria.com.br",
    "https://selahconsultoria.com.br",
    "http://localhost:5174",
    "http://localhost:5173"
],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"]
)

ERROR = {
 "23505" : (409, "Já existe um registro para esse valor"),
 "23503" : (409, "Operação bloqueada : existe outro registro vinculado"),
 "23514" : (422, "Valor inválido para esse campo"),
}

@app.exception_handler(APIError)
async def tratar_erro(request : Request, exc : APIError):
 code = exc.code
 status, mensagem = ERROR.get(code,(500, "Erro ao consultar o banco de dados"))
 return JSONResponse(status_code=status, content={'detail' : mensagem})


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
  raise HTTPException(status_code=401, detail="Credenciais Inválidas")

@app.get("/dados_user")
async def dados_user(authorization : str = Header(...)):
 id_usuário = id_user(authorization)

 if not id_usuário:
  raise HTTPException(status_code=401, detail="Usuário não cadastrado")
 
 user_data = supabase.table("usuarios").select("nome, email").eq("id", id_usuário).single().execute()

 return {
  "nome" : user_data.data["nome"],
  "email": user_data.data["email"],
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

  id = id_user(authorization)

  if not id :
   raise HTTPException(status_code=401, detail='ID de usuário inválido')

  cliente = {"id_user": id,
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
  

  insert = supabase.table("lista_clientes").insert(
  [cliente]
  ).execute()

  return {"Status" : "OK",
  "Dados inseridos": insert.data}
 
@app.get("/empresas")
async def get_empresas(authorization : str = Header(...)):
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=401, detail="Permissão negada, id inválido!")

 response = supabase.table("lista_clientes").select("empresa").eq("id_user", id).execute()

 empresas = [row["empresa"] for row in response.data]


 return {"empresas": empresas}

class Respostas(BaseModel):
 empresa : str
 notas : Dict[str,Any]
 cliente_id : str

@app.post("/questionario")
async def post_respostas(authorization : str = Header(...), data : Respostas = Body(...)):
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=401, detail='Id de usuário inválida')

 insert_data = {
  "id_user" : id,
  'cliente_id' : data.cliente_id,
  "empresa" : data.empresa,
  "respostas" : data.notas
 }

 response_1 = supabase.table("questionarios").upsert([insert_data],on_conflict="cliente_id").execute()

 if response_1.data is None :
  raise HTTPException(status_code=404, detail="Questionário não encontrado no banco")

 return {"Dados Inseridos": response_1.data,
         "Status":"Dados inseridos com sucesso"
         }

@app.get("/dados_clientes")
async def get_dados(authorization : str = Header(...)):
 
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=401, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").select("*").eq("id_user",id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Clientes não encontrados no banco")

 data_clientes = [
   {
      "id" : row["id"],
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

@app.delete("/clientes/{cliente_id}")
async def deleteClient( cliente_id : str, authorization : str = Header(...)):
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").delete().eq("id",cliente_id).eq("id_user",id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Erro ao deletar cliente : Cliente não encontrado")
 
 return {"Status": "Cliente deletado com sucesso do banco de dados"}

@app.put("/update_cliente/{cliente_id}")
async def updateCliente(cliente_id : str, authorization : str = Header(...), dados : DataCliente = Body(...)):
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=401, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").update(dados.model_dump()).eq("id", cliente_id).eq("id_user",id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Cliente não encontrado no banco de dados")
 
 return {"status":"Dados atualizados com sucesso"}

class Status (BaseModel):
 status : str

@app.patch("/status_cliente/{cliente_id}")
async def updateStatus(cliente_id : str, authorization : str = Header(...), cliente : Status = Body(...)):
 id = id_user(authorization)

 if not id : 
  raise HTTPException(status_code=401, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").update(cliente.model_dump()).eq("id_user",id).eq("id",cliente_id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Cliente não encontrado")
 
 return {"status":"Status do cliente atualizado com sucesso"}

class Contrato (BaseModel) :
 cliente_id : str
 valor_mensal : str
 forma_pagamento : str
 tempo_contrato : str

@app.delete("/delete_contrato/{cliente_id}")
async def delete_contrato(cliente_id : str, authorization : str = Header(...)) :
 user_id = id_user(authorization)

 if not user_id :
  raise HTTPException(status_code=401, detail="Usuário não autorizado")

 response = supabase.table("contratos").delete().eq("cliente_id", cliente_id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Contrato não encontrado na tabela")

 return { "status" : "Contrato Deletado com sucesso"}

@app.post("/contrato_cliente")
async def att_contrato(authorization : str = Header(...), contrato : Contrato = Body(...)):
 
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=401, detail="Id de usuário inválido")
 
 
 data_contrato = {
  "id_user" : id,
  "cliente_id" : contrato.cliente_id,
  "valor_mensal" : contrato.valor_mensal,
  "forma_pagamento" : contrato.forma_pagamento,
  "tempo_contrato" : contrato.tempo_contrato
 }


 response = supabase.table("contratos").upsert([data_contrato],on_conflict="cliente_id").execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Contrato não encontrado")
 
 return {"status":"Contrato Inserido com Sucesso"}

@app.get("/dados_contrato")
async def data_contrato(authorization : str = Header(...)):
 
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("contratos").select("*").eq("id_user",id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Contratos não encontrados")
 

 data = [
  {
   "cliente_id": row["cliente_id"],
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

class IndicadoresProps(BaseModel):
 nome : str
 valor : int
 classificacao : str

class IndicadorGeral(BaseModel):
 valor : int
 classificacao : str

class IMS(BaseModel):
 geral : IndicadorGeral
 mais_maduro : IndicadoresProps
 mais_fragil : IndicadoresProps

class ICS(BaseModel):
 geral : IndicadorGeral
 mais_saudavel : IndicadoresProps
 mais_fragil : IndicadoresProps

class Dados_Indicadores(BaseModel):
 empresa : str
 ims : IMS
 ics : ICS
 conclusao : str

class RelatorioSelah(FPDF):
 def __init__(self, empresa : str, consultor : str, email : str, telefone : str, estado : str, cidade : str):
  super().__init__()
  self.empresa = empresa
  self.consultor = consultor
  self.email = email
  self.telefone = telefone
  self.estado = estado
  self.cidade = cidade

 def header(self):
   self.image('assets/LogoSelah.png', x=160, y=0, w=30)
   self.set_font('DejaVu', 'B', 18)
   self.set_text_color(0,0,0)
   self.set_xy(10,10)
   self.cell(100,8 ,'Diagnóstico Estratégico', new_x='LMARGIN', new_y='NEXT')

   self.set_font('DejaVu', '', 8)
   self.cell(0 , 6, f'Empresa : {self.empresa}')

   self.set_draw_color(0,0,0)
   self.set_line_width(0.3)
   self.line(0, 30, 300, 30)

   self.set_draw_color(16, 185, 129)
   self.line(0, 31.2, 200, 31.2)

   self.set_y(40)

 def card(self, x, y, titulo, valor, classificacao):
    ALTURA = 30
    LARGURA = 60

    self.set_draw_color(180, 180, 180)
    self.set_line_width(0.3)
    self.rect(x, y, LARGURA, ALTURA)

    self.set_xy(x, y + 2)
    self.set_font('DeJaVu', 'B', 9)
    self.set_text_color(90,90,90)
    self.cell(60, 5, F'{titulo}', align='C')

    self.set_xy(x, y + 13)
    self.set_font('DeJaVu', '', 18)
    self.set_text_color(0,0,0)
    self.cell(60, 5, f'{valor}', align='C')

    self.set_xy(x, y + 24)
    self.set_font('DeJaVu', 'B', 9)
    self.set_text_color(60,60,60)
    self.cell(60, 5, f'{classificacao}', align='C')


 def footer(self):
   y_linha = self.h - 24
   self.set_draw_color(0,0,0)
   self.set_line_width(0.3)
   self.line(0, y_linha, 300, y_linha)
   
   self.set_draw_color(16, 185, 129)
   self.line(0, y_linha + 1.2, 200, y_linha + 1.2)

   self.set_y(-18)
   self.set_font('DejaVu', "", 8)
   self.set_text_color(120, 120, 120)

   texto_footer = f'Consultor {self.consultor} · Contato {self.telefone} · {self.cidade} - {self.estado} · Email {self.email}'
   self.cell(0, 5, texto_footer, new_x='LMARGIN', new_y='NEXT')
   self.cell(0 , 5, f'Data : {date.today().strftime("%d-%m-%Y")}', align='L')
   self.cell(5, 5, f'Página {self.page_no()} de {{nb}}', align='R')

@app.post('/gerar_pdf')
async def gerar_pdf(authorization : str = Header(...), indicadores : Dados_Indicadores = Body(...)):
  id = id_user(authorization)

  if not id :
   raise HTTPException(status_code=404, detail='ID de usuário inválido')

  query = supabase.table('usuarios').select("nome, email, telefone, estado, cidade").eq("id", id).execute()

  if not query.data :
   raise HTTPException(status_code=400, detail="Dados de usuário não encontrados")

  pdf = RelatorioSelah(empresa=indicadores.empresa, 
      consultor=query.data[0]['nome'], email=query.data[0]['email'], telefone=query.data[0]['telefone'], 
      cidade=query.data[0]['cidade'], estado=query.data[0]['estado']
  )

  pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf')
  pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf')

  pdf.alias_nb_pages()
  pdf.set_top_margin(20)
  pdf.set_auto_page_break(auto=True, margin=32)
  pdf.add_page()

  pdf.set_font('DejaVu', 'B', 13)
  pdf.set_text_color(0,0,0)
  pdf.cell(0, 8, "IMS - Índice de Maturidade Selah", new_x='LMARGIN', new_y='NEXT')

  pdf.set_font('DejaVu', '', 8)
  pdf.multi_cell(0, 6, 
  "O índice de maturidade mede : estrutura, organização, processos, gestão e disciplina operacional. Seu objetivo não é medir resultados, e sim a capacidade de gestão", 
  new_x='LMARGIN', new_y='NEXT'
  )
  pdf.ln(4)

  h_cards = pdf.get_y()
  ims = indicadores.ims

  pdf.card(x=10, y=h_cards, titulo='IMS Geral', valor=f'{ims.geral.valor}%', classificacao=ims.geral.classificacao)
  pdf.card(x=10 + 1 * 65, y=h_cards, titulo=ims.mais_maduro.nome, valor=f'{ims.mais_maduro.valor}%', classificacao=ims.mais_maduro.classificacao)
  pdf.card(x=10 + 2 * 65, y=h_cards, titulo=ims.mais_fragil.nome, valor=f'{ims.mais_fragil.valor}%', classificacao=ims.mais_fragil.classificacao)

  pdf.set_y(h_cards + 35)

  pdf.set_font('DejaVu', 'B', 13)
  pdf.set_text_color(0,0,0)
  pdf.cell(0, 8, "ICS - Índice de Conexões Selah", new_x='LMARGIN', new_y='NEXT')

  pdf.set_font('DejaVu', '', 8)
  pdf.multi_cell(0, 6, 
  "O índice tem o objetivo de mostrar onde está a verdade que a empresa ainda não consegue enxergar. O ICS analisa conexões e mede o alinhamento da empresa, identificando possíveis rupturas", 
  new_x='LMARGIN', new_y='NEXT'
  )
  pdf.ln(4)

  h_cards = pdf.get_y()
  ics = indicadores.ics

  pdf.card(x=10, y=h_cards, titulo='ICS Geral', valor=f'{ics.geral.valor}pts', classificacao=ics.geral.classificacao)
  pdf.card(x=10 + 1 * 65, y=h_cards, titulo=ics.mais_saudavel.nome, valor=f'{ics.mais_saudavel.valor}pts', classificacao=ics.mais_saudavel.classificacao)
  pdf.card(x=10 + 2 * 65, y=h_cards, titulo=ics.mais_fragil.nome, valor=f'{ics.mais_fragil.valor}pts', classificacao=ics.mais_fragil.classificacao)

  pdf.set_y(h_cards + 35)

  pdf.set_font('DejaVu', 'B', 13)
  pdf.cell(0, 8,"Conclusão do Consultor", new_x='LMARGIN', new_y='NEXT')

  pdf.set_font('DejaVu', '', 8)
  pdf.multi_cell(0, 5, f'{indicadores.conclusao}')

  pdf_bytes = bytes(pdf.output())

  return Response (
      content=pdf_bytes,
      media_type='application/pdf',
      headers={"Content-Disposition" : f"attachment; filename=diagnostico_{indicadores.empresa}.pdf"}
  )

@app.get("/clientes_fechados")
async def get_dados(authorization : str = Header(...)):
 
 id = id_user(authorization)

 if not id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").select("*").eq("id_user",id).eq("status","contratado").execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Clientes não encontrados")

 data_clientes = [
   {
       "id" : row['id'],
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

@app.get("/notas_questionario/{id}")
async def get_notas (id : str, authorization : str = Header(...)) :
 user_id = id_user(authorization)

 if not user_id :
  raise HTTPException(status_code=404, detail="Usuário não encontrado")

 response = supabase.table("questionarios").select("respostas, conclusao, updated_at").eq("id_user", user_id).eq("cliente_id", id).execute()

 if not response.data:
  raise HTTPException(status_code=404, detail="Questionário não encontrado")


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

@app.patch("/data_conclusao/{id}")
async def insert_conclusao(id : str, authorization : str = Header(...), data : Conclusao = Body(...) ) :
 user_id = id_user(authorization)

 if not user_id :
  raise HTTPException(status_code=404, detail="Usuário não encontrado")

 updated_at = str(datetime.now())

 response = supabase.table("questionarios").update({"conclusao" : data.conclusao, "updated_at" : updated_at}).eq("cliente_id", id).eq("id_user", user_id).execute()

 if not response.data:
  raise HTTPException(status_code=404, detail="Questionário não encontrado")

 return {
        "status" : "Conclusão inserida com sucesso",
         "updated" : updated_at
  }



 


 
 

