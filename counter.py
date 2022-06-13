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

    def __init__(self, transcription, fin, index, switchref=None):

        """"""

        self.transcription = transcription  # можно сделать черех наследование
        self.fin = fin
        self.index = index
        self.switchref = switchref


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
            fin = word_note.split('.')[0]
            switchref = word_note.split('.')[1]
            index = int(findall('\((\d+)\)', word_indexation)[0])

            word = Pred(word_transcription, fin, index, switchref)

        else:  # референциальное средство
            n_arg = 'NOTARG'
            case = 'NOCASE'

            try:
                referent = findall('([^/(]+)\(.+\)', word_indexation)[0]
                index = int(findall('\((\d+)\)', word_indexation)[0])
                number = 'PL' if referent.lower() in ['pear', 'boys'] else 'SG'
                anim = 'ANIM' if referent.lower() in ['boy', 'boy2', 'boy3', 'boy4', 'boys', 'man', 'man2', 'girl',
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
                    print(word_transcription, index)
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
    raise PredNotFound('Предикат не найден для слова с номером ' + str(index))


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
            elif type(word) is RefDevice and word.typ == 'NP' and mean.referent.lower() == word.referent.lower() and mean.index > word.index:
                WAD = fin_pred

                ant_pred = get_pred(context, word.index)
                WAD += ant_pred.fin == 'Fin'
                break
        else:
            continue
        break

    return [WAD, word]


def nad(mean, context):
    NAD = 0
    fin_pred = 0

    for sentence in context[::-1]:
        for word in sentence.words[::-1]:
            if type(word) is Pred and word.fin == 'Fin' and word.index != mean.index:
                #print(word.transcription, word.fin, word.index, mean.referent + str(mean.index), fin_pred + 1)
                fin_pred += 1
            elif type(word) is RefDevice and word.typ in ['dem_prox', 'dem_med', 'dem_dist', 'dem_self', 'null', 'NP'] and mean.referent.lower() == word.referent.lower() and mean.index > word.index:
                NAD = fin_pred

                ant_pred = get_pred(context, word.index)
                NAD += ant_pred.fin == 'Fin'
                break
        else:
            continue
        break

    return [NAD, word]

def ad_calc(text):
    sent_n = 0
    ad_list = []
    for sentence in text:
        for word in sentence.words:
            if type(word) is RefDevice:  # and word.typ != 'NP'
                context = text[:sent_n + 1]
                NAD, target_nad = nad(word, context)
                WAD, target_wad = wad(word, context)


                print(word.referent + str(word.index), NAD, WAD)

                ad_list.append([word, NAD, WAD, target_nad, target_wad])

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

    arg_0_n, overt_0_n = 0, 0
    arg_1_n, overt_1_n = 0, 0
    arg_2_n, overt_2_n = 0, 0
    arg_3_n, overt_3_n = 0, 0

    arg_abs_n, overt_abs_n = 0, 0
    arg_erg_n, overt_erg_n = 0, 0
    arg_dat_n, overt_dat_n = 0, 0
    arg_loc_n, overt_loc_n = 0, 0

    arg_fin_n, overt_fin_n = 0, 0
    arg_nfin_n, overt_nfin_n = 0, 0

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

                if word.n_arg == '0':
                    arg_0_n += 1
                elif word.n_arg == '1':
                    arg_1_n += 1
                elif word.n_arg == '2':
                    arg_2_n += 1
                elif word.n_arg == '3':
                    arg_3_n += 1

                if word.case == 'ABS':
                    arg_abs_n += 1
                elif word.case == 'ERG':
                    arg_erg_n += 1
                elif word.case == 'DAT':
                    arg_dat_n += 1
                elif word.case == 'LOC':
                    arg_loc_n += 1

                if get_pred(text, word.index).fin == 'Fin':
                    arg_fin_n += 1
                else:
                    arg_nfin_n += 1

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

                    if word.n_arg == '0':
                        overt_0_n += 1
                    elif word.n_arg == '1':
                        overt_1_n += 1
                    elif word.n_arg == '2':
                        overt_2_n += 1
                    elif word.n_arg == '3':
                        overt_3_n += 1

                    if word.case == 'ABS':
                        overt_abs_n += 1
                    elif word.case == 'ERG':
                        overt_erg_n += 1
                    elif word.case == 'DAT':
                        overt_dat_n += 1
                    elif word.case == 'LOC':
                        overt_loc_n += 1

                    if get_pred(text, word.index).fin == 'Fin':
                        overt_fin_n += 1
                    else:
                        overt_nfin_n += 1

    RD = overt_n / arg_n

    RD_SG = overt_sg_n / arg_sg_n
    RD_PL = overt_pl_n / arg_pl_n

    RD_AN = overt_an_n / arg_an_n
    RD_NAN = overt_nan_n / arg_nan_n

    RD_0 = overt_0_n / arg_0_n
    RD_1 = overt_1_n / arg_1_n
    RD_2 = overt_2_n / arg_2_n
    RD_3 = overt_3_n / arg_3_n

    RD_ABS = overt_abs_n / arg_abs_n
    RD_ERG = overt_erg_n / arg_erg_n
    RD_DAT = overt_dat_n / arg_dat_n
    try:
        RD_LOC = overt_loc_n / arg_loc_n
    except:
        RD_LOC = 'ND'

    try:
        RD_FIN = overt_fin_n / arg_fin_n
    except:
        RD_FIN = 'ND'

    RD_NFIN = overt_nfin_n / arg_nfin_n

    RD_dict = {'RD': RD,
               'RD_SG': RD_SG,
               'RD_PL': RD_PL,
               'RD_AN': RD_AN,
               'RD_NAN': RD_NAN,
               'RD_0': RD_0,
               'RD_1': RD_1,
               'RD_2': RD_2,
               'RD_3': RD_3,
               'RD_ABS': RD_ABS,
               'RD_ERG': RD_ERG,
               'RD_DAT': RD_DAT,
               'RD_LOC': RD_LOC,
               'RD_FIN': RD_FIN,
               'RD_NFIN': RD_NFIN,
               'arg_n': arg_n,
               'arg_sg_n': arg_sg_n,
               'arg_pl_n': arg_pl_n,
               'arg_an_n': arg_an_n,
               'arg_nan_n': arg_nan_n,
               'arg_0_n': arg_0_n,
               'arg_1_n': arg_1_n,
               'arg_2_n': arg_2_n,
               'arg_3_n': arg_3_n,
               'arg_abs_n': arg_abs_n,
               'arg_erg_n': arg_erg_n,
               'arg_dat_n': arg_dat_n,
               'arg_loc_n': arg_loc_n,
               'arg_fin_n': arg_fin_n,
               'arg_nfin_n': arg_nfin_n

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
                                 rd_data['RD_NAN'], rd_data['arg_nan_n'],
                                 rd_data['RD_0'], rd_data['arg_0_n'],
                                 rd_data['RD_1'], rd_data['arg_1_n'],
                                 rd_data['RD_2'], rd_data['arg_2_n'],
                                 rd_data['RD_3'], rd_data['arg_3_n'],
                                 rd_data['RD_ABS'], rd_data['arg_abs_n'],
                                 rd_data['RD_ERG'], rd_data['arg_erg_n'],
                                 rd_data['RD_DAT'], rd_data['arg_dat_n'],
                                 rd_data['RD_LOC'], rd_data['arg_loc_n'],
                                 rd_data['RD_FIN'], rd_data['arg_fin_n'],
                                 rd_data['RD_NFIN'], rd_data['arg_nfin_n']
                                 ])
                       )

    wr(file_name, line + '\n')

