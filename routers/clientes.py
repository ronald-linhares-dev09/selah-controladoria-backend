from fastapi import APIRouter, Header, Body, Depends, HTTPException
from auth import supabase
from schemas.clientes import DataCliente, Status
from core.security import id_user

router_v1 = APIRouter(
 prefix='/clientes',
 tags=['clientes'],
)

def get_dados():

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

@router_v1.post("")
async def add_cliente(dados : DataCliente = Body(...), user_id  : str = Depends(id_user),):

  if not user_id :
   raise HTTPException(status_code=401, detail='ID de usuário inválido')

  cliente = {"id_user": user_id,
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
 
@router_v1.get("")
async def get_dados(status : str | None = None , fields : str | None  = None, user_id  : str = Depends(id_user),):

 if not user_id :
  raise HTTPException(status_code=401, detail="Id de usuário inválido")

 if status is not None:
  get_dados()

 if fields is not None:
  response = supabase.table("lista_clientes").select("empresa").eq("id_user", user_id).execute()
  
  empresas = [row["empresa"] for row in response.data]
  
  
  return {"empresas": empresas}
  
 response = supabase.table("lista_clientes").select("*").eq("id_user",user_id).execute()

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

@router_v1.delete("/{cliente_id}")
async def deleteClient( cliente_id : str, user_id  : str = Depends(id_user)):

 if not user_id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").delete().eq("id",cliente_id).eq("id_user",user_id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Erro ao deletar cliente : Cliente não encontrado")
 
 return {"Status": "Cliente deletado com sucesso do banco de dados"}

@router_v1.put("/{cliente_id}")
async def updateCliente(cliente_id : str, user_id  : str = Depends(id_user), dados : DataCliente = Body(...)):

 if not user_id :
  raise HTTPException(status_code=401, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").update(dados.model_dump()).eq("id", cliente_id).eq("id_user",user_id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Cliente não encontrado no banco de dados")
 
 return {"status":"Dados atualizados com sucesso"}

@router_v1.patch("/{cliente_id}/status")
async def updateStatus(cliente_id : str, user_id  : str = Depends(id_user), cliente : Status = Body(...)):

 if not user_id : 
  raise HTTPException(status_code=401, detail="Id de usuário inválido")
 
 response = supabase.table("lista_clientes").update(cliente.model_dump()).eq("id_user",user_id).eq("id",cliente_id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Cliente não encontrado")
 
 return {"status":"Status do cliente atualizado com sucesso"}
