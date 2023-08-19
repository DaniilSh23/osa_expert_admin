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
                _, i_created = BotSettings.objects.get_or_create(
                    key=i_key,
                    defaults={'key': i_key, 'value': i_val}
                )
                logger.success(f'Ключ {i_key} успешно {"создан" if i_created else "получен"} со значением {i_val}')

            prompts = (
                ('consultant', 'Текст промпта для консультанта'),
            )
            for i_name, i_prompt in prompts:
                _, i_created = PromptsAI.objects.get_or_create(
                    name=i_name,
                    defaults={'name': i_name, 'prompt': i_prompt}
                )
                logger.success(f'Промпт {i_name!r} успешно {"создан" if i_created else "получен"} --> '
                               f'{i_prompt[:48]}...')

        logger.info('Окончание команды по установке настроек и промптов')