def write_data4rd_r(file_name, pear_name, text):
    """записывает данные по тексту в таблицу для R"""
    text_line = ''

    for sentence in text:
        for word in sentence.words:
            if type(word) is RefDevice:
                word_pred = get_pred(text, word.index)
                text_line += '\t'.join([pear_name, word.transcription, word.referent, str(word.index), word.typ, word.n_arg,
                                        word.number, word.case, word.anim, word_pred.transcription, word_pred.fin, word_pred.switchref
                                        ]) + '\n'
    wr(file_name, text_line)


def write_ad_r(file_name, pear_name, ad_data):

    """записывает данные по AD в таблицу R формат (обращается не по индексу, проблема?)"""

    for ref_dev in ad_data:
        word, NAD, WAD, target_nad, target_wad = ref_dev
        if not type(target_nad) is RefDevice or not type(target_wad) is RefDevice:
            target_nad_transcription, target_nad_index, target_nad_arg, target_wad_transcription, target_wad_index, target_wad_arg = \
                'ND', 'ND', 'ND', 'ND', 'ND', 'ND'
        else:
            target_nad_transcription, target_nad_index, target_nad_arg, target_wad_transcription, target_wad_index, target_wad_arg =\
                target_nad.transcription, str(target_nad.index), target_nad.n_arg, target_wad.transcription, str(target_wad.index), target_wad.n_arg

        line = '\t'.join([word.transcription,
                          word.referent,
                          word.typ,
                          word.n_arg,
                          str(word.index),
                          str(NAD),
                          str(WAD),
                          target_nad_transcription,
                          target_nad_index,
                          target_nad_arg,
                          target_wad_transcription,
                          target_wad_index,
                          target_wad_arg,
                          pear_name])

        wr(file_name, line + '\n')

