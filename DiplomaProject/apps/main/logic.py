import os
import xlsxwriter
from .models import Translator, TrainText, TestText, AnalysisParam, TestDictionary, TrainDictionary, TotalNumEl
import csv
from django.core.files import File


class Train:
    translators = []
    totals = dict()
    total_name = "_Total"
    Exceldocument = "Analysis.xlsx"
    testTexts = []
    analysisParams = None
    stopwords = []

    def __init__(self, translators, testTexts):
        self.translators = translators
        self.testTexts = testTexts
        self.analysisParams = AnalysisParam.objects.all().order_by('code')
        self.stopwords = []
        with open("trained/stop_words.txt", "r") as f:
            for line in f.readlines():
                self.stopwords.append(line.rstrip('\n'))

    def stop_words(self, text):

        words = text.split()
        without_stop_text = ""
        for stopword in self.stopwords:
            while stopword in words:
                words.remove(stopword)
        for word in words:
            without_stop_text += word + " "
        '''
        words = text.replace('\n',' ')
        for stop_word in self.stop_words:
            while stop_word + ' ' in words:
                words.replace(stop_word + ' ', ' ')
        while '  ' in words:
            words.replace('  ',' ')
            '''
        return without_stop_text

    def canonize(self, text):
        n = 8
        endings = [[]]
        with open("trained/endings.txt", "r") as f:
            for i in range(n):
                endings.append([])
            for line in f.readlines():
                endings[len(line) - 2].append(line.rstrip('\n'))
        words = text.split()
        canonized_text = ""
        for word in words:
            if word[-4:] == "ться":
                word = word[0:-4]
            if word[-3:] == "тся":
                word = word[0:-3]
            if word[-2:] == "сь" or word[-2:] == "ся" or word[-2:] == "ть":
                word = word[0:-2]
            for i in range(n, -1, -1):
                if len(word) > i + 2:
                    for end in endings[i]:
                        if word[-i - 1:] == end:
                            word = word[0:-i - 1]
            canonized_text += word + " "
        return canonized_text

    def count(self, text, length):
        res = dict()
        if length == 0:
            text = self.canonize(text)
            for key in text.replace('\n', ' ').split():
                if key in res:
                    res[key] += 1
                else:
                    res[key] = 1
        else:
            alphabet = set("йцукенгшщзхїфівапролджєячсмитьбюґ")
            for i in range(0, len(text) - length + 1):
                key = text[i:i + length]
                if set(key) < alphabet:
                    if key in res:
                        res[key] += 1
                    else:
                        res[key] = 1
        total = 0
        for key in res.keys():
            total += res[key]
        res[self.total_name] = total
        return res

    def count_freq(self, res, mode):
        if mode == "train":
            for key in res.keys():
                if not key == self.total_name:
                    res[key] *= 1 / res[self.total_name]
        elif mode == "test":
            for col in range(len(res)):
                for key in res[col].keys():
                    if not key == self.total_name:
                        res[col][key] *= 1 / res[col][self.total_name]
        return res

    def total_det_gram(self, res):
        max_length = 1000
        total_gram = dict()
        for col in range(len(res)):
            for key in res[col].keys():
                if key in total_gram:
                    total_gram[key] += res[col][key]
                else:
                    total_gram[key] = res[col][key]
        '''
        sorted_keys = [i[0] for i in sorted(total_gram.items(), key=lambda item: item[1], reverse=True)]
        for i in range(max_length,len(sorted_keys)):
            del total_gram[sorted_keys[i]]
        '''
        #total_gram[self.total_name] *= 2
        return total_gram

    def createDictionary(self, texts, mode):
        data = []
        for sh_i in self.analysisParams:
            print("Started ", sh_i)
            res = []
            for text in texts:
                res.append(self.count(text, sh_i.code))
            if mode == "train":
                res = self.total_det_gram(res)

            total_res = self.count_freq(res,mode)
            data.append(total_res)
        print("Finished dict")
        return data

    def writeDictionary(self, translator, translator_data):
        for num,analysisParam in enumerate(self.analysisParams):
            total_res = translator_data[num]
            analysisParamCode = analysisParam.code
            print("Started" + str(analysisParamCode))
            #analysisParam = AnalysisParam.objects.get(code=analysisParamCode)
            path = "trained/" + translator.translator_name + " " + analysisParam.name + ".csv"
            w = csv.writer(open(path, "w", newline=''))
            i = 0
            for key, val in total_res.items():
                i += 1
                w.writerow([key, val])
            print(i, path)
            obj, created = TrainDictionary.objects.get_or_create(translator=translator, analysisParam=analysisParam)
            w = csv.reader(open(path, "r", newline=''))
            if created:
                obj.file = File(open(path, 'r'))
                obj.save()
            else:
                obj.file.save(path, File(open(path, 'r')))
                print(obj.file.name)

    def clean(self, paths):
        english = "qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM"
        texts = []
        for path in paths:
            res = ""
            with open(path, "r", encoding="UTF-8") as f:
                for line in f.readlines():
                    if not line.isupper():
                        line = line.replace(chr(65279), '')
                        line = line.replace(chr(110), '')
                        line = line.replace(chr(1105), '')
                        for s in "1234567890!@#$%^&*()-=,:./;'\"?><↑…[]«»”“„–|—`’`—":
                            while s in line:
                                line = line.replace(s, '')
                        while "°" in line:
                            line = line.replace('°', 'ї')
                        while "i" in line:
                            line = line.replace('i', 'і')
                        while "c" in line:
                            line = line.replace('c', 'с')
                        for el in english:
                            while el in line:
                                line = line.replace(el, '')
                        while "  " in line:
                            line = line.replace("  ", " ")
                        if not ("Глава" in line and len(line) < 9):
                            res += line[:-1]
            texts.append(res.lower())
        return texts

    def difference(self, translator_dictionary, test_data): # на входе словари конкретного грамма
        results = []
        for test_dictionary in test_data:
            total = 0
            for key in test_dictionary.keys():
                if not key in translator_dictionary.keys():
                    translator_dictionary[key] = 0
            for key in translator_dictionary.keys():
                if not key == self.total_name:
                    if key in test_dictionary.keys():
                        total += abs(test_dictionary[key] - translator_dictionary[key])
                    #else:
                        #total += abs(test_dictionary[key])
            results.append(total)
        return results

    def analysis(self, test_data, train_data):
        differences = []
        for translator_dictionary in train_data:
            gram_translator = []
            for id,sh_i in enumerate(self.analysisParams):
                gram_translator.append(self.difference(translator_dictionary[id], test_data[id]))
            differences.append(gram_translator)
        return differences

    def writeExcel(self, differences):
        booklist = [text.file.name[:text.file.name.find('.')] for text in self.testTexts]
        translate_list = [translator.translator_name for translator in self.translators]
        workbook = xlsxwriter.Workbook(self.Exceldocument)
        worksheets = []
        worksheets.append(workbook.add_worksheet("Близькості"))
        for tr_id, translator in enumerate(translate_list):
            start_row = tr_id * (len(self.analysisParams) + 3)
            worksheets[-1].write(start_row, 0, translator)
            for col in range(len(booklist)):
                worksheets[-1].write(start_row + 1, col + 1, booklist[col])
            for id,sh_i in enumerate(self.analysisParams):
                worksheets[-1].write(start_row + 2 + id, 0, sh_i.name)
                for col in range(len(booklist)):
                    worksheets[-1].write(start_row + 2 + id, col + 1, differences[tr_id][id][col])


        worksheets.append(workbook.add_worksheet("Результати ідентифікації"))
        min_results = [[1 for i in booklist] for i in self.analysisParams]
        determined_translator = [["" for i in booklist] for i in self.analysisParams]
        for tr_id, translator in enumerate(translate_list):
            for id,sh_i in enumerate(self.analysisParams):
                for col in range(len(booklist)):
                    if differences[tr_id][id][col] < min_results[id][col]:
                        min_results[id][col] = differences[tr_id][id][col]
                        determined_translator[id][col] = translator
        for col in range(len(booklist)):
            worksheets[-1].write(0, col + 1, booklist[col])
        tr_results = []
        for id, sh_i in enumerate(self.analysisParams):
            tr_dict = dict()
            for translator in translate_list:
                tr_dict[translator] = 0
            tr_results.append(tr_dict)

        for id,sh_i in enumerate(self.analysisParams):
            worksheets[-1].write(id + 1, 0, sh_i.name)
            for col in range(len(booklist)):
                worksheets[-1].write(id + 1, col + 1, determined_translator[id][col])
                tr_results[id][determined_translator[id][col]] += 1
        start_row = len(self.analysisParams) + 3
        worksheets[-1].write(start_row, 0, "Загальні результати ідентифікації:")
        worksheets[-1].write(start_row + 1, 0, "Загальна кількість текстів: " + str(len(booklist)))
        for tr_id, translator in enumerate(translate_list):
            worksheets[-1].write(start_row + 3 + tr_id, 0, translator)
            for id, sh_i in enumerate(self.analysisParams):
                worksheets[-1].write(start_row + 2, id + 1, sh_i.name)
                worksheets[-1].write(start_row + 3 + tr_id, id + 1, tr_results[id][translator])

        workbook.close()

    def takeTrain(self):
        translatorRes = []
        for translator in self.translators:
            analysisParamRes = []
            for analysisParam in self.analysisParams:
                dictionary = dict()
                trainDictionary = TrainDictionary.objects.get(translator=translator, analysisParam=analysisParam)
                with open(trainDictionary.file.path, 'r', newline='\n') as fh:
                    rd = csv.reader(fh, delimiter=',')
                    for row in rd:
                        dictionary[row[0]] = float(row[1])
                analysisParamRes.append(dictionary)
            translatorRes.append(analysisParamRes)
        return translatorRes

    def train(self):
        for translator in self.translators:
            print(translator)
            trainTexts = TrainText.objects.filter(translator=translator)
            paths = [text.file.path for text in trainTexts]
            texts = self.clean(paths)
            translator_data = self.createDictionary(texts,"train")
            self.writeDictionary(translator, translator_data)

    def test(self):
        if self.translators != [] and self.testTexts != []:
            #self.analysisParams = AnalysisParam.objects.all().order_by('code')
            paths = [text.file.path for text in self.testTexts]
            texts = self.clean(paths)
            texts_dictionary = self.createDictionary(texts, "test")
            print("Анализировал тексты")
            translators_data = self.takeTrain()
            print("Считал csv")
            differences = self.analysis(texts_dictionary, translators_data)
            print("Провел анализ")
            self.writeExcel(differences)
            print("Записал в эксель")

            return self.Exceldocument
        return 0


