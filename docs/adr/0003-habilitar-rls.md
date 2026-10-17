*Data : 14/10/2026*
*Status : Aceito*

# Contexto # 
O RLS de todas as 3 tabelas : lista_clientes, contratos e questionario, estava desativado. Logo, tendo em vista que a ANON_KEY é pública, requisições poderiam ser feitas ao banco de posse dessa chave, comprometendo a segurança dos dados dos clientes.

# Opções #
Mediante a isso, a opção de ativação da RLS era obrigatória, a fim de restringir esse acesso, tendo em vista que o RLS bloqueia requests com a chave pública. Posteriomente, era possível criar políticas específicas para cada tabela, ou apenas manter a ativação da RLS.

# Decisão e consequência #
Optei por apenas ativar a RLS em cada tabela do banco, já que dessa forma operações no banco só poderão ser feitas via service role (chave que a RLS não bloqueia), que está apenas presente no backend. Ou seja, as operações só são feitas pelo backend, e a validação via JWT presente no backend, garante que só irá acessar o banco queme está autenticado.
Dessa forma, garanto uma proteção "frontal" com fastAPI, e uma proteção na "porta dos fundos" com RLS.
