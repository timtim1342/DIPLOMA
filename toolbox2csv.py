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

def search_sentences(txt):
    sentenses = txt.split('\\ref')
    # sentenses = re.findall('\\\\ref([\s\S]*)', txt)
    print(sentenses[0])
    print(sentenses[1])
    print(sentenses[2])





def op(file_name):
    with open(file_name + '.txt', encoding='utf-8') as f:
        txt = f.read()
    return txt
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
