from re import findall, sub

from os.path import join
from os import getcwd, listdir

from toolbox2csv import op, wr

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

    def __init__(self, transcription, n_arg, case, referent, index, type):
        """"""
        self.transcription = transcription
        self.n_arg = n_arg
        self.case = case
        self.referent = referent
        self.type = type
        self.index = index

def parse_table(txt):
    """делит текст на строки по типу"""
    all_translation = [word.split('\t') for word in findall(r'Translation:(.*)', txt)]
    all_transcription = [word.split('\t') for word in findall(r'Transcription:(.*)', txt)]
    all_indexation = [word.split('\t') for word in findall(r'Indexation:(.*)', txt)]
    all_note = [word.split('\t') for word in findall(r'Note:(.*)', txt)]

    return all_translation, all_transcription, all_indexation, all_note

def main():
    files = listdir('texts_done')
    for file in files:
        txt = op(join('texts_done', file))
        all_translation, all_transcription, all_indexation, all_note = parse_table(txt)


    # ... все что ниже на одну табуляцию сместить

    text = []

    for i in range(len(all_transcription)):
        sentence = []
        translation, transcription, indexation, note = all_translation[i],\
                                                       all_transcription[i],\
                                                       all_indexation[i],\
                                                       all_note[i]
        for j in range(len(transcription)):
            if indexation[j] != '':  # размеченное слово

                if 'pred' in indexation[j]:  # предикат
                    fin = note[j]
                    index = findall('\((\d+)\)', indexation[j])[0]

                    word = Pred(transcription[j], fin, index)

                else:  # референциальное средство
                    n_arg = 'NOTARG'
                    case = 'NOCASE'
                    referent = findall('([^/(]+)\(.+\)', indexation[j])[0]
                    index = findall('\((\d+)\)', indexation[j])[0]

                    if transcription[j] == 'Ø':
                        type = 'null'
                    elif indexation[j][0].istitle():
                        type = 'NP'
                    else:
                        type = 'dem'

                    if note[j] != '':  # неаргумент
                        n_arg = findall('(\d+)\(', note[j])[0]
                        case = findall('\((.+)\)', note[j])[0]

                    word = RefDevice(transcription[j], n_arg, case, referent, index, type)

            else:
                word = transcription[j]

            sentence.append(word)

        sentence = Sentence(all_translation[i][1], sentence)
        text.append(sentence)





if __name__ == '__main__':
    main()



