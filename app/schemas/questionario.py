from pydantic import BaseModel
from typing import Dict, Any
from fpdf import FPDF
from datetime import date

class Conclusao (BaseModel) : 
 conclusao : str

class Respostas(BaseModel):
 empresa : str
 notas : Dict[str,Any]
 cliente_id : str

class Dados_Validacao (BaseModel):
 empresa : str
 validacao : Dict[str, Any]

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