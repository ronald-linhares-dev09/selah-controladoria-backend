from fastapi import APIRouter, Header, Body, Depends, HTTPException,Response
from auth import supabase
from schemas.clientes import DataCliente, Status
from core.security import id_user
import pandas as pd
from io import BytesIO
from schemas.questionario import *
from datetime import datetime
from fastapi.responses import JSONResponse

router_v1 = APIRouter(
    prefix='/questionarios',
    tags=['questionarios'],
)

@router_v1.post("")
async def post_respostas(id  : str = [Depends(id_user)], data : Respostas = Body(...)):

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

@router_v1.get("/{id}/notas")
async def get_notas (id : str, user_id  : str = [Depends(id_user)]) :


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

@router_v1.patch("/{id}/data_conclusao")
async def insert_conclusao(id : str, user_id  : str = [Depends(id_user)], data : Conclusao = Body(...) ) :

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

@router_v1.post('/{id}/relatorio.pdf')
async def gerar_pdf(id  : str = [Depends(id_user)], indicadores : Dados_Indicadores = Body(...)):

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

@router_v1.post("/{id}/planilha.xlsx")
async def gerar_excel(id  : str = [Depends(id_user)], dados : Dados_Validacao = Body(...)) :
 

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