#
#
# def arguments_list(name):  # переделать в класс
#
#     arg_list = []
#
#     text = open_text(name)
#     transcription = [word.split('\t') for word in findall(r'Transcription:(.*)', text)]
#     note = [word.split('\t') for word in findall(r'Note:(.*)', text)]
#
#     for i in range(len(note)):
#         for j in range(len(note[i])):
#             if note[i][j].startswith(('0', '1', '2', '3')):
#                 arg_list.append([note[i][j], transcription[i][j]])
#
#     return arg_list
#
# def fin_arguments_list(name):  # отдельно для финитности и нет (привиньтить к предыд функц; вообще переделать урода)
#
#     f_arg_list = []
#     nf_arg_list = []
#
#     arg_list = []  # костыль для аргум для pred(i)
#
#     text = open_text(name)
#     transcription = [word.split('\t') for word in findall(r'Transcription:(.*)', text)]
#     note = [word.split('\t') for word in findall(r'Note:(.*)', text)]
#     indexation = [word.split('\t') for word in findall(r'Indexation:(.*)', text)]
#
#     for i in range(len(note)):
#
#             if 'pred' in indexation[i]:  # для предложений с одним пред
#
#                 if 'Fin' in note[i]:
#                     for j in range(len(note[i])):
#                         if note[i][j].startswith(('0', '1', '2', '3')):
#                             f_arg_list.append([note[i][j], transcription[i][j]])
#
#                 else:  # elif 'NFin' not in note[i] для конвербов
#                     for j in range(len(note[i])):
#                         if note[i][j].startswith(('0', '1', '2', '3')):
#                             nf_arg_list.append([note[i][j], transcription[i][j]])
#
#             elif 'pred(i)' in indexation[i]:  # для пред с неск пред
#
#                 arg_list = []
#                 for j in range(len(note[i])):  # костыль
#
#                     if note[i][j].startswith(('0', '1', '2', '3')):
#                         arg_list.append([note[i][j], transcription[i][j], indexation[i][j]])
#
#                 for j in range(len(note[i])):
#                     if note[i][j] == 'Fin':
#                         index = indexation[i][j][-2:-1]
#                         for arg in arg_list:
#                             if arg[2][-2:-1] == index:
#                                 f_arg_list.append([arg[0], arg[1]])
#                     elif 'pred' in indexation[i][j] and note[i][j] != 'Fin':  # and note[i][j] != 'NFin' для конвербов
#                         index = indexation[i][j][-2:-1]
#                         for arg in arg_list:
#                             if arg[2][-2:-1] == index:
#                                 nf_arg_list.append([arg[0], arg[1]])
#
#
#
#
#     return f_arg_list, nf_arg_list
#
# def argum_referential_density(name):  # для рд для разных падежей и аргум позиц
#     f_arg_list, nf_arg_list = fin_arguments_list(name)
#     fin_dict, nfin_dict = {}, {}
#     total_f_dict, total_nf_dict = {}, {}
#
#     for argum in f_arg_list:
#         if argum[0] in fin_dict.keys():
#             fin_dict[argum[0]].append(argum[1])
#         else:
#             fin_dict[argum[0]] = [argum[1]]
#
#     for argum in nf_arg_list:
#         if argum[0] in nfin_dict.keys():
#             nfin_dict[argum[0]].append(argum[1])
#         else:
#             nfin_dict[argum[0]] = [argum[1]]
#
#
#
#
#     for key in fin_dict.keys():
#         fin_nulls = 0
#         fin_NPs = 0
#         for argum in fin_dict[key]:
#
#             if argum == 'Ø':
#                 fin_nulls += 1
#             else:
#                 fin_NPs += 1
#
#         fin_RD = fin_NPs / (fin_NPs + fin_nulls)
#         total_f_dict[key] = [fin_RD, fin_nulls, fin_NPs]
#
#     for key in nfin_dict.keys():
#         nfin_nulls = 0
#         nfin_NPs = 0
#         for argum in nfin_dict[key]:
#
#             if argum == 'Ø':
#                 nfin_nulls += 1
#             else:
#                 nfin_NPs += 1
#
#         nfin_RD = nfin_NPs / (nfin_NPs + nfin_nulls)
#         total_nf_dict[key] = [nfin_RD, nfin_nulls, nfin_NPs]
#
#     return total_f_dict, total_nf_dict
#
# def rd_w():  # специально для предыд ф, чтобы не засорять
#     texts = all_texts()
#     with open('RD_per_arg.tsv', 'w', encoding='UTF-8') as f:
#         f.write(
#             'TEXT_NAME\tFiniteness\tArgum\tRD\tnulls\tNPs\n')
#     for name in texts:
#         total_f_dict, total_nf_dict = argum_referential_density(name)
#         with open('RD_per_arg.tsv', 'a', encoding='UTF-8') as f:
#             for key in total_f_dict:
#                 f.write(name + '\t')
#                 f.write('Fin' + '\t' +
#                         key + '\t' +
#                         str(total_f_dict[key][0]) + '\t' +
#                         str(total_f_dict[key][1]) + '\t' +
#                         str(total_f_dict[key][2]) + '\n')
#             for key in total_nf_dict:
#                 f.write(name + '\t')
#                 f.write('NFin' + '\t' +
#                         key + '\t' +
#                         str(total_nf_dict[key][0]) + '\t' +
#                         str(total_nf_dict[key][1]) + '\t' +
#                         str(total_nf_dict[key][2]) + '\n')
#
# def fin_referential_density(name):
#     f_arg_list, nf_arg_list = fin_arguments_list(name)
#     fin_nulls = 0
#     fin_NPs = 0
#     nfin_nulls = 0
#     nfin_NPs = 0
#
#     for i in range(len(f_arg_list)):
#         if f_arg_list[i][1] == 'Ø':
#             fin_nulls += 1
#         else:
#             fin_NPs += 1
#
#     fin_RD = fin_NPs / (fin_NPs + fin_nulls)
#
#     for i in range(len(nf_arg_list)):
#         if f_arg_list[i][1] == 'Ø':
#             nfin_nulls += 1
#         else:
#             nfin_NPs += 1
#
#     nfin_RD = nfin_NPs / (nfin_NPs + nfin_nulls)
#
#
#     return fin_nulls, fin_NPs, fin_RD, nfin_nulls, nfin_NPs, nfin_RD
#
#
#
# def referential_density(name):
#     text = open_text(name)
#     arg_list = arguments_list(name)
#     total_nuls = []
#     total_NPs = []
#
#     for argument in arg_list:
#         if argument[1] == 'Ø':
#             total_nuls.append(argument)
#         else:
#             total_NPs.append(argument)
#
#     nuls = len(total_nuls)
#     NPs = len(total_NPs)
#     rd = NPs / (NPs + nuls)
#     return rd, nuls, NPs
#
# def omission_stat(name):
#     text = open_text(name)
#     arg_list = arguments_list(name)
#     zero_NPs, one_NPs, two_NPs, three_NPs = [], [], [], []
#     zero_null, one_null, two_null, three_null = [], [], [], []
#     case_dict = {}
#
#     for argument in arg_list:
#         if argument[0].startswith('0'):
#             if argument[1] == 'Ø':
#                 zero_null.append(argument)
#             else:
#                 zero_NPs.append(argument)
#         elif argument[0].startswith('1'):
#             if argument[1] == 'Ø':
#                 one_null.append(argument)
#             else:
#                 one_NPs.append(argument)
#         elif argument[0].startswith('2'):
#             if argument[1] == 'Ø':
#                 two_null.append(argument)
#             else:
#                 two_NPs.append(argument)
#         else:
#             if argument[1] == 'Ø':
#                 three_null.append(argument)
#             else:
#                 three_NPs.append(argument)
#
#     zero_density = len(zero_NPs) / (len(zero_NPs) + len(zero_null))
#     one_density = len(one_NPs) / (len(one_NPs) + len(one_null))
#     two_density = len(two_NPs) / (len(two_NPs) + len(two_null))
#     three_density = len(three_NPs) / (len(three_NPs) + len(three_null))
#
#     zero_total = len(zero_NPs) + len(zero_null)
#     one_total = len(one_NPs) + len(one_null)
#     two_total = len(two_NPs) + len(two_null)
#     three_total= len(three_NPs) + len(three_null)
#
#     for arg in arg_list:  # словарь по падежам
#         case = arg[0][2:5]
#         if case not in case_dict.keys():
#             case_dict[case] = [0, 0]
#         if arg[1] == 'Ø':
#             case_dict[case][0] += 1
#         else:
#             case_dict[case][1] += 1
#
#     for key in case_dict.keys():
#         case_dict[key] = [case_dict[key][0], case_dict[key][1], case_dict[key][1] / (case_dict[key][0] + case_dict[key][1])]
#
#
#     return zero_density, zero_total, one_density, one_total, two_density, two_total, three_density, three_total,\
#            len(zero_null), len(zero_NPs), len(one_null), len(one_NPs), len(two_null), len(two_NPs), len(three_null),\
#            len(three_NPs), case_dict
#
# def anaphors_list(name):
#     anaph_list = []
#     NP_list = []
#
#     text = open_text(name)
#     transcription = [word.split('\t') for word in findall(r'Transcription:(.*)', text)]
#     indexation = [word.split('\t') for word in findall(r'Indexation:(.*)', text)]
#
#     for i in range(len(indexation)):
#         for j in range(len(indexation[i])):
#
#             anaphor = sub(r'\(.\)', '', indexation[i][j])  # чтобы убрать индексы
#
#             if 'pred' not in anaphor and anaphor.islower():  # для анафоров
#                 l, m = i, j-1
#                 WD = 0
#                 ND = 0
#                 wd_ok = False
#                 nd_ok = False
#                 while l != -1 and not wd_ok:
#                     while m != -1 and not wd_ok:
#
#                         antecedent = sub(r'\(.\)', '', indexation[l][m])  # чтобы убрать индексы
#
#                         if 'pred' in antecedent:
#                             WD += 1
#                             if not nd_ok:
#                                 ND += 1
#                         elif anaphor == antecedent:
#                             nd_ok = True
#                         elif anaphor.upper() == antecedent:
#                             #print(indexation[i][j], i, j, indexation[l][m], l, m, WD, ND)
#                             anaph_list.append([transcription[i][j], anaphor, WD, ND])
#                             wd_ok = True
#                         m -= 1
#                     l -= 1
#                     m = len(indexation[l])-1
#
#             elif 'pred' not in anaphor and anaphor.isupper():  # для ИГ
#                 l, m = i, j - 1
#                 WD = 0
#                 ND = 0
#                 wd_ok = False
#                 nd_ok = False
#                 while l != -1 and not wd_ok:
#                     while m != -1 and not wd_ok:
#
#                         antecedent = sub(r'\(.\)', '', indexation[l][m])  # чтобы убрать индексы
#
#                         if 'pred' in antecedent:
#                             WD += 1
#                             if not nd_ok:
#                                 ND += 1
#                         elif anaphor.lower() == antecedent:
#                             nd_ok = True
#                         elif anaphor == antecedent:
#                             # print(indexation[i][j], i, j, indexation[l][m], l, m, WD, ND)
#                             NP_list.append([transcription[i][j], anaphor, WD, ND])
#                             wd_ok = True
#                         m -= 1
#                     l -= 1
#                     m = len(indexation[l]) - 1
#
#     for i in range(len(anaph_list)):  # убрать предикацию для нулей
#         if anaph_list[i][0] == 'Ø':
#             anaph_list[i] = ['Ø', anaph_list[i][1], anaph_list[i][2]-1, anaph_list[i][3]-1]
#
#     return anaph_list, NP_list
#
# def pred_count(name):
#     text = open_text(name)
#     note = [word.split('\t') for word in findall(r'Note:(.*)', text)]
#     indexation = [word.split('\t') for word in findall(r'Indexation:(.*)', text)]
#
#     pred_tot = 0
#     pred_fin = 0
#
#     for i in range(len(indexation)):
#         for j in range(len(indexation[i])):
#             if 'pred' in indexation[i][j]:
#                 pred_tot += 1
#                 if note[i][j] == 'Fin':
#                     pred_fin += 1
#     return pred_tot, pred_fin
#
# def anaphoric_distance(name):
#     anaph_list, NP_list = anaphors_list(name)
#     null_WD, prox_WD, med_WD, dist_WD, self_WD = 0, 0, 0, 0, 0
#     null_ND, prox_ND, med_ND, dist_ND, self_ND = 0, 0, 0, 0, 0
#     null_total, prox_total, med_total, dist_total, self_total = 0, 0, 0, 0, 0
#
#     np_WD, np_ND, np_total = 0, 0, 0
#
#     for anaphor in anaph_list:
#         if anaphor[0] == 'Ø':
#             null_total += 1
#             null_WD += anaphor[2]
#             null_ND += anaphor[3]
#         elif anaphor[0].startswith('mi'):
#             prox_total += 1
#             prox_WD += anaphor[2]
#             prox_ND += anaphor[3]
#         elif anaphor[0].startswith('ha'):  # могут быть префиксы с ha
#             med_total += 1
#             med_WD += anaphor[2]
#             med_ND += anaphor[3]
#         elif anaphor[0].startswith('ti'):
#             dist_total += 1
#             dist_WD += anaphor[2]
#             dist_ND += anaphor[3]
#         elif anaphor[0].startswith('ǯ') or anaphor[0].startswith('j'):
#             self_total += 1
#             self_WD += anaphor[2]
#             self_ND += anaphor[3]
#
#
#     try:
#         null_WD = null_WD / null_total
#         null_ND = null_ND / null_total
#     except:
#         pass
#
#     try:
#         prox_WD = prox_WD / prox_total
#         prox_ND = prox_ND / prox_total
#     except:
#         pass
#
#     try:
#         med_WD = med_WD / med_total
#         med_ND = med_ND / med_total
#     except:
#         pass
#
#     try:
#         dist_WD = dist_WD / dist_total
#         dist_ND = dist_ND / dist_total
#     except:
#         pass
#
#     try:
#         self_WD = self_WD / self_total
#         self_ND = self_ND / self_total
#     except:
#         pass
#
#
#     for np in NP_list:
#         np_total += 1
#         np_WD += np[2]
#         np_ND += np[3]
#
#     try:
#         np_WD = np_WD / np_total
#         np_ND = np_ND / np_total
#     except:
#         pass
#
#     return null_WD, null_ND, null_total,\
#            prox_WD, prox_ND, prox_total,\
#            med_WD, med_ND, med_total,\
#            dist_WD, dist_ND, dist_total,\
#            self_WD, self_ND, self_total, \
#            np_WD, np_ND, np_total
#
# def main():
#     texts = all_texts()
#     with open('results.tsv', 'w', encoding='UTF-8') as f:
#         f.write('TEXT_NAME\tFin\tNFin\tTotal_pred\tRD\tTotal_nulls\tTotal_NPs\tZERO_argument_density\tZERO_nulls\tZERO_NPs\tTotal\t'
#                 'ONE_argument_density\tONE_nulls\tONE_NPs\tTotal\t' +
#                 'TWO_argument_density\tTWO_nulls\tTWO_NPs\tTotal\t' +
#                 'THREE_argument_density\tTHREE_nulls\tTHREE_NPs\tTotal\t' +
#                 'NP_WD\tNP_ND\tNP_Total\t' +
#                 'NULL_WD\tNULL_ND\tNULL_Total\t' +
#                 'PROX_WD\tPROX_ND\tPROX_Total\t' +
#                 'MED_WD\tMED_ND\tMED_Total\t' +
#                 'DIST_WD\tDIST_ND\tDIST_Total\t' +
#                 'SELF_WD\tSELF_ND\tSELF_Total\t' +
#                 'ABS_nulls\tABS_NPs\tABS_RD\t' +
#                 'ERG_nulls\tERG_NPs\tERG_RD\t' +
#                 'DAT_nulls\tDAT_NPs\tDAT_RD\t' +
#                 'LOC_nulls\tLOC_NPs\tLOC_RD\t' +
#                 'FIN_nulls\tFIN_NPs\tFIN_RD\t' +
#                 'NFIN_nulls\tNFIN_NPs\tNFIN_RD\n')
#     for name in texts:
#
#         rd, nuls, NPs = referential_density(name)
#         zero_density, zero_total, one_density, one_total, \
#         two_density, two_total, three_density, three_total,\
#         zero_null, zero_NPs,\
#         one_null, one_NPs,\
#         two_null, two_NPs,\
#         three_null, three_NPs, case_dict = omission_stat(name)
#
#         null_WD, null_ND, null_total, \
#         prox_WD, prox_ND, prox_total, \
#         med_WD, med_ND, med_total, \
#         dist_WD, dist_ND, dist_total, \
#         self_WD, self_ND, self_total, \
#         np_WD, np_ND, np_total = anaphoric_distance(name)
#
#         pred_tot, pred_fin = pred_count(name)
#         pred_nfin = pred_tot - pred_fin
#
#         fin_nulls, fin_NPs, fin_RD, nfin_nulls, nfin_NPs, nfin_RD = fin_referential_density(name)
#
#         with open('results.tsv', 'a', encoding='UTF-8') as f:
#             f.write(name + '\t')
#             f.write(str(pred_fin) + '\t' + str(pred_nfin) + '\t' + str(pred_tot) + '\t')
#             f.write(str(rd) + '\t' + str(nuls) + '\t' + str(NPs) + '\t')
#
#             f.write(str(zero_density) + '\t' + str(zero_null) + '\t' + str(zero_NPs) + '\t' + str(zero_total) + '\t' +
#                     str(one_density) + '\t' + str(one_null) + '\t' + str(one_NPs) + '\t' + str(one_total) + '\t' +
#                     str(two_density) + '\t' + str(two_null) + '\t' + str(two_NPs) + '\t' + str(two_total) + '\t' +
#                     str(three_density) + '\t' + str(three_null) + '\t' + str(three_NPs) +  '\t' + str(three_total) +
#                     '\t')
#
#             f.write(str(np_WD) + '\t' + str(np_ND) + '\t' + str(np_total) + '\t' +
#                     str(null_WD) + '\t' + str(null_ND) + '\t' + str(null_total) + '\t' +
#                     str(prox_WD) + '\t' + str(prox_ND) + '\t' + str(prox_total) + '\t' +
#                     str(med_WD) + '\t' + str(med_ND) + '\t' + str(med_total) + '\t' +
#                     str(dist_WD) + '\t' + str(dist_ND) + '\t' + str(dist_total) + '\t' +
#                     str(self_WD) + '\t' + str(self_ND) + '\t' + str(self_total) + '\t')
#
#             f.write(str(case_dict['ABS'][0]) + '\t' + str(case_dict['ABS'][1]) + '\t' + str(case_dict['ABS'][2]) + '\t' +
#                     str(case_dict['ERG'][0]) + '\t' + str(case_dict['ERG'][1]) + '\t' + str(case_dict['ERG'][2]) + '\t' +
#                     str(case_dict['DAT'][0]) + '\t' + str(case_dict['DAT'][1]) + '\t' + str(case_dict['DAT'][2]) + '\t' +
#                     str(case_dict['LOC'][0]) + '\t' + str(case_dict['LOC'][1]) + '\t' + str(case_dict['LOC'][2]) + '\t')
#
#             f.write(str(fin_nulls) + '\t' + str(fin_NPs) + '\t' + str(fin_RD) + '\t' +
#                     str(nfin_nulls) + '\t' + str(nfin_NPs) + '\t' + str(nfin_RD) + '\n')
#
#
# '''
#         print('Referencial density: ' + str(rd) +
#               '\nTotal nulls: ' + str(nuls) +
#               '\nTotal NPs: ' + str(NPs))
#
#         print('ZERO argument density: ' + str(zero_density) + ' Total: ' + str(zero_total) + '\n' +
#               'ONE argument density: ' + str(one_density) + ' Total: ' + str(one_total) + '\n' +
#               'TWO argument density: ' + str(two_density) + ' Total: ' + str(two_total) + '\n' +
#               'THREE argument density: ' + str(three_density) + ' Total: ' + str(three_total))
#
#         print('\nAnaphoric distance: ')
# '''
#
#
# '''
#         print('\nNULL\n' + 'WD: ' + str(null_WD) + ' ND: ' + str(null_ND) + ' Total: ' + str(null_total) +
#               '\n\nPROX\n' + 'WD: ' + str(prox_WD) + ' ND: ' + str(prox_ND) + ' Total: ' + str(prox_total) +
#               '\n\nMED\n' + 'WD: ' + str(med_WD) + ' ND: ' + str(med_ND) + ' Total: ' + str(med_total) +
#               '\n\nDIST\n' + 'WD: ' + str(dist_WD) + ' ND: ' + str(dist_ND) + ' Total: ' + str(dist_total) +
#               '\n\nSELF\n' + 'WD: ' + str(self_WD) + ' ND: ' + str(self_ND) + ' Total: ' + str(self_total))
#         #anaphoric_distance(name)
# '''
# # if __name__ == '__main__':
# #     rd_w()
# #     #main()