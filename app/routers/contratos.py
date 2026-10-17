from fastapi import APIRouter, Header, Body, Depends, HTTPException
from auth import supabase
from schemas.clientes import DataCliente, Status
from core.security import id_user
from schemas.contratos import Contrato

router_v1 = APIRouter(
 prefix='/contratos',
 tags=['contratos'],
)

@router_v1.delete("/{cliente_id}")
async def delete_contrato(cliente_id : str, user_id  : str = Depends(id_user)) :

 if not user_id :
  raise HTTPException(status_code=401, detail="Usuário não autorizado")

 response = supabase.table("contratos").delete().eq("cliente_id", cliente_id).execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Contrato não encontrado na tabela")

 return { "status" : "Contrato Deletado com sucesso"}

@router_v1.post("")
async def att_contrato(user_id  : str = Depends(id_user), contrato : Contrato = Body(...)):
 

 if not user_id:
  raise HTTPException(status_code=401, detail="Id de usuário inválido")
 
 
 data_contrato = {
  "id_user" : user_id,
  "cliente_id" : contrato.cliente_id,
  "valor_mensal" : contrato.valor_mensal,
  "forma_pagamento" : contrato.forma_pagamento,
  "tempo_contrato" : contrato.tempo_contrato
 }


 response = supabase.table("contratos").upsert([data_contrato],on_conflict="cliente_id").execute()

 if response.data is None :
  raise HTTPException(status_code=404, detail="Contrato não encontrado")
 
 return {"status":"Contrato Inserido com Sucesso"}

@router_v1.get("")
async def data_contrato(user_id  : str = Depends(id_user)):
 

 if not user_id :
  raise HTTPException(status_code=404, detail="Id de usuário inválido")
 
 response = supabase.table("contratos").select("*").eq("id_user",user_id).execute()

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
