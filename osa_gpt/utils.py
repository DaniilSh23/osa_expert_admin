import requests

from osa_expert_admin.settings import MY_LOGGER, BOT_TOKEN


def send_message_by_bot(chat_id, text, disable_notification=False) -> bool | None:
    """
    Функция для отправки сообщений в телеграм от лица бота
    """
    MY_LOGGER.info(f'Вызвана функция для отправки от лица бота сообщений в телегу юзеру {chat_id!r}')
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text, 'disable_notification': disable_notification}
    MY_LOGGER.debug(f'Выполняем запрос на отправку сообщения от лица бота, данные запроса: {data}')
    response = requests.post(url=url, data=data)  # Выполняем запрос на отправку сообщения

    if response.status_code != 200:  # Обработка неудачного запроса на отправку
        MY_LOGGER.error(f'Неудачная отправка сообщения от лица бота.\n'
                        f'Запрос: url={url} | data={data}\n'
                        f'Ответ:{response.text}')
        return
    MY_LOGGER.success(f'Успешная отправка сообщения от лица бота юзеру {chat_id!r}.')
    return True
