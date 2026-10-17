from pydantic import BaseModel

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

class Status (BaseModel):
 status : str

