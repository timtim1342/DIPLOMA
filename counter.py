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

    def __init__(self, transcription, n_arg, case, referent, index, typ, number, anim):

        """"""

        self.transcription = transcription
        self.n_arg = n_arg
        self.case = case
        self.referent = referent
        self.typ = typ
        self.index = index
        self.number = number
        self.anim = anim

class PredNotFound(Exception):
    pass


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
            index = int(findall('\((\d+)\)', word_indexation)[0])

            word = Pred(word_transcription, fin, index)

        else:  # референциальное средство
            n_arg = 'NOTARG'
            case = 'NOCASE'

            try:
                referent = findall('([^/(]+)\(.+\)', word_indexation)[0]
                index = int(findall('\((\d+)\)', word_indexation)[0])
                number = 'PL' if referent.lower() in ['pear', 'boys'] else 'SG'
                anim = 'ANIM' if referent.lower() in ['boy', 'boy2', 'boy3', 'boy4' 'boys', 'man', 'man2', 'girl',
                                                      'rooster'] else 'NANIM'

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


            word = RefDevice(word_transcription, n_arg, case, referent, index, typ, number, anim)

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

def get_pred(context, index):

    """поиск предиката по индексу"""

    for sentence in context:
        for word in sentence.words:
            if type(word) is Pred and index == word.index:
                return word
    raise PredNotFound('Предикат не найден.')

"""

анализ
данных

 """

def wad(mean, context):

    WAD = 0
    fin_pred = 0

    for sentence in context[::-1]:
        for word in sentence.words[::-1]:
            if type(word) is Pred and word.fin == 'Fin' and word.index != mean.index:
                #print(word.transcription, word.fin, word.index, mean.referent + str(mean.index), fin_pred + 1)
                fin_pred += 1
            elif type(word) is RefDevice and word.typ == 'NP' and mean.referent == word.referent.lower() and mean.index > word.index:
                WAD = fin_pred

                ant_pred = get_pred(context, word.index)
                WAD += ant_pred.fin == 'Fin'
                break
        else:
            continue
        break

    return WAD


def nad(mean, context):
    NAD = 0
    fin_pred = 0

    for sentence in context[::-1]:
        for word in sentence.words[::-1]:
            if type(word) is Pred and word.fin == 'Fin' and word.index != mean.index:
                #print(word.transcription, word.fin, word.index, mean.referent + str(mean.index), fin_pred + 1)
                fin_pred += 1
            elif type(word) is RefDevice and word.typ in ['dem_prox', 'dem_med', 'dem_dist', 'dem_self', 'null', 'NP'] and mean.referent == word.referent.lower() and mean.index > word.index:
                NAD = fin_pred

                ant_pred = get_pred(context, word.index)
                NAD += ant_pred.fin == 'Fin'
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

                print(word.referent + str(word.index), NAD, WAD)

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
    arg_n, overt_n = 0, 0
    arg_sg_n, overt_sg_n = 0, 0
    arg_pl_n, overt_pl_n = 0, 0
    arg_an_n, overt_an_n = 0, 0
    arg_nan_n, overt_nan_n = 0, 0

    for sentence in text:
        for word in sentence.words:
            if type(word) is RefDevice and word.n_arg != 'NOTARG':
                arg_n += 1

                if word.number == 'SG':
                    arg_sg_n += 1
                else:
                    arg_pl_n += 1

                if word.anim == 'ANIM':
                    arg_an_n += 1
                else:
                    arg_nan_n += 1

                if word.typ in ['NP', 'dem']:
                    overt_n += 1

                    if word.number == 'SG':
                        overt_sg_n += 1
                    else:
                        overt_pl_n += 1

                    if word.anim == 'ANIM':
                        overt_an_n += 1
                    else:
                        overt_nan_n += 1

    RD = overt_n / arg_n
    RD_SG = overt_sg_n / arg_sg_n
    RD_PL = overt_pl_n / arg_pl_n
    RD_AN = overt_an_n / arg_an_n
    RD_NAN = overt_nan_n / arg_nan_n

    RD_dict = {'RD': RD,
               'RD_SG': RD_SG,
               'RD_PL': RD_PL,
               'RD_AN': RD_AN,
               'RD_NAN': RD_NAN,
               'arg_n': arg_n,
               'arg_sg_n': arg_sg_n,
               'arg_pl_n': arg_pl_n,
               'arg_an_n': arg_an_n,
               'arg_nan_n': arg_nan_n

    }

    return RD_dict

