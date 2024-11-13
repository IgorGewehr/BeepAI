from openAIConfig.openaiInit import initializeOpenAI
import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openAIConfig.queryCreator import querycreator
import pickle

# Inicializa o cliente OpenAI
client = initializeOpenAI()

# Variáveis globais para armazenar o último contexto e seu DataFrame
last_context = None
last_context_df = None

# Função para obter embeddings em lotes
def get_embeddings(texts, model="text-embedding-3-small"):
    embeddings = []
    batch_size = 100  # Ajuste o tamanho do lote conforme necessário
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        try:
            response = client.embeddings.create(input=batch_texts, model=model)
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
        except Exception as e:
            # Em caso de erro, adiciona vetores de zeros
            embeddings.extend([[0] * 1536] * len(batch_texts))
    return embeddings

# Carrega e processa o CSV de acordo com o contexto fornecido
def load_and_process_csv(csv_file):
    try:
        embeddings_file = f"C:/App/{os.path.splitext(os.path.basename(csv_file))[0]}_with_embeddings.pkl"
        if os.path.exists(embeddings_file):
            print(f"Carregando embeddings do contexto do arquivo {csv_file}...")
            with open(embeddings_file, 'rb') as f:
                context_df = pickle.load(f)
        else:
            print(f"Calculando embeddings do contexto para {csv_file}...")
            context_df = pd.read_csv(csv_file, encoding='utf-8', delimiter=';', on_bad_lines='skip')
            context_df.dropna(axis=1, how='all', inplace=True)  # Remove colunas completamente nulas
            context_df.fillna('', inplace=True)  # Substitui valores nulos por strings vazias
            context_df['combined_text'] = context_df.astype(str).agg(' '.join, axis=1).str.slice(0, 2000)

            # Gerar embeddings em lotes
            embeddings = get_embeddings(context_df['combined_text'].tolist())
            context_df['embedding'] = embeddings

            # Remover a coluna 'combined_text' antes de salvar
            context_df.drop(columns=['combined_text'], inplace=True)

            # Salvar o DataFrame com embeddings em um arquivo Pickle
            with open(embeddings_file, 'wb') as f:
                pickle.dump(context_df, f)

        return context_df
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Erro: Arquivo CSV não encontrado no caminho especificado: {csv_file}")
    except Exception as e:
        raise Exception(f"Erro ao carregar ou processar o arquivo CSV: {str(e)}")

# Função para gerar o embedding da pergunta do usuário
def get_question_embedding(userQuestion):
    try:
        embedding = get_embeddings([userQuestion])[0]
        return np.array(embedding)
    except Exception as e:
        raise Exception(f"Erro ao gerar embedding da pergunta do usuário: {str(e)}")

# Função para calcular a similaridade entre a pergunta e os dados
def check_similarity(question_embedding, context_df):
    try:
        # Filtrar linhas com embeddings válidos
        valid_embeddings_df = context_df[
            context_df['embedding'].apply(lambda x: isinstance(x, list) and len(x) == 1536)
        ]

        if valid_embeddings_df.empty:
            raise ValueError("Nenhum embedding válido encontrado no DataFrame de contexto.")

        context_embeddings = np.vstack(valid_embeddings_df['embedding'].values)
        similarities = cosine_similarity([question_embedding], context_embeddings).flatten()
        valid_embeddings_df = valid_embeddings_df.copy()  # Evitar SettingWithCopyWarning
        valid_embeddings_df['similarity'] = similarities
        sorted_df = valid_embeddings_df.sort_values(by='similarity', ascending=False)
        return sorted_df
    except KeyError as ke:
        raise KeyError(f"Erro: Coluna de embeddings ausente no DataFrame: {str(ke)}")
    except Exception as e:
        raise Exception(f"Erro ao calcular similaridade: {str(e)}")

# Função para extrair os dados mais relevantes com base na similaridade
def answer_context(similarity_df, top_n=5):
    try:
        top_similar = similarity_df.head(top_n)
        if top_similar.empty:
            return "Desculpe, não foram encontrados dados relevantes para sua pergunta."
        data_columns = [col for col in top_similar.columns if col not in ['embedding', 'similarity']]
        data = top_similar[data_columns]
        return data.to_string(index=False)
    except Exception as e:
        raise Exception(f"Erro ao extrair dados relevantes: {str(e)}")

# Carrega o contexto com base no parâmetro "contexto"
def get_context_df(contexto):
    global last_context, last_context_df
    csv_map = {
        'Financeiro': 'C:/App/financeiro.csv',
        'Compras': 'C:/App/compras.csv',
        'Vendas': 'C:/App/vendas.csv'
    }

    if contexto not in csv_map:
        raise ValueError(f"Contexto inválido: {contexto}. Escolha entre 'Financeiro', 'Compras' ou 'Vendas'.")

    csv_file = csv_map[contexto]

    # Se o contexto mudou, recarregar o CSV correspondente
    if last_context != contexto:
        last_context_df = load_and_process_csv(csv_file)
        last_context = contexto

    return last_context_df

# Função principal que integra tudo
def create_ai_reply(userQuestion, contexto):
    try:
        context_df = get_context_df(contexto)
        question_embedding = get_question_embedding(userQuestion)
        similarity_df = check_similarity(question_embedding, context_df)
        data = answer_context(similarity_df)
        response = querycreator(data, userQuestion)
        return response
    except Exception as e:
        raise Exception(f"Erro ao criar a resposta da IA: {str(e)}")
