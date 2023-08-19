import re
from typing import List, Tuple

import openai
from langchain import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, NLTKTextSplitter

from osa_expert_admin.settings import MY_LOGGER
from osa_gpt.models import KnowledgeBaseChunks


def make_embeddings(knowledge_base_text: str) -> List[Tuple[str, List[float]]]:
    """
    Функция для разбиения базы знаний на чанки и создания эмбеддингов
    """
    text_splitter = NLTKTextSplitter(chunk_size=500, chunk_overlap=0)  # chunk_size видимо или токены, или символы
    chunks = text_splitter.split_text(text=knowledge_base_text)
    embeddings = OpenAIEmbeddings(max_retries=2)
    result_embeddings_lst = []
    for i_chunk in chunks:
        i_embedding = embeddings.embed_query(text=i_chunk)
        result_embeddings_lst.append((i_chunk, i_embedding))  # Складываем в список кортежи (текст, эмбеддинг)
    return result_embeddings_lst


def relevant_text_preparation(query: str) -> str | None:
    """
    Подготовка текста, перед запросом к модели OpenAI
    Чанки базы знаний достаются из БД.
    query - запрос пользователя, под который в base_text нужно найти более релевантные куски текста
    """
    # Создадим индексную базу векторов по данному тексту (переведом текст в цифры, чтобы его понял комп)
    embeddings = OpenAIEmbeddings()
    chunks_qset = KnowledgeBaseChunks.objects.all()
    index_db = FAISS.from_embeddings(
        # Сложная конструкция, но всё просто: пилим список с кортежами. В кортежах текст чанка и вектора в виде float
        text_embeddings=[(i_chunk.text, list(map(lambda vector: float(vector), i_chunk.embedding.split())))
                         for i_chunk in chunks_qset],
        embedding=embeddings,
    )

    # Отбираем более релевантные чанки БЗ, согласно запросу (query)
    relevant_pieces = index_db.similarity_search_with_score(query, k=4)  # Достаём куски с Евклидовым расстоянием
    message_content = re.sub(
        pattern='\n{2}',
        repl=' ',
        string='\n '.join(
            [f'\nОтрывок документа №{indx + 1}\n======{doc.page_content}======\n'
             for indx, (doc, score) in enumerate(relevant_pieces)]
        )
    )
    return message_content  # Отдаём склеенные более релевантные отрывки БЗ


def request_to_gpt(system, content, temp=0):
    """
    Функция для того, чтобы отправить запрос к модели GPT и получить ответ.
    system - инструкция для модели GPT
    content - единая переменная, в которой указываем и запрос пользователя, и БЗ с нужным лексическим контекстом.
    temp - (значение от 0 до 1) чем выше, тем более творчески будет ответ модели, то есть она будет додумывать что-то.
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": content},
    ]
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temp
        )
    except openai.error.ServiceUnavailableError as err:
        MY_LOGGER.error(f'Серверы OpenAI перегружены или недоступны. {err}')
        return False
    except Exception as err:
        MY_LOGGER.error(f'Иная ошибка при запросе с OpenAI. {err}')
        return False

    answer = completion.choices[0].message.content
    return answer  # возвращает ответ
