*Data : 14/10/2026*
*Status : Aceito*

# Contexto #
Na versão incial da API, todas as rotas, bem como a função de autenticação e extração do id do usuário, estavam alocadas no arquivo main.py. Nesse caso, não havia separação de endpoints por tabelas e entidades do banco, ou seja, rotas para a tabela lista_clientes, contratos e questionario estavam no mesmo local. Esse modelo de organização traz dificuldades quanto ao tempo gasto para ajustar uma rota específica ou até rotas relacionadas a uma mesma entidade. Além disso, os schemas específicos de cada entidade estavam inseridos no arquivo, o que torna maior o nível de densidade do arquivo.

# Opções e Decisão #
O versionamento poderia ser feito separando as rotas em camadas, mas sem nomea-las com /v1. A decisão facilitaria ajustes nos endpoints, devido a divisão em camadas, mas não traria especificidade quanto ao processo de versionamento. Além do fato de que, não poderia haver nenhum endpoint com o mesmo path, pois haveria conflito.
Nesse contexto, há também a possibilidade de realizar a divisão em camadas, endereçando as rotas para um folder específco separado por entidade, bem como os schemas e a função de autenticação. Bem como, versionar as rotas, nomeando-as com '/v1'.
Para isso criei a seguinte relação de pastas no arquivo :
- routers - clientes.py, contratos.py, questionario.py (rotas)
- core - security.py (autenticação)
- schemas - clientes.py, contratos.py, questionario.py (Objetos pydantic)

# Consequências da Decisão #
Esse versionamento resolve justamente o problema da dificuldade de alterações nos endpoints, oferecendo agilidade se necessário for alterar algum elemento no endpoint, ou alterar algum schema referente ao endpoint. Em caso de possíveis alterações, basta apenas alterar o include_router no main.py para a versão seguinte da rota, no caso '/v2', mantendo as versões antigas '/v1' até todas as validações serem concluídas.
Para essa implementação, utilizei a técnica de **expand and contract** : 
- Criei as novas rotas como uma versão v1 da API, realizei a adaptação do frontend para a nova versão e testei por alguns dias. 
- Posteriomente, com a validação feita, fiz uma limpeza nas rotas antigas - já que no momento, não havia nenhum usuário que as utilizasse, e mantive no main.py apenas a inclusão das rotas provenientes do folder routers. Nesse processo, utilizei o APIRouter para a importação das rotas de cada entidade do banco.