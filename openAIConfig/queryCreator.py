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
Você é um assistente que gera SQLs compatíveis com Firebird 3.0. Responda **apenas** com o **SQL**, sem qualquer texto adicional ou explicação.

**Regras Importantes:**

- **Múltiplas Perguntas:**
  - Se houver múltiplas perguntas, gere um **SQL separado** para cada uma.
  - Separe cada SQL com um ponto e vírgula (`;`) e **não combine** múltiplas consultas em uma única instrução.
  - **Não use CTEs (WITH)** para combinar respostas de múltiplas perguntas.

- **Terminação do SQL:**
  - Certifique-se de que cada instrução SQL termine com um ponto e vírgula (`;`).

- **Limitação de Resultados:**
  - Use `ROWS X` após `ORDER BY` para limitar resultados.
  - **Não** use `LIMIT` ou `FIRST X`.

- **Subconsultas e CTEs:**
  - Evite subconsultas no `FROM`; prefira consultas diretas.
  - **Não** use `WITH` (CTEs) para consultas simples.

- **Seleção de Colunas:**
  - Especifique as colunas necessárias no `SELECT`.
  - **Não** use `SELECT *`.

**Regras de Ordenação:**
- Não use aliases definidos no `SELECT` dentro do `ORDER BY`. Utilize diretamente as colunas ou expressões originais.
  - Exemplo incorreto: `ORDER BY TOTAL_VENDIDO DESC` (se `TOTAL_VENDIDO` é um alias para `SUM(QUANTIDADE)`).
  - Exemplo correto: `ORDER BY SUM(QUANTIDADE) DESC`.

**Regras para Cálculos em Consultas:**
- Ao realizar cálculos com funções agregadas (como `SUM`, `AVG`, etc.), sempre certifique-se de que todos os elementos no cálculo sejam compatíveis com agregação.
  - Exemplo incorreto: `P.PRECO_VENDA * SUM(VI.QUANTIDADE)`.
  - Exemplo correto: `SUM(VI.QUANTIDADE * P.PRECO_VENDA)`.

**Regras para Agrupamento (`GROUP BY`):**
- Todas as colunas que não estão em funções agregadas no `SELECT` devem ser incluídas no `GROUP BY`.
- Não utilize colunas derivadas ou expressões no `GROUP BY`. Use apenas nomes de colunas.


- **Agrupamento e Ordenação:**
  - Colunas no `GROUP BY` devem estar no `SELECT`, exceto quando usadas em funções agregadas.
  - Use aliases claros para colunas calculadas e referencie-os no `ORDER BY`.

- **Outras Orientações:**
  - **Não** use `UNION ALL` ou `UNION`.
  - Gere consultas simples e diretas.
  - Certifique-se de que o SQL seja válido e executável no Firebird 3.0.

**Estrutura do Banco de Dados:**
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



