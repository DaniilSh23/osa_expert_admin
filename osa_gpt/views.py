import re

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages as err_msgs
from langchain import FAISS
from langchain.embeddings import OpenAIEmbeddings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from osa_expert_admin.settings import MY_LOGGER, BOT_TOKEN
from osa_gpt.forms import NewApplicationForm
from osa_gpt.gpt_processing import make_embeddings, relevant_text_preparation, request_to_gpt
from osa_gpt.models import BotUser, BotSettings, Applications, KnowledgeBaseChunks, PromptsAI
from osa_gpt.serializers import GetSettingsSerializer
from osa_gpt.tasks import send_notifications, knowledge_base_processing


class WriteUsrView(APIView):
    """
    Вьюшка для обработки запросов при старте бота, записывает или обновляет данные о пользователе.
    """

    def post(self, request):
        MY_LOGGER.info(f'Получен запрос на вьюшку WriteUsrView: {request.data}')

        if not request.data.get("token") or request.data.get("token") != BOT_TOKEN:
            MY_LOGGER.warning(f'Неверный токен запроса: {request.data.get("token")} != {BOT_TOKEN}')
            return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid token')

        MY_LOGGER.debug(f'Записываем/обновляем данные о юзере в БД')
        bot_usr_obj, created = BotUser.objects.get_or_create(
            tlg_id=request.data.get("tlg_id"),
            defaults={
                "tlg_id": request.data.get("tlg_id"),
                "tlg_username": request.data.get("tlg_username"),
            }
        )
        MY_LOGGER.success(f'Данные о юзере успешно {"созданы" if created else "получены"} даём ответ на запрос.')
        return Response(data=f'success {"write" if created else "update"} object of bot user!',
                        status=status.HTTP_200_OK)


class GetSettingsView(APIView):
    """
    Вьюшка для получения настроек по ключу
    """
    def post(self, request: Request):
        """
        Принимает параметр запроса key=ключ настройки. Отдаёт JSON с настройками, либо с описанием ошибки
        """
        MY_LOGGER.debug(f'Пришёл POST запрос для получения настроек')

        serializer = GetSettingsSerializer(data=request.data)
        if serializer.is_valid() and serializer.validated_data.get("api_token") == BOT_TOKEN:
            key = serializer.validated_data.get("key")
            bot_settings = BotSettings.objects.filter(key=key)
            MY_LOGGER.debug(f'Список настроек по ключу {key!r}: {bot_settings}')
            return Response(data={'result': [i_set.value for i_set in bot_settings]}, status=status.HTTP_200_OK)
        else:
            MY_LOGGER.warning(f'Значение ключа слишком длинное')
            return Response(data={'result:' 'значение ключа слишком длинное'}, status=status.HTTP_400_BAD_REQUEST)


class NewApplication(View):
    """
    Вьюшки для новых заявок.
    """
    def get(self, request):
        """
        Рендерим страницу с формой
        """
        MY_LOGGER.debug(f'Получен GET запрос для отображения формы подачи заявки.')
        context = {}
        return render(request, template_name='osa_gpt/new_application.html', context=context)

    def post(self, request):
        """
        Обрабатываем запрос на создание новой заявки.
        """
        MY_LOGGER.info(f'Получен POST запрос для создания новой заявки')

        form = NewApplicationForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            tlg_id = form.cleaned_data.get('tlg_id')

            # Чекаем регуляркой номер телефона
            reg = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
            if not re.match(reg, phone_number):
                MY_LOGGER.warning(f'Невалидный номер телефона: {phone_number!r}')
                err_msgs.error(request, message='Ошибка: введите корректный номер телефона!')
                return redirect(to=reverse_lazy('osa_gpt:new_application'))

            # Чекаем ID телеграмма
            elif not tlg_id or not tlg_id.isdigit():
                MY_LOGGER.warning(f'Не обработан POST запрос на запись интересов. '
                                  f'В запросе отсутствует tlg_id')
                err_msgs.error(request, message='Ошибка: Вы уверены, что открыли форму из Telegram?')
                return redirect(to=reverse_lazy('osa_gpt:new_application'))

            # Создаём заявку и отправляем уведомление админам
            try:
                bot_usr_obj = BotUser.objects.get(tlg_id=tlg_id)
            except ObjectDoesNotExist:
                err_msgs.error(request, message='Ошибка: Пользователь не зарегистрирован в боте. Попробуйте '
                                                'перезапустить бота или отправьте ему следующее сообщение /start.')
                return redirect(to=reverse_lazy('osa_gpt:new_application'))

            appl_obj = Applications.objects.create(
                name=form.cleaned_data.get('client_name'),
                phone_number=form.cleaned_data.get('phone_number'),
                description=form.cleaned_data.get('description'),
                bot_user=bot_usr_obj,
            )
            send_notifications.delay(appl_obj.pk, appl_obj.name, appl_obj.phone_number, appl_obj.description)

            # Даём ответ на успешный запрос
            context = dict(
                header='✅ Заявка создана!',
                description=f'📌 Номер Вашей заявки {appl_obj.pk}. С Вами свяжется наш специалист. '
                            f'Пожалуйста, убедитесь, что указанный номер телефона {appl_obj.phone_number} доступен. 📲',
                btn_text='Хорошо, спасибо!'
            )
            return render(request, template_name='osa_gpt/success.html', context=context)
        else:
            MY_LOGGER.warning(f'Форма не прошла валидацию: {form.errors!r}')
            err_msgs.error(request, message=f'Невалидные данные формы. {form.errors!r}')
            return redirect(to=reverse_lazy('osa_gpt:new_application'))


