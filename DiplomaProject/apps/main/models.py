from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

class Translator(models.Model):
    translator_name = models.CharField("Ім'я перекладача", max_length=200,  unique=True)

    def __str__(self):
        return self.translator_name


class TrainText(models.Model):
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE)
    file = models.FileField(default='some file')

    def __str__(self):
        position = self.file.name.find('-')
        dot = self.file.name.find('.txt')
        return self.file.name[position+1:dot] if position != -1 else self.file.name[:dot]


class TestText(models.Model):
    file = models.FileField(default='some file')

    def __str__(self):
        dot = self.file.name.find('.')
        return self.file.name[:dot]


class AnalysisParam(models.Model):
    name = models.CharField("Назва параметра", max_length=200)
    code = models.IntegerField("Код", default=0)

    def __str__(self):
        return self.name


class TrainDictionary(models.Model):
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE)
    analysisParam = models.ForeignKey(AnalysisParam, on_delete=models.CASCADE)
    file = models.FileField(default='some file', storage=OverwriteStorage())

    def __str__(self):
        return self.file.name


class TestDictionary(models.Model):
    testText = models.ForeignKey(TestText, on_delete=models.CASCADE)
    analysisParam = models.ForeignKey(AnalysisParam, on_delete=models.CASCADE)
    file = models.FileField(default='some file', storage=OverwriteStorage())


class TotalNumEl(models.Model):
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE)
    analysisParam = models.ForeignKey(AnalysisParam, on_delete=models.CASCADE)
    value = models.FloatField("Загальна величина", default=0)

@receiver(pre_delete, sender=TrainText)
def traintext_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)

@receiver(pre_delete, sender=TestText)
def testtext_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)

@receiver(pre_delete, sender=TrainDictionary)
def traindictionary_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)

@receiver(pre_delete, sender=TestDictionary)
def testdictionary_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)