from django.core.management import BaseCommand
from django.db import transaction
from loguru import logger

from osa_gpt.models import BotSettings, PromptsAI


class Command(BaseCommand):
    """
    Команда для по установки настроек
    """
    def handle(self, *args, **options):
        logger.info('Старт команды по установке настроек и промптов')
        with transaction.atomic():
            keys = {
                'bot_admins': '1978587604',
            }
            for i_key, i_val in keys.items():
                _, i_created = BotSettings.objects.update_or_create(
                    key=i_key,
                    defaults={'key': i_key, 'value': i_val}
                )
                logger.success(f'Ключ {i_key} успешно {"создан" if i_created else "получен"} со значением {i_val}')

            prompts = (
                ('consultant', 'Ты опытный консультант клиентов компании "ОСА Автоэксперт". '
                               'У тебя есть большой документ со всеми материалами о специфике работы компании, '
                               'требованиях законодательства и популярными кейсами, '
                               'которые очень полезны для потенциальных клиентов компании.'
                               'Тебе задаёт вопрос потенциальный клиент компании, дай ему ответ, опираясь на документ.'
                               'Отвечай максимально точно по документу, не придумывай ничего от себя.'
                               'Не упоминай документ при ответе. Постарайся построить свой ответ так, '
                               'чтобы клиент захотел связаться с экспертом компании и воспользоваться услугами. '
                               'Документ с информацией для ответа специалисту:'),
                ('summarizer', 'Ты - ассистент отдела продаж, основанный на AI. Ты умеешь профессионально '
                               'суммаризировать присланные тебе диалоги менеджера и клиента. '
                               'Твоя задача - саммаризировать диалог, который тебе пришел. Обязательно указывай в '
                               'саммаризации диалога имя клиента и другую важную для отдела продаж информацию, '
                               'если она будет в диалоге.')
            )
            for i_name, i_prompt in prompts:
                _, i_created = PromptsAI.objects.update_or_create(
                    name=i_name,
                    defaults={'name': i_name, 'prompt': i_prompt}
                )
                logger.success(f'Промпт {i_name!r} успешно {"создан" if i_created else "получен"} --> '
                               f'{i_prompt[:48]}...')

        logger.info('Окончание команды по установке настроек и промптов')