class UploadKnowledgeBaseView(View):
    """
    Вьюшки для загрузки базы знаний
    """
    def get(self, request):
        MY_LOGGER.debug(f'Получен GET запрос для отображения формы загрузки БЗ.')

        if not request.user.is_staff:
            MY_LOGGER.warning(f'Юзер, выполнивший запрос, не имеет статус staff. Редиректим для авторизации')
            return redirect(to=f'/admin/login/?next={reverse_lazy("osa_gpt:upload_knowledge_base")}')

        context = {}
        return render(request, template_name='osa_gpt/upload_knowledge_base.html', context=context)

    def post(self, request):
        MY_LOGGER.debug(f'POST запрос на вьюшку загрузки БЗ')

        if not request.user.is_staff:
            MY_LOGGER.warning(f'Юзер, выполнивший запрос, не имеет статус staff. Редиректим для авторизации')
            return redirect(to=f'/admin/login/?next={reverse_lazy("mytlg:upload_new_channels")}')

        if not request.FILES.get("file"):
            MY_LOGGER.warning(f'Отсутствует файл в запросе!')
            return HttpResponse(content='Отсутствует файл в запросе', status=400)

        file = request.FILES.get("file")
        knowledge_base_processing.delay(knowledge_base_text=file.read().decode())
        return HttpResponse(content=f'Получил файлы, спасибо.')


class AnswerGPT(APIView):
    """
    Обработка вопросов пользователя и генерирование ответа моделью OpenAI.
    """
    def get(self, request):
        MY_LOGGER.info(f'GET запрос на вьюшку генерирования ответа нейронкой.')

        if not request.GET.get('token') or request.GET.get('token') != BOT_TOKEN:
            MY_LOGGER.warning(f'Неверный токен в запросе: {request.GET!r}')
            return Response(data='invalid token', status=status.HTTP_400_BAD_REQUEST)

        if not request.GET.get('msg'):
            MY_LOGGER.warning(f'В запросе отсутствует параметр msg: {request.GET!r}')
            return Response(data='msg param is required!', status=status.HTTP_400_BAD_REQUEST)

        # Достаём релевантные чанки
        MY_LOGGER.debug(f'Достаём релевантные чанки из БД.')
        base_text = relevant_text_preparation(query=request.GET.get('msg'))

        # Кидаем запрос к ChatGPT
        MY_LOGGER.debug(f'Кидаем запрос к ChatGPT')
        prompt = PromptsAI.objects.get(name='consultant').only('prompt').prompt
        gpt_answer = request_to_gpt(
            content=f"Документ с информацией для ответа клиенту: {base_text}\n\n"
                    f"Вопрос клиента:\n{request.GET.get('msg')}",
            system=prompt
        )
        if not gpt_answer:
            MY_LOGGER.warning(f'Неудалось получить ответ от ChatGPT. Отдаём ответ с инфой об ошибке.')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'gpt_answer': gpt_answer}, status=status.HTTP_200_OK)

        # TODO: вроде допилил обработку запроса. Не тестил. Нужно прописать ещё промпт так, чтобы он впаривал услуги.


def test_view(request):
    # chunks = make_embeddings(knowledge_base_path='/home/da/PycharmProjects/osa_expert_admin/База_знаний_УИИ.txt')

    # Отбираем более релевантные куски базового текста (base_text), согласно запросу (query)
    query = 'Сколько человек уже выбрали УИИ'
    relevant_text_preparation(query=query)
    context = {}
    return render(request, template_name='osa_gpt/test.html', context=context)
