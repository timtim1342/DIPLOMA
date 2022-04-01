from re import findall
from os.path import join
from os import listdir
import traceback

from toolbox2csv import op, wr
from numpy import mean


class Sentence:

    """"""

    def __init__(self, translation, words):

        """"""

        self.translation = translation
        self.words = words


class Pred:

    """"""

    def __init__(self, transcription, fin, index):

        """"""

        self.transcription = transcription  # можно сделать черех наследование
        self.fin = fin
        self.index = index


class RefDevice:

    """"""

    def __init__(self, transcription, n_arg, case, referent, index, typ):

        """"""

        self.transcription = transcription
        self.n_arg = n_arg
        self.case = case
        self.referent = referent
        self.typ = typ
        self.index = index


""" 

подготовка 
данных

"""


def parse_tsv(txt):

    """делит текст на строки по типу"""

    all_translation = [word.split('\t') for word in findall(r'Translation:(.*)', txt)]
    all_transcription = [word.split('\t') for word in findall(r'Transcription:(.*)', txt)]
    all_indexation = [word.split('\t') for word in findall(r'Indexation:(.*)', txt)]
    all_note = [word.split('\t') for word in findall(r'Note:(.*)', txt)]

    return all_translation, all_transcription, all_indexation, all_note


def word_former(word_transcription, word_indexation, word_note):

    """определяет тип слова"""

    if word_indexation != '':  # размеченное слово

        if 'pred' in word_indexation:  # предикат
            fin = word_note
            index = findall('\((\d+)\)', word_indexation)[0]

            word = Pred(word_transcription, fin, index)

        else:  # референциальное средство
            n_arg = 'NOTARG'
            case = 'NOCASE'

            try:
                referent = findall('([^/(]+)\(.+\)', word_indexation)[0]
                index = int(findall('\((\d+)\)', word_indexation)[0])

            except IndexError as e:
                print(word_transcription)
                raise e

            if word_transcription == 'Ø':
                typ = 'null'
            elif word_indexation[0].istitle():
                typ = 'NP'
            else:
                if 'ha' in word_transcription:
                    typ = 'dem_med'
                elif 'mi' in word_transcription:
                    typ = 'dem_prox'
                elif 'ti' in word_transcription:
                    typ = 'dem_dist'
                else:
                    typ = 'dem_self'

            if word_note != '':  # неаргумент

                try:
                    n_arg = findall('(\d+)\(', word_note)[0]
                    case = findall('\((.+)\)', word_note)[0]
                except IndexError as e:
                    print(word_transcription)
                    raise e


            word = RefDevice(word_transcription, n_arg, case, referent, index, typ)

    else:
        word = word_transcription

    return word


def tsv2list(all_translation, all_transcription, all_indexation, all_note):

    """приводит строки tsv к формату списка с классами в зависимости от типа разметки"""

    text = []
    for i in range(len(all_transcription)):
        sentence = []
        translation, transcription, indexation, note = all_translation[i], \
                                                       all_transcription[i], \
                                                       all_indexation[i], \
                                                       all_note[i]
        for j in range(len(transcription)):
            word = word_former(transcription[j], indexation[j], note[j])
            sentence.append(word)

        sentence = Sentence(all_translation[i][1], sentence)
        text.append(sentence)
    return text


"""

анализ
данных

 """


def wad(mean, context):

    WAD = 0

    for sentence in context[::-1]:
        for word in sentence.words[::-1]:
            if type(word) is RefDevice and word.typ == 'NP' and mean.referent == word.referent.lower() and mean.index > word.index:
                WAD = mean.index - word.index
                break
        else:
            continue
        break

    return WAD


def nad(mean, context):
    NAD = 0

    for sentence in context[::-1]:
        for word in sentence.words[::-1]:
            if type(word) is RefDevice and word.typ in ['dem_prox', 'dem_med', 'dem_dist', 'dem_self', 'null'] and mean.referent == word.referent.lower() and mean.index > word.index:
                NAD = mean.index - word.index
                break
        else:
            continue
        break

    return NAD

