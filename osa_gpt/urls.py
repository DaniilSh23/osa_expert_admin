from django.urls import path

from osa_gpt.views import WriteUsrView, NewApplication, test_view, UploadKnowledgeBaseView, AnswerGPT

app_name = 'osa_gpt'

urlpatterns = [
    path('write_usr/', WriteUsrView.as_view(), name='write_usr'),
    path('new_application/', NewApplication.as_view(), name='new_application'),
    path('upload_knowledge_base/', UploadKnowledgeBaseView.as_view(), name='upload_knowledge_base'),
    path('answer_gpt/', AnswerGPT.as_view(), name='answer_gpt'),

    path('test/', test_view, name='test'),
]
