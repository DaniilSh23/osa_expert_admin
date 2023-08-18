import datetime
import time
from celery import shared_task

from osa_expert_admin.settings import MY_LOGGER
from osa_gpt.gpt_processing import make_embeddings
from osa_gpt.models import BotSettings, KnowledgeBaseChunks
from osa_gpt.utils import send_message_by_bot


@shared_task
def scheduled_task_example():
    """
    Пример отложенной задачи, которая печатает в консоль.
    """
    time.sleep(5)
    print(f'Привет мир, я отложенная задача. Сейчас: {datetime.datetime.utcnow()}')


@shared_task
def send_notifications(appl_pk, client_name, phone_number, description):
    """
    Отправка уведомлений админам бота о новой заявке.
    """
    MY_LOGGER.info('Старт задачи celery по отправке админам уведомлений о новой заявке')
    bot_admins_qset = BotSettings.objects.filter(key='bot_admins').only('value')
    for i_admin in bot_admins_qset:
        send_message_by_bot(
            chat_id=i_admin.value,
            text=f'🔥 Новая заявка из бота!\n\n🔹 № заявки: {appl_pk}\n🔹 Имя клиента: {client_name}\n'
                 f'🔹 Номер телефона: {phone_number}\n🔹 Описание ситуации: {description}'
        )
    MY_LOGGER.info(f'Конец таска celery')


@shared_task
def knowledge_base_processing(knowledge_base_text: str):
    """
    Таск по созданию в БД чанков БЗ с векторами
    """
    MY_LOGGER.info(f'Старт задачи по созданию в БД чанков БЗ с векторами')
    embeddings_lst = make_embeddings(knowledge_base_text=knowledge_base_text)
    KnowledgeBaseChunks.objects.all().delete()
    knowledge_base_lst = list()
    for i_chunk in embeddings_lst:
        vectors = list(map(lambda vector: str(vector), i_chunk[1]))
        knowledge_base_lst.append(KnowledgeBaseChunks(text=i_chunk[0], embedding=' '.join(vectors)))
    KnowledgeBaseChunks.objects.bulk_create(knowledge_base_lst)
    MY_LOGGER.info(f'Окончание задачи')
