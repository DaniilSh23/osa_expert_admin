from django.urls import path

from osa_gpt.views import WriteUsrView, NewApplication

app_name = 'osa_gpt'

urlpatterns = [
    path('write_usr/', WriteUsrView.as_view(), name='write_usr'),
    path('new_application/', NewApplication.as_view(), name='new_application'),
]
