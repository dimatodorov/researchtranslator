from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('train-model/', views.index, name='index'),
    path('analysis/', views.analysis, name='analysis'),
    path('about/', views.about, name='about'),
    url(r'add-translator/', views.addTranslator, name='addTranslator'),
    url(r'delete-translator/(?P<tr_id>[\d]+)', views.deleteTranslator, name='deleteTranslator'),
    url(r'delete-translator-file/(?P<file_id>[\d]+)', views.deleteTranslatorFile, name='deleteTranslatorFile'),
    url(r'delete-test-file/(?P<file_id>[\d]+)', views.deleteTestFile, name='deleteTestFile'),
    url(r'upload_translator_files/(?P<tr_id>[\d]+)', views.uploadTranslatorFiles, name='upload_translator_files'),
    url(r'upload/', views.uploadTestTexts, name='upload'),
    url(r'train/', views.train, name='train'),
    url(r'make-analysis/', views.makeAnalysis, name='makeAnalysis'),
    url(r'^deleteCheckedTestFiles/$', views.deleteCheckedTestFiles)
]
#if settings.DEBUG:
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)