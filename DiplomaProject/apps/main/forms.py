from django import forms
from .models import Translator, TestText, TrainText


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class TranslatorForm(forms.Form):
    name = forms.CharField()


class transForm(forms.ModelForm):
    class Meta:
        model = Translator
        fields = ('translator_name',)


class TestTextForm(forms.ModelForm):
    class Meta:
        model = TestText
        fields = ('file',)


class TrainTextForm(forms.ModelForm):
    class Meta:
        model = TrainText
        fields = ('translator', 'file',)