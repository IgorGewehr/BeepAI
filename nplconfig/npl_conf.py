import os
import pandas as pd
import numpy as np
from openAIConfig.queryCreator import querycreator  # Se necessário
import pickle
import re
import dateparser
from dateparser.search import search_dates
import spacy
from spacy.matcher import Matcher

# Carregar modelo em português
nlp = spacy.load("pt_core_news_sm")

# Variáveis globais para armazenar o último contexto e seu DataFrame
last_context = None
last_context_df = None


def get_context_df(contexto):
    global last_context, last_context_df
    csv_map = {
        'Financeiro': 'C:/App/financeiro.csv',
        'Compras': 'C:/App/compras.csv',
        'Vendas': 'C:/App/vendas.csv',
        'NFCes': 'C:/App/nfces.csv',
        'Notas': 'C:/App/notas.csv',
        'Servicos': 'C:/App/servicos.csv',
        'Pessoas': 'C:/App/pessoas.csv',
        'Tributacao': 'C:/App/tributacao.csv',
        'Produtos': 'C:/App/produtos.csv'
    }

    if contexto not in csv_map:
        raise ValueError(f"Contexto inválido: {contexto}.")

    csv_file = csv_map[contexto]

    # Se o contexto mudou, recarregar o CSV correspondente
    if last_context != contexto:
        context_df = pd.read_csv(csv_file, encoding='utf-8', delimiter=';', on_bad_lines='skip')
        context_df.dropna(axis=1, how='all', inplace=True)  # Remove colunas completamente nulas
        context_df.fillna('', inplace=True)  # Substitui valores nulos por strings vazias
        last_context_df = context_df
        last_context = contexto

    return last_context_df


def extract_dates_from_question(user_question):
    # Buscar datas na pergunta
    results = search_dates(user_question, languages=['pt'])
    dates = []
    if results:
        for result in results:
            dates.append(result[1])  # result[1] é o objeto datetime
    return dates


def extract_numbers_from_question(user_question):
    # Extrair números da pergunta
    numbers = re.findall(r'\b\d+(\,\d+)?\b', user_question)
    # Converter números para float
    numbers = [float(num.replace(',', '.')) for num in numbers]
    return numbers


def parse_user_question(user_question):
    doc = nlp(user_question)
    matcher = Matcher(nlp.vocab)

    # Definir padrões para intenções
    patterns = [
        {"label": "MAX", "pattern": [{"LOWER": "maior"}]},
        {"label": "MIN", "pattern": [{"LOWER": "menor"}]},
        {"label": "SUM", "pattern": [{"LOWER": {"IN": ["total", "somatório", "soma"]}}]},
        {"label": "AVG", "pattern": [{"LOWER": "média"}]},
        {"label": "COMPARE", "pattern": [{"LOWER": "comparar"}]},
        {"label": "COUNT", "pattern": [{"LOWER": {"IN": ["quantas", "quantos", "número"]}}]},
    ]

    for pattern in patterns:
        matcher.add(pattern["label"], [pattern["pattern"]])

    matches = matcher(doc)
    intents = set()
    for match_id, start, end in matches:
        intent = nlp.vocab.strings[match_id]
        intents.add(intent)

    # Extrair entidades nomeadas
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text

    # Extrair datas usando dateparser
    date_entities = extract_dates_from_question(user_question)
    if date_entities:
        entities['DATES'] = date_entities

    # Extrair valores numéricos
    numeric_entities = extract_numbers_from_question(user_question)
    if numeric_entities:
        entities['NUMBERS'] = numeric_entities

    return intents, entities


