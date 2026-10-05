from main import RelatorioSelah, Dados_Indicadores

indicadores = Dados_Indicadores(**{
    "empresa": "Metalúrgica Horizonte",
    "ims": {
        "geral": {"valor": 58, "classificacao": "Em Estruturação"},
        "mais_maduro": {"nome": "Financeiro", "valor": 79, "classificacao": "Gerenciado"},
        "mais_fragil": {"nome": "Tecnologia", "valor": 34, "classificacao": "Fragilizado"},
    },
    "ics": {
        "geral": {"valor": 22, "classificacao": "Em Atenção"},
        "mais_saudavel": {
            "nome": "Financeiro → Comercial",
            "valor": 6,
            "classificacao": "Saudável",
        },
        "mais_fragil": {
            "nome": "Tecnologia → Clientes",
            "valor": 45,
            "classificacao": "Crítica",
        },
    },
    "conclusao": (
        "A empresa apresenta base financeira sólida, com controles consistentes e "
        "disciplina de acompanhamento. O desalinhamento mais relevante está entre a "
        "área de tecnologia e a experiência do cliente, onde a diferença de maturidade "
        "indica que decisões operacionais vêm sendo tomadas sem apoio de informação "
        "estruturada. Recomenda-se priorizar a padronização dos registros de atendimento "
        "antes de avançar em novas frentes comerciais."
    ),
})

pdf = RelatorioSelah(empresa=indicadores.empresa, consultor='Ronald Assis', telefone='44 9 9717-7332', cidade="Cianorte", estado="Paraná")

pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf')
pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf')

pdf.alias_nb_pages()
pdf.set_top_margin(45)
pdf.add_page()
pdf.ln(20)

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

pdf.card(x=10, y=h_cards, indicador='ims', titulo='IMS Geral', valor=ims.geral.valor, classificacao=ims.geral.classificacao)
pdf.card(x=10 + 1 * 65, y=h_cards, indicador='ims', titulo=ims.mais_maduro.nome, valor=ims.mais_maduro.valor, classificacao=ims.mais_maduro.classificacao)
pdf.card(x=10 + 2 * 65, y=h_cards, indicador='ims', titulo=ims.mais_fragil.nome, valor=ims.mais_fragil.valor, classificacao=ims.mais_fragilclassificacao)

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

pdf.card(x=10, y=h_cards, indicador='ics', titulo='ICS Geral', valor=ics.geral.valor, classificacao=ics.geral.classificacao)
pdf.card(x=10 + 1 * 65, y=h_cards, indicador='ics', titulo=ics.mais_saudavel.nome, valor=ics.mais_saudavel.valor, classificacao=ics.mais_saudavel.classificacao)
pdf.card(x=10 + 2 * 65, y=h_cards, indicador='ics', titulo=ics.mais_fragil.nome, valor=ics.mais_fragil.valor, classificacao=ics.mais_fragil.classificacao)

pdf.set_y(h_cards + 35)

pdf.set_font('DejaVu', 'B', 13)
pdf.cell(0, 8,"Conclusão do Consultor", new_x='LMARGIN', new_y='NEXT')

pdf.set_font('DejaVu', '', 8)
pdf.multi_cell(0, 5, f'{indicadores.conclusao}')

pdf.output('teste_pdf.pdf')

