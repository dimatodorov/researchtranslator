from django.contrib import admin

from .models import Translator, TrainText, TestText, AnalysisParam, TestDictionary, TrainDictionary

admin.site.register(Translator)
admin.site.register(TrainText)
admin.site.register(TestText)
admin.site.register(AnalysisParam)
admin.site.register(TrainDictionary)
admin.site.register(TestDictionary)

