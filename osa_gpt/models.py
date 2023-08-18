from django.db import models


class BotUser(models.Model):
    """
    Модель для юзеров бота
    """
    tlg_id = models.CharField(verbose_name='tlg_id', max_length=30, db_index=True)
    tlg_username = models.CharField(verbose_name='username', max_length=100, blank=False, null=True)
    start_bot_at = models.DateTimeField(verbose_name='старт бота', auto_now_add=True)

    def __str__(self):
        return f'User TG_ID {self.tlg_id}'

    class Meta:
        ordering = ['-start_bot_at']
        verbose_name = 'юзер бота'
        verbose_name_plural = 'юзеры бота'


class BotSettings(models.Model):
    """
    Настройки бота.
    """
    key = models.CharField(verbose_name='ключ', max_length=50)
    value = models.TextField(verbose_name='значение', max_length=500)

    class Meta:
        ordering = ['-id']
        verbose_name = 'настройка бота'
        verbose_name_plural = 'настройки бота'


class Applications(models.Model):
    """
    Модель для заявок.
    """
    name = models.CharField(verbose_name='имя клиента', max_length=150)
    phone_number = models.CharField(verbose_name='номер телефона', max_length=50)
    description = models.TextField(verbose_name='описание проблемы', max_length=1000)
    created_at = models.DateTimeField(verbose_name='дата и время', auto_now_add=True)
    bot_user = models.ForeignKey(verbose_name='юзер бота', to=BotUser, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'


class KnowledgeBaseChunks(models.Model):
    """
    Модель для хранения эмбеддингов разбитой на чанки базы знаний.
    """
    text = models.TextField(verbose_name='текст чанка')
    embedding = models.TextField(verbose_name='эмбеддинги')

    class Meta:
        ordering = ['-id']
        verbose_name = 'чанк базы знаний'
        verbose_name_plural = 'чанки базы знаний'
