*Data : 14/10/2026*
*Status : Aceito*

# Contexto #
Na arquitetura do banco de dados, as 3 tabelas: lista_clientes, contratos e questionarios, estavam interligadas por :
lista_clientes - contratos - (cpf_cliente - que residia como coluna nas 2 tabelas)
lista_clientes - questionario - (empresa - que residia como colunas nas 2 tabelas)
Esse tipo de arquitetura é frágil devido ao fato de que poderia haver empresas cadastradas acidentalmente com mesmo nome ou clientes cadastrados erroneamente com mesmo cpf.

# Opções e Decisão tomada #
A decisão válida nos dois cenários é adicionar uma constraint unique ao CPF, o que o torna uma chave candidata legitima. Agora há duas escolhas que residem justamente na escolha da FK nas tabelas contratos e questionarios : 
- A primeira opção é tornar o CPF uma FK. Porém, por ser uma chave natural, ela pode mudar, e isso acarretaria uma alteração de todas as tabelas que estivessem relacionadas ao cliente. Ademais, apenas para citação, seria necessário criar uma coluna cpf_cliente na tabela questionario, já que o elo anterior era feito pela coluna empresa.
- A segunda opção, que é a mais válida e que foi a tomada, é determinar o id, da entidade cliente na tabela lista_clientes, como FK. Dessa forma, a coluna empresa, presente na tabela questionario, pode ser apagada, bem como a coluna cpf_cliente da tabela contratos. 
Ademais à segunda decisão, adicionei uma ação RESTRICT na FK cliente_id da tabela contratos, isso significa que clientes com contratos não poderão ser deletados, e também acrescentei uma constraint UNIQUE a FK da tabela, ou seja, ao tentar inserir um novo contrato, caso houver um contrato que aponte para o mesmo cliente_id, ele será sobreescrito. Logo o UNIQUE no cliente_id é o que torna possível o on_conflict, e juntos o insert virá atualização. Porém, nesse cenário o histórico de contratos do cliente não persiste.
Na FK, cliente_id, da tabela questionarios, adicionei a ação de CASCADE, logo questionarios de clientes deletados não irão persistir na tabela como histórico. A constraint UNIQUE também está presente no cliente_id, garantindo o mesmo processo da tabela anterior, bem como a mesma consequência de perca de histórico, nesse caso de questionário.

# Consequências da decisão #
Agora as tabelas possuem um relacionamento robusto, tendo em vista que  a relação anterior entre elas era frágil, pois estava estabelecida em colunas que não representavam FK verdadeiras, além do fato de não terem uma constraint UNIQUE.
Essa nova característica fornece uma maior precisão de relação entre clientes - contratos - questionários de consultoria, o que facilita o trabalho assertivo do consultor ao utilizar o sistema.