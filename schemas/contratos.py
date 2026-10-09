from pydantic import BaseModel

class Contrato (BaseModel) :
 cliente_id : str
 valor_mensal : str
 forma_pagamento : str
 tempo_contrato : str