def ad_calc(text):
    sent_n = 0
    ad_list = []
    for sentence in text:
        for word in sentence.words:
            if type(word) is RefDevice and word.typ != 'NP':
                context = text[:sent_n + 1]
                NAD = nad(word, context)
                WAD = wad(word, context)

                if NAD == 0:
                    NAD = WAD

                ad_list.append([word, NAD, WAD])

        sent_n += 1

    return ad_list

def ad_mean(ad_list):
    ad_dict = {'null': {'wad': 0, 'nad': 0, 'count': 0},
               'dem_med': {'wad': 0, 'nad': 0, 'count': 0},
               'dem_prox': {'wad': 0, 'nad': 0, 'count': 0},
               'dem_dist': {'wad': 0, 'nad': 0, 'count': 0},
               'dem_self': {'wad': 0, 'nad': 0, 'count': 0}}
    ad_mean_dict = {}
    for ref_dev in ad_list:
        ad_dict[ref_dev[0].typ]['nad'] += ref_dev[1]
        ad_dict[ref_dev[0].typ]['wad'] += ref_dev[2]
        ad_dict[ref_dev[0].typ]['count'] += 1

    for tp in ad_dict.keys():
        try:
            mean_NAD = ad_dict[tp]['nad'] / ad_dict[tp]['count']
            mean_WAD = ad_dict[tp]['wad'] / ad_dict[tp]['count']
        except ZeroDivisionError:
            mean_NAD = 0
            mean_WAD = 0
        ad_mean_dict[tp] = {'mean_wad': mean_WAD, 'mean_nad': mean_NAD, 'count': ad_dict[tp]['count']}

    return ad_mean_dict

def ad_mean_all_texts(ad_mean_dict, ad_mean_dict_total):
    for key in ad_mean_dict.keys():
        for key2 in ad_mean_dict[key].keys():
            if ad_mean_dict[key][key2] != 0:
                ad_mean_dict_total[key][key2].append(ad_mean_dict[key][key2])

    return ad_mean_dict_total

def ad_count_mean(ad_mean_dict_total):
    for key in ad_mean_dict_total.keys():
        for key2 in ad_mean_dict_total[key].keys():
            if key2 == 'count':
                ad_mean_dict_total[key][key2] = sum(ad_mean_dict_total[key][key2])
            else:
                ad_mean_dict_total[key][key2] = mean(ad_mean_dict_total[key][key2])
    return ad_mean_dict_total

def rd(text):
    arg_n = 0
    overt_n = 0
    for sentence in text:
        for word in sentence.words:
            if type(word) is RefDevice and word.n_arg != 'NOTARG':
                arg_n += 1
                if word.typ in ['NP', 'dem']:
                    overt_n += 1

    RD = overt_n / arg_n
    return RD

def main():
    files = listdir('texts_done')
    ad_mean_dict_total = {'null': {'mean_wad': [], 'mean_nad': [], 'count': []},
                          'dem_med': {'mean_wad': [], 'mean_nad': [], 'count': []},
                          'dem_prox': {'mean_wad': [], 'mean_nad': [], 'count': []},
                          'dem_dist': {'mean_wad': [], 'mean_nad': [], 'count': []},
                          'dem_self': {'mean_wad': [], 'mean_nad': [], 'count': []}}

    for file in files:
        txt = op(join('texts_done', file))
        all_translation, all_transcription, all_indexation, all_note = parse_tsv(txt)

        try:
            text = tsv2list(all_translation, all_transcription, all_indexation, all_note)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
            print(file)

        ad_list = ad_calc(text)


        ad_mean_dict_total = ad_mean_all_texts(ad_mean(ad_list), ad_mean_dict_total)

        print(ad_mean(ad_list))

        print(rd(text))
        print()

    print('----------------------------------------\n', ad_mean_dict_total)
    ad_mean_dict_total = ad_count_mean(ad_mean_dict_total)
    print()
    print('========================================\n', ad_mean_dict_total)


if __name__ == '__main__':
    main()

