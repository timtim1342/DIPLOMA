import re


class Sentence:
    """"""
    def __init__(self, translation, morphs, glosses, order_id):
        """"""
        self.translation = translation
        self.morphs = morphs
        self.glosses = glosses
        self.order_id = order_id
# ...

def op(file_name):
    with open(file_name + '.txt', encoding='utf-8') as f:
        txt = f.read()
    return txt

def search_sentences(txt):
    refs = txt.split('\\ref')
    info, sentense_chunks = refs[0], refs[1:]
    #print(sentense_chunks[0])
    for chunk in sentense_chunks:
        translation = re.findall('\\\\ft(.*)', chunk)
        order_id = re.findall('\.(\d\d\d)', chunk)
        morphs = re.findall('\\\\mb(.*)', chunk)[0].split()
        glosses = re.findall('\\\\ge(.*)', chunk.replace(', ', ','))[0].split()  # replace, для корней типа "do, make"
        #print(translation)
        #print(order_id)
        #print(morphs)
        #print(glosses)
        morph_gloss_merger(glosses, morphs)



def morph_gloss_merger(glosses, morphs):
    if len(glosses) == len(morphs):  # остается проблема склеившихся глосс типа "basket(r)"
        prev_morph_type = 'root'

        morph_word = ''
        gloss_word = ''

        morphs_merged = []
        glosses_merged = []

        for i in range(len(morphs)):
            current_morph = morphs[i]
            current_gloss = glosses[i]
            symbs = tuple(['-', '='])

            if current_morph.startswith(symbs):
                current_morph_type = 'post'
            elif current_morph.endswith(symbs):
                current_morph_type = 'pre'
            else:
                current_morph_type = 'root'

            if prev_morph_type == 'root' and current_morph_type == 'root' \
                    or prev_morph_type == 'post' and current_morph_type == 'root' \
                    or prev_morph_type == 'root' and current_morph_type == 'post' \
                    or prev_morph_type == 'root' and current_morph_type == 'root' \
                    or prev_morph_type == 'post' and current_morph_type == 'pre':
                morphs_merged.append(morph_word)
                glosses_merged.append(gloss_word)
                print(morph_word)
                print(gloss_word)
                morph_word = ''
                gloss_word = ''
            else:

                morph_word += current_morph
                gloss_word += current_gloss

            prev_morph_type = current_morph_type



    else:
        print(morphs, '\n', glosses)
        print(len(morphs), len(glosses))
        print()


#
# def translation(txt):
#     txt = txt.replace('\\rf', '')  # remove. only for Bezhta
#     tr = re.findall('\\\\ft(.*)', txt)
#     print(tr)
#     return tr
#
# def wr(s, name):
#     with open(name + 'T.txt', 'a') as f:
#         f.write(s)
#
# def numb(s):
#     if '\\ref' in s:
#         try:
#             n = s[len(s)-4: len(s)].replace('\n', '').replace("'", '').replace("#", '')
#             int(n)
#         except:
#             n = 0
#         return '(' + str(int(n)) + ')'
#
#     else:
#         return ''
#
# def main(name):
#     txt = op(name)
#     tr = translation(txt)
#     with open(name + 'T.txt', 'w', encoding='utf-8') as f:
#         pass
#     n = ''
#     for s in tr:
#         s = n + s + '\n'
#         n = numb(s)
#         wr(s.replace('\\rt', ''), name)

if __name__ == '__main__':
    # main("data/Khwarshi_PS")
    txt = op("data/Khwarshi_PS")
    search_sentences(txt)
