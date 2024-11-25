from openAIConfig.openaiInit import initializeOpenAI

client = initializeOpenAI()

def querycreator(data, question):

    query = f"""Você é uma assistente virtual para me ajudar com dados do meu comércio, abaixo tem os dados do meu comércio
    Nos dados que terá acesso lembresse de nunca trazer informações na sua resposta que sejam IDs, nem ID de vendas ou produtos, nada, apenas códigos, opte por códigos 
    ou outras informações úteis, tente trazer também respostas mais curtas e objetivas, porém que sejam prestativas, por exemplo, se eu lhe pedir o .
    meu produto mais caro, você me responde com o código do produto, seu preço de custo e seu preço de venda, etc.
    
    Article:
    \"\"\"
    {data}
    \"\"\"

    Question: {question}"""

    response = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': 'Sua resposta sobre meu comércio.'},
            {'role': 'user', 'content': query},
        ],
        model="gpt-4o",
        temperature=0,
    )
    iareturn = response.choices[0].message.content
    return iareturn

def queryNCMcreator(data, question):
    query = f"""Você é um buscador de NCMs na nossa base de dados, vamos te entregar dados onde vai aparecer a descrição de um NCM e o NCM me si, sempre sem pontuação
    e você vai sempre, sem exceções responder com apenas o número do NCM sem pontos, então por exemplo, você vai receber como question o nome do produto coca cola 2l, 
    vai buscar pelo NCM mais apropriado através da descrição e retornar o número do NCM sem pontuação, relembrando sem pontuação, só os números, no seu output, e você
    não vai responder "olá o NCM é 000000" por exemplo, você só vai responder "000000" nada mais, o número do NCM e completamente nada além disso, o seu output é somente o número do NCM e nada mais!!!
    

        tabela de NCMs:
        \"\"\"
        {data}
        \"\"\"

        Question: {question}"""

    response = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': 'Sua resposta sobre meu comércio.'},
            {'role': 'user', 'content': query},
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )
    iareturn = response.choices[0].message.content
    return iareturn

def interpret_question(question):
    prompt = f"""
Você é um assistente que interpreta perguntas em linguagem natural e as converte em um SQL, e somente um SQL para resposta, que sera usado para uma busca
direta no banco de dados do cliente, toda a estrutura do banco de dados do cliente está abaixo, lembrando que vocÊ só pode retornar um sql e literalmente nada a mais
sua respost ajá vai direto para a consulta no DB.
Abaixo estará as estruturas do banco de dados do cliente divididas por tables e seus campos, é um banco de dados firebird:

Vendas:
	Table VENDAS
		ID
		VENDA
		STATUS
		DATA_EMISSAO (Formato ex: 30.12.2024 00:00)
		ID_CLIENTE
		CLIENTE_NOME
		TOTAL_PRODUTOS
		DESCONTO
		TOTAL_VENDA
	Table VENDAS_ITENS
		ID_VENDA
		ID_PRODUTO
		PRODUTO_DESCRICAO
		VALOR_UNITARIO
		QUANTIDADE
		VALOR_TOTAL
	Table VENDAS_PARCELAS
		ID_VENDA
		ESPECIE
		DATA
		VENCIMENTO
		VALOR
		CONDICAO

Compras:
	Table COMPRAS	
		ID
		STATUS
		NOTAFISCAL
		ID_FORNECEDOR
		FORNECEDOR_NOME
		DATA_EMISSAO
		DATA_RECE
		VALOR_FRETE
		TOTAL_PRODUTOS
		TOTAL_NOTA
	Table COMPRAS_ITENS
		ID_COMPRA
		ID_PRODUTO
		PRODUTO_DESCRICAO
		QUANTIDADE
		VALOR_UNITARIO
		VALOR_TOTAL
	Table COMPRAS_PARCELAS
		ID_COMPRA
		ESPECIE
		DATA
		VENCIMENTO	
		VALOR
		CONDICAO

Produtos:
	Table PRODUTOS
		ID
		CODIGO
		PRECO_VENDA
		PRECO_CUSTO
		ESTOQUE
	
Pessoas:
	Table PESSOAS
		ID
		RAZAO
		CNPJ
		FANTASIA
		LOGRADOURO
		NUMERO
		BAIRRO

Financeiro:
	Table CONTAS_PAGAR
		ID
		ID_NOTA (ID da compra em questão)
		ID_PESSOA
		ESPECIE
		VALOR
		DATA_EMISSAO
		DATA_VENCIMENTO
		DATA_PAGAMENTO
		DESCONTO
		ACRESCIMO
		VALOR_PAGO
		PAGO (Sim ou Não)
	Table CONTAS_RECEBER
		ID
		ID_NOTA (ID da nota de venda)
		ID_PESSOA
		ESPECIE
		VALOR
		DATA_EMISSAO
		DATA_VENCIMENTO
		DATA_RECEBIMENTO
		DESCONTO
		ACRESCIMO
		VALOR_RECEBIDO
		RECEBIDO (Sim ou Não)
	Table CAIXA
		ID_RECEBER
		ID_PAGAR
		DATA
		TIPO (Entrada ou Saida)
		VALOR
		SALDO
Fiscal: 
	Table NOTAS
		ID
		ID_VENDA
		NOTAFISCAL	
		STATUS
		DATA_EMISSAO
		VALOR_FRETE
		TOTAL_PRODUTOS
		TOTAL_NOTA
	Table NFCE
		ID
		ID_VENDA
		NOTAFISCAL	
		STATUS
		DATA_EMISSAO
		TOTAL_PRODUTOS
		TOTAL_NOTA
Ordem de Serviço:
	Table OS
		ID
		ORDEM_SERVICO
		STATUS
		DATA_EMISSAO
		ID_CLIENTE
		DEFEITO
		RESOLUCAO
		TOTAL_SERVICOS
		TOTAL_PRODUTOS
		TOTAL_OS
	Table OS_ITENS
		ID_OS
		ID_PRODUTO
		PRODUTO_DESCRICAO
		QUANTIDADE
		VALOR_UNITARIO
		VALOR_TOTAL
		
    

Analise a pergunta abaixo e gere um SQL para extrair todos os dados necessários para a pergunta em questão, e responda somente com o SQL, sem nada além disso
EX: SELECT * FROM VENDAS_ITENS WHERE ID_VENDA = '129'


Question: {question}"""

    response = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': 'SQL:'},
            {'role': 'user', 'content':question},
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )
    iareturn = response.choices[0].message.content
    return iareturn


