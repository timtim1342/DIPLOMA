import re

class ParseError(Exception):
    pass

class Sentence:
    """"""
    def __init__(self, translation, morphs, glosses, order_id):
        """"""
        self.translation = translation
        self.morphs = morphs
        self.glosses = glosses
        self.order_id = order_id

    def merge_glosses_morphs(self):
        """"""
        if len(self.glosses) == len(self.morphs):  # остается проблема склеившихся глосс типа "basket(r)"
            morphs_merged = ' '.join(self.morphs).replace('- ', '-').replace(' -', '-').split()
            glosses_merged = ' '.join(self.glosses).replace('- ', '-').replace(' -', '-').split()

            return morphs_merged, glosses_merged

        else:
            raise ParseError('The number of morphs and glosses is different')

    def make_line(self):
        """"""
        line = self.order_id
        try:
            morphs_merged, glosses_merged = self.merge_glosses_morphs()
            line += '\n'
            line += '\t'.join(morphs_merged) + '\n'
            line += '\t'.join(glosses_merged) + '\n'

        except ParseError:
            line += ' ParseError\n'
            line += '\t'.join(' '.join(self.morphs).replace('- ', '-').replace(' -', '-').split()) + '\n'
            line += '\t'.join(' '.join(self.glosses).replace('- ', '-').replace(' -', '-').split()) + '\n'

        line += self.translation + '\n' + '\n'
        return line

def op(file_name):
    with open(file_name, encoding='utf-8') as f:
        txt = f.read()
    return txt

def wr(file_name, line):
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write(line)

def main(txt):
    texts = txt.split('\\id')
    for text in texts:
        refs = text.split('\\ref')
        info, sentense_chunks = refs[0], refs[1:]
        file_name = info.split('\n')[0].replace('.', '_')
        with open(file_name + '.tsv', 'w', encoding='utf-8') as f:
            pass

        for chunk in sentense_chunks:
            try:
                translation = re.findall('\\\\ft(.*)', chunk)[0]
                if len(translation) == 0:
                    translation = 'NO TRANSLATION'
            except:
                translation = 'NO TRANSLATION'
            order_id = str(re.findall('\.(\d\d\d)', chunk)[0])
            morphs = re.findall('\\\\mb(.*)', chunk)[0].split()
            glosses = re.findall('\\\\ge(.*)', chunk.replace(', ', ','))[
                0].split()  # replace, для корней типа "do, make"

            current_sentence = Sentence(translation, morphs, glosses, order_id)
            wr(file_name + '.tsv', current_sentence.make_line())



if __name__ == '__main__':
    txt = op("data/Hinuq_PS.txt")
    main(txt)