def execute_query(intents, entities, context_df):
    if not intents:
        return "Desculpe, não consegui entender sua pergunta."

    # Vamos lidar com uma intenção por vez
    intent = intents.pop()
    result = None

    # Aplicar filtros baseados nas entidades
    filtered_df = context_df.copy()

    # Filtrar por datas, se houver
    if 'DATES' in entities:
        dates = entities['DATES']
        if len(dates) == 1:
            date = dates[0]
            # Considerar apenas o mês e o ano
            start_date = date.replace(day=1)
            end_date = (start_date + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
            filtered_df = filtered_df[
                (filtered_df['DATA_EMISSAO'] >= start_date) & (filtered_df['DATA_EMISSAO'] <= end_date)]
        elif len(dates) == 2:
            date1 = dates[0]
            date2 = dates[1]
            # Obter intervalos de datas
            start_date1 = date1.replace(day=1)
            end_date1 = (start_date1 + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
            start_date2 = date2.replace(day=1)
            end_date2 = (start_date2 + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
            df1 = filtered_df[(filtered_df['DATA_EMISSAO'] >= start_date1) & (filtered_df['DATA_EMISSAO'] <= end_date1)]
            df2 = filtered_df[(filtered_df['DATA_EMISSAO'] >= start_date2) & (filtered_df['DATA_EMISSAO'] <= end_date2)]
            # Executar comparação
            result = compare_intent(intent, df1, df2, dates)
            return result

    # Executar operações baseadas na intenção
    result = perform_intent_operation(intent, filtered_df, entities)
    return result


def perform_intent_operation(intent, df, entities):
    if intent == "MAX":
        if 'VENDA_TOTAL' in df.columns:
            max_row = df.loc[df['VENDA_TOTAL'].idxmax()]
            return f"A maior venda é:\n{max_row.to_string()}"
        else:
            return "Dados de vendas não encontrados."
    elif intent == "MIN":
        if 'VENDA_TOTAL' in df.columns:
            min_row = df.loc[df['VENDA_TOTAL'].idxmin()]
            return f"A menor venda é:\n{min_row.to_string()}"
        else:
            return "Dados de vendas não encontrados."
    elif intent == "SUM":
        if 'VENDA_TOTAL' in df.columns:
            total = df['VENDA_TOTAL'].sum()
            return f"O total das vendas é: R$ {total:.2f}"
        else:
            return "Dados de vendas não encontrados."
    elif intent == "AVG":
        if 'VENDA_TOTAL' in df.columns:
            average = df['VENDA_TOTAL'].mean()
            return f"A média das vendas é: R$ {average:.2f}"
        else:
            return "Dados de vendas não encontrados."
    elif intent == "COUNT":
        count = df.shape[0]
        return f"O número total de registros é: {count}"
    else:
        return "Intenção não reconhecida ou não suportada no momento."


def compare_intent(intent, df1, df2, dates):
    if 'VENDA_TOTAL' not in df1.columns or 'VENDA_TOTAL' not in df2.columns:
        return "Dados de vendas não encontrados."

    total1 = df1['VENDA_TOTAL'].sum()
    total2 = df2['VENDA_TOTAL'].sum()
    difference = total2 - total1
    percentage_change = (difference / total1) * 100 if total1 != 0 else 0

    response = (
        f"Total de vendas em {dates[0].strftime('%B de %Y')}: R$ {total1:.2f}\n"
        f"Total de vendas em {dates[1].strftime('%B de %Y')}: R$ {total2:.2f}\n"
        f"Diferença: R$ {difference:.2f}\n"
        f"Variação percentual: {percentage_change:.2f}%"
    )
    return response


def create_ai_reply(userQuestion, contexto):
    try:
        context_df = get_context_df(contexto)

        # Certificar-se de que a coluna 'DATA_EMISSAO' está no formato datetime
        if 'DATA_EMISSAO' in context_df.columns:
            context_df['DATA_EMISSAO'] = pd.to_datetime(context_df['DATA_EMISSAO'], errors='coerce')

        # Analisar a pergunta do usuário
        intents, entities = parse_user_question(userQuestion)

        # Executar a consulta baseada na intenção e entidades
        response = execute_query(intents, entities, context_df)

        return response
    except Exception as e:
        return f"Erro ao criar a resposta da IA: {str(e)}"