def main():
    # KINA
    # files = listdir(join('texts_done', 'KINA'))
    # ad_mean_dict_total = {'null': {'mean_wad': [], 'mean_nad': [], 'count': []},
    #                       'dem_med': {'mean_wad': [], 'mean_nad': [], 'count': []},
    #                       'dem_prox': {'mean_wad': [], 'mean_nad': [], 'count': []},
    #                       'dem_dist': {'mean_wad': [], 'mean_nad': [], 'count': []},
    #                       'dem_self': {'mean_wad': [], 'mean_nad': [], 'count': []}}
    #
    # file_name_ad = 'results_ad_kina.tsv'
    # file_name_rd = 'results_rd_kina.tsv'
    #
    # header_ad = 'pear name\t' + \
    #          'WAD_Fin_null\tNAD_Fin_null\tcount_null\t' +\
    #          'WAD_Fin_dem_med\tNAD_Fin_dem_med\tcount_dem_med\t' + \
    #          'WAD_Fin_dem_prox\tNAD_Fin_dem_prox\tcount_dem_prox\t' + \
    #          'WAD_Fin_dem_dist\tNAD_Fin_dem_dist\tcount_dem_dist\t' + \
    #          'WAD_Fin_dem_self\tNAD_Fin_dem_self\tcount_dem_self\t'
    #
    # header_rd = 'pear name\t' + \
    #             '\t'.join(['RD', 'arg_n',
    #                        'RD_SG', 'arg_sg_n',
    #                        'RD_PL', 'arg_pl_n',
    #                        'RD_AN', 'arg_an_n',
    #                        'RD_NAN', 'arg_nan_n',
    #                        'RD_0', 'arg_0_n',
    #                        'RD_1', 'arg_1_n',
    #                        'RD_2', 'arg_2_n',
    #                        'RD_3', 'arg_3_n',
    #                        'RD_ABS', 'arg_abs_n',
    #                        'RD_ERG', 'arg_erg_n',
    #                        'RD_DAT', 'arg_dat_n',
    #                        'RD_LOC', 'arg_loc_n',
    #                        'RD_FIN', 'arg_fin_n',
    #                        'RD_NFIN', 'arg_nfin_n'
    #                        ])
    #
    # with open(file_name_ad, 'w', encoding='utf-8') as f:
    #     f.write(header_ad + '\n')
    # with open(file_name_rd, 'w', encoding='utf-8') as f:
    #     f.write(header_rd + '\n')
    #
    # for file in files:
    #     print(file)
    #     txt = op(join('texts_done', 'KINA', file))
    #     all_translation, all_transcription, all_indexation, all_note = parse_tsv(txt)
    #
    #     try:
    #         text = tsv2list(all_translation, all_transcription, all_indexation, all_note)
    #     except Exception as ex:
    #         print(ex)
    #         print(traceback.format_exc())
    #         print(file)
    #
    #     ad_list = ad_calc(text)
    #     ad_mean_dict_total = ad_mean_all_texts(ad_mean(ad_list), ad_mean_dict_total)
    #
    #     write_ad(file_name_ad, file, ad_mean(ad_list))
    #     write_rd(file_name_rd, file, rd(text))
    #
    # ad_mean_dict_total = ad_count_mean(ad_mean_dict_total)
    #
    # # print()
    # # print('========================================\n', ad_mean_dict_total)
    #
    # write_ad(file_name_ad, 'TOTAL', ad_mean_dict_total)


    # RD to R
    files = listdir(join('texts_done', 'KINA'))

    file_name_rd = 'results_data4rd_r_kina.tsv'
    header_ad = 'pear\ttrans\treferent\tindex\ttype\tn_arg\tnumber\tcase\tanim\tpred\tfin\tswitchref'
    with open(file_name_rd, 'w', encoding='utf-8') as f:
        f.write(header_ad + '\n')

    for file in files:
        print(file)
        txt = op(join('texts_done', 'KINA', file))
        all_translation, all_transcription, all_indexation, all_note = parse_tsv(txt)

        try:
            text = tsv2list(all_translation, all_transcription, all_indexation, all_note)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
            print(file)

        write_data4rd_r(file_name_rd, file, text)


    # # AD to R
    # files = listdir(join('texts_done', 'KINA'))
    #
    # file_name_ad = 'results_ad_r_kina.tsv'
    # header_ad = 'refdef\treferent\treftype\tref_n_arg\tindex\tnad\twad\ttarg_nad\ttarg_nad_ind\ttarg_nad_arg\ttarg_wad\ttarg_wad_ind\ttarg_wad_arg\tpearname'
    # with open(file_name_ad, 'w', encoding='utf-8') as f:
    #     f.write(header_ad + '\n')
    #
    # for file in files:
    #     print(file)
    #     txt = op(join('texts_done', 'KINA', file))
    #     all_translation, all_transcription, all_indexation, all_note = parse_tsv(txt)
    #
    #     try:
    #         text = tsv2list(all_translation, all_transcription, all_indexation, all_note)
    #     except Exception as ex:
    #         print(ex)
    #         print(traceback.format_exc())
    #         print(file)
    #
    #
    #     ad_list = ad_calc(text)
    #     write_ad_r(file_name_ad, file, ad_list)


    # # MEHWEB-SANZHI
    # files = listdir(join('texts_done', 'SANZHI'))
    # file_name_rd = 'results_rd_sanzhi.tsv'
    # header_rd = 'pear name\t' + \
    #             '\t'.join(['RD', 'arg_n',
    #                        'RD_SG', 'arg_sg_n',
    #                        'RD_PL', 'arg_pl_n',
    #                        'RD_AN', 'arg_an_n',
    #                        'RD_NAN', 'arg_nan_n',
    #                        'RD_0', 'arg_0_n',
    #                        'RD_1', 'arg_1_n',
    #                        'RD_2', 'arg_2_n',
    #                        'RD_3', 'arg_3_n',
    #                        'RD_ABS', 'arg_abs_n',
    #                        'RD_ERG', 'arg_erg_n',
    #                        'RD_DAT', 'arg_dat_n',
    #                        'RD_LOC', 'arg_loc_n',
    #                        'RD_FIN', 'arg_fin_n',
    #                        'RD_NFIN', 'arg_nfin_n'
    #                        ])
    # with open(file_name_rd, 'w', encoding='utf-8') as f:
    #     f.write(header_rd + '\n')
    #
    # for file in files:
    #     print(file)
    #     txt = op(join('texts_done', 'SANZHI', file))
    #     all_translation, all_transcription, all_indexation, all_note = parse_tsv(txt)
    #
    #     try:
    #         text = tsv2list(all_translation, all_transcription, all_indexation, all_note)
    #     except Exception as ex:
    #         print(ex)
    #         print(traceback.format_exc())
    #         print(file)
    #
    #     write_rd(file_name_rd, file, rd(text))


if __name__ == '__main__':
    main()

