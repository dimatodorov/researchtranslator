import os

from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.edit import FormView
from .forms import FileFieldForm, TranslatorForm, transForm, TestTextForm, TrainTextForm
from django.shortcuts import render, get_object_or_404
from .models import Translator, TrainText, TestText, TrainDictionary
from .logic import Train
import mimetypes
from django.core.files.storage import FileSystemStorage

def home(request):
    return render(request, 'home.html')

def index(request):
    # translatorform(request)
    translatorForm = transForm()
    translator_list = Translator.objects.all()
    train_texts = TrainText.objects.all()
    test_texts = TestText.objects.all()
    return render(request, 'main.html',
                  {'translator_list': translator_list, 'train_texts': train_texts, 'test_texts': test_texts,
                   'translatorForm': translatorForm})


def analysis(request):
    translator_list = Translator.objects.all()
    test_texts = TestText.objects.all()
    trainDictionary = TrainDictionary.objects.all()
    return render(request, 'analysis.html',
                  {'translator_list': translator_list, 'test_texts': test_texts, 'trainDictionary': trainDictionary})


def makeAnalysis(request):
    if request.method == 'POST':
        data = request.POST.copy()
        print(data)
        translator_list = Translator.objects.all()
        checked_translator_list = []
        for translator in translator_list:
            if str(translator) in data.getlist('translators'):
                checked_translator_list.append(translator)
        test_texts_list = TestText.objects.all()
        checked_test_texts_list = []
        for test_text in test_texts_list:
            if str(test_text) in data.getlist('test-texts'):
                checked_test_texts_list.append(test_text)

        test = Train(translator_list,test_texts_list)
        file_path = test.test()
        if os.path.exists(file_path) and file_path != 0:
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
    return HttpResponse("<script>alert( 'Привет' );</script>")

def addTranslator(request):
    if request.method == 'POST':
        form = TranslatorForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
    if request.method == 'POST':
        form = transForm(request.POST)
        if form.is_valid():
            form.save()
    return index(request)


def deleteTranslator(request, tr_id):
    translator_obj = get_object_or_404(Translator, id=tr_id)
    translator_obj.delete()
    if request.method == 'POST':
        form = TranslatorForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
    return index(request)


def about(request):
    return render(request, 'about.html')


def uploadTestTexts(request):
    if request.method == "POST":
        files = request.FILES.getlist('document')
        for f in files:
            form = TestTextForm()
            instance = form.save(commit=False)
            instance.file = f

            instance.save()

    return analysis(request)


def uploadTranslatorFiles(request, tr_id):
    print(tr_id)
    translator_obj = get_object_or_404(Translator, id=tr_id)
    if request.method == "POST":
        files = request.FILES.getlist('document')
        for f in files:
            form = TrainTextForm()
            instance = form.save(commit=False)
            instance.file = f
            instance.file.name = translator_obj.translator_name + "-" + instance.file.name
            instance.translator = translator_obj
            instance.save()

    return index(request)


def deleteTranslatorFile(request, file_id):
    file_obj = get_object_or_404(TrainText, id=file_id)
    file_obj.delete()
    if request.method == 'POST':
        form = TranslatorForm(request.POST)
        if form.is_valid():
            file = form.cleaned_data['file']

    return index(request)


def deleteTestFile(request, file_id):
    file_obj = get_object_or_404(TestText, id=file_id)
    file_obj.delete()
    if request.method == 'POST':
        form = TranslatorForm(request.POST)
        if form.is_valid():
            file = form.cleaned_data['file']

    return analysis(request)
def deleteCheckedTestFiles(request):
    data = request.POST.copy().getlist('selected[]')
    print(data)

    for file_id in data:
        print(int(file_id))
        file_obj = get_object_or_404(TestText, id=int(file_id))
        file_obj.delete()
    return analysis(None)

def train(request):
    if request.method == "POST":
        print("Start")
        translator_list = Translator.objects.all()
        trains = Train(translator_list,None)
        trains.train()
    return index(request)
