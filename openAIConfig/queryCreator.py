from openAIConfig.openaiInit import initializeOpenAI
from utils import *

client = initializeOpenAI()

def querycreator(data, question):

    query = f"""
    Você é uma assistente virtual para me ajudar com dados do meu comércio, abaixo tem os dados do meu comércio
    Nos dados que terá acesso lembresse de nunca trazer informações na sua resposta que sejam IDs, nem ID de vendas ou produtos, nada, apenas códigos, opte por códigos 
    ou outras informações úteis, tente trazer também respostas mais curtas e objetivas, porém que sejam prestativas, por exemplo, se eu lhe pedir o .
    meu produto mais caro, você me responde com o código do produto, seu preço de custo e seu preço de venda, etc. Lemresse de preencher as informações de forma profissional também,
    valores de dinheiro sempre R$ na frente por exemplo.
    
    **Importante** CASO NÃO TENHA DADOS PARA A PERGUNTA EM QUESTÃO RESPONDER "Perdão, não consegui concluir sua pesquisa, tente um prompt diferente ou mais específico por gentileza."
    
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

    update_ia_usage(1)

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

    update_ncm_usage(1)

    return iareturn


def interpret_questionSQLs(question):
    prompt = f"""
Você é um assistente que gera SQLs compatíveis com Firebird 3.0. Responda apenas com o SQL, sem qualquer texto adicional ou explicação. 

Regras:
- Use `ROWS X` para limitar resultados, nunca `LIMIT` ou `FIRST X`.
- Evite subconsultas no `FROM`; prefira `WITH` (CTEs) para simplificar.
- Não use `UNION ALL`. Gere SQLs separados para múltiplas consultas.
- Especifique as colunas no `SELECT`. Não use `SELECT *`.
- Colunas no `GROUP BY` devem estar no `SELECT`, exceto funções agregadas.
- Ordene por aliases definidos no `SELECT`.

Estrutura do Banco:
VENDAS (ID, VENDA, STATUS, DATA_EMISSAO, ID_CLIENTE, CLIENTE_NOME, TOTAL_PRODUTOS, DESCONTO, TOTAL_VENDA)
VENDAS_ITENS (ID_VENDA, ID_PRODUTO, PRODUTO_DESCRICAO, VALOR_UNITARIO, QUANTIDADE, VALOR_TOTAL)
VENDAS_PARCELAS (ID_VENDA, ESPECIE, DATA, VENCIMENTO, VALOR, CONDICAO)
PRODUTOS (ID, CODIGO, PRECO_VENDA, PRECO_CUSTO, ESTOQUE, DESCRICAO)
PESSOAS (ID, RAZAO, CNPJ, FANTASIA, LOGRADOURO, NUMERO, BAIRRO)
CONTAS_PAGAR (ID, ID_NOTA, ID_PESSOA, ESPECIE, VALOR, DATA_EMISSAO, DATA_VENCIMENTO, DATA_PAGAMENTO, DESCONTO, ACRESCIMO, VALOR_PAGO, PAGO)
CONTAS_RECEBER (ID, ID_NOTA, ID_PESSOA, ESPECIE, VALOR, DATA_EMISSAO, DATA_VENCIMENTO, DATA_RECEBIMENTO, DESCONTO, ACRESCIMO, VALOR_RECEBIDO, RECEBIDO)
CAIXA (ID_RECEBER, ID_PAGAR, DATA, TIPO, VALOR, SALDO)

Question: {question}"""

    response = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': 'SQL:'},
            {'role': 'user', 'content':prompt},
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )
    iareturn = response.choices[0].message.content

    update_ia_usage(1)


    return iareturn