"""

запись
данных

"""

def write_ad(file_name, pear_name, ad_data):

    """записывает данные по AD в таблицу (обращается не по индексу, проблема?)"""

    line = pear_name + '\t' + \
             '\t'.join(map(str, [ad_data['null']['mean_wad'], ad_data['null']['mean_nad'], ad_data['null']['count'],
                        ad_data['dem_med']['mean_wad'], ad_data['dem_med']['mean_nad'], ad_data['dem_med']['count'],
                        ad_data['dem_prox']['mean_wad'], ad_data['dem_prox']['mean_nad'], ad_data['dem_prox']['count'],
                        ad_data['dem_dist']['mean_wad'], ad_data['dem_dist']['mean_nad'], ad_data['dem_dist']['count'],
                        ad_data['dem_self']['mean_wad'], ad_data['dem_self']['mean_nad'], ad_data['dem_self']['count']])
                       )

    wr(file_name, line + '\n')

def write_rd(file_name, pear_name, rd_data):

    """записывает данные по RD в таблицу"""

    line = pear_name + '\t' + \
             '\t'.join(map(str, [rd_data['RD'], rd_data['arg_n'],
                                 rd_data['RD_SG'], rd_data['arg_sg_n'],
                                 rd_data['RD_PL'], rd_data['arg_pl_n'],
                                 rd_data['RD_AN'], rd_data['arg_an_n'],
                                 rd_data['RD_NAN'], rd_data['arg_nan_n']
                                 ])
                       )

    wr(file_name, line + '\n')


def main():
    files = listdir('texts_done')
    ad_mean_dict_total = {'null': {'mean_wad': [], 'mean_nad': [], 'count': []},
                          'dem_med': {'mean_wad': [], 'mean_nad': [], 'count': []},
                          'dem_prox': {'mean_wad': [], 'mean_nad': [], 'count': []},
                          'dem_dist': {'mean_wad': [], 'mean_nad': [], 'count': []},
                          'dem_self': {'mean_wad': [], 'mean_nad': [], 'count': []}}

    file_name_ad = 'results_ad.tsv'
    file_name_rd = 'results_rd.tsv'

    header_ad = 'pear name\t' + \
             'WAD_Fin_null\tNAD_Fin_null\tcount_null\t' +\
             'WAD_Fin_dem_med\tNAD_Fin_dem_med\tcount_dem_med\t' + \
             'WAD_Fin_dem_prox\tNAD_Fin_dem_prox\tcount_dem_prox\t' + \
             'WAD_Fin_dem_dist\tNAD_Fin_dem_dist\tcount_dem_dist\t' + \
             'WAD_Fin_dem_self\tNAD_Fin_dem_self\tcount_dem_self\t'

    header_rd = 'pear name\t' + \
                '\t'.join(['RD', 'arg_n',
                           'RD_SG', 'arg_sg_n',
                           'RD_PL', 'arg_pl_n',
                           'RD_AN', 'arg_an_n',
                           'RD_NAN', 'arg_nan_n'])

    with open(file_name_ad, 'w', encoding='utf-8') as f:
        f.write(header_ad + '\n')
    with open(file_name_rd, 'w', encoding='utf-8') as f:
        f.write(header_rd + '\n')

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

        write_ad(file_name_ad, file, ad_mean(ad_list))
        write_rd(file_name_rd, file, rd(text))

    ad_mean_dict_total = ad_count_mean(ad_mean_dict_total)

    # print()
    # print('========================================\n', ad_mean_dict_total)

    write_ad(file_name_ad, 'TOTAL', ad_mean_dict_total)


if __name__ == '__main__':
    main()

