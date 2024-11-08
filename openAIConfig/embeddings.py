from openAIConfig.openaiInit import initializeOpenAI
import os
import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from openAIConfig.queryCreator import querycreator
from tqdm import tqdm

# Inicializa o cliente OpenAI
client = initializeOpenAI()

# Função para obter embeddings em lote com tratamento de erros
def get_embeddings(texts, model="text-embedding-3-small"):
    embeddings = []
    for text in texts:
        try:
            text = text.replace("\n", " ")
            response = client.embeddings.create(input=[text], model=model)
            embedding = response.data[0].embedding
            embeddings.append(embedding)
        except Exception as e:
            # Em caso de erro, adiciona um vetor de zeros ou trata conforme necessário
            embeddings.append([0] * 1536)  # Tamanho do embedding do modelo 'text-embedding-ada-002'
    return embeddings

# Carrega e processa o CSV
def load_and_process_csv(csv_file):
    try:
        embeddings_file = 'C:/App/data_with_embeddings.csv'
        if os.path.exists(embeddings_file):
            print("Carregando embeddings do contexto do arquivo CSV...")
            context_df = pd.read_csv(
                embeddings_file,
                converters={'embedding': json.loads}
            )
        else:
            print("Calculando embeddings do contexto...")
            chunk_size = 1000  # Ajuste conforme necessário
            chunks = pd.read_csv(csv_file, encoding='utf-8', delimiter=';', on_bad_lines='skip', chunksize=chunk_size, low_memory=False)

            processed_chunks = []
            for chunk in tqdm(chunks):
                # Remove colunas completamente nulas ou com todos os valores ausentes
                chunk.dropna(axis=1, how='all', inplace=True)
                # Substitui valores nulos por string vazia
                chunk.fillna('', inplace=True)
                # Concatena todas as colunas em uma string
                chunk['combined_text'] = chunk.astype(str).agg(' '.join, axis=1)
                # Limita o tamanho do texto para evitar exceder os limites da API
                chunk['combined_text'] = chunk['combined_text'].str.slice(0, 2000)
                # Divide o chunk em sublotes para evitar exceder o limite da API
                texts = chunk['combined_text'].tolist()
                batch_size = 100  # Número de textos por lote
                embeddings = []
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_embeddings = get_embeddings(batch_texts)
                    embeddings.extend(batch_embeddings)
                chunk['embedding'] = embeddings
                processed_chunks.append(chunk)

            context_df = pd.concat(processed_chunks, ignore_index=True)
            # Salva embeddings no CSV
            df_embeddings = context_df[['embedding']].copy()
            df_embeddings['embedding'] = df_embeddings['embedding'].apply(json.dumps)
            df_embeddings.to_csv(embeddings_file, index=False)
        return context_df
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Erro: Arquivo CSV não encontrado no caminho especificado. {str(e)}")
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
        context_embeddings = np.vstack(context_df['embedding'].values)
        similarities = cosine_similarity([question_embedding], context_embeddings).flatten()
        context_df['similarity'] = similarities
        return context_df.sort_values(by='similarity', ascending=False)
    except KeyError as ke:
        raise KeyError(f"Erro: Coluna de embeddings ausente no DataFrame: {str(ke)}")
    except Exception as e:
        raise Exception(f"Erro ao calcular similaridade: {str(e)}")

# Função para extrair os dados mais relevantes com base na similaridade
def answer_context(similarity_df, top_n=5):
    try:
        top_similar = similarity_df.head(top_n)
        data_columns = [col for col in top_similar.columns if col not in ['embedding', 'similarity', 'combined_text']]
        data = top_similar[data_columns]
        return data.to_string(index=False)
    except Exception as e:
        raise Exception(f"Erro ao extrair dados relevantes: {str(e)}")

# Carrega o contexto uma vez
csv_file = 'C:/App/data_exported.csv'
context_df = load_and_process_csv(csv_file)

# Função principal que integra tudo
def create_ai_reply(userQuestion):
    try:
        question_embedding = get_question_embedding(userQuestion)
        similarity_df = check_similarity(question_embedding, context_df)
        data = answer_context(similarity_df)
        response = querycreator(data, userQuestion)
        return response
    except Exception as e:
        raise Exception(f"Erro ao criar a resposta da IA: {str(e)}")
