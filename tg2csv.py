import re
from toolbox2csv import op, wr


def tg2list(txt):
    transcription = re.findall(r'text = "(.+)"', re.findall(r'name = "Mary"([\W\w]+)name = "John"', txt)[0])
    translation = re.findall(r'text = "(.+)"',re.findall(r'name = "John"([\W\w]+)', txt)[0])
    return translation, transcription

def make_line(translation, transcription, file_name):
    if len(transcription) != len(translation):
        return
    for i in range(len(transcription)):
        line = 'Transcription:\t' + transcription[i].replace(' ', '\t') + '\nNote:\nIndexation:\nTranslation:\t' + translation[i] + '\n\n'
        wr(file_name, line)

if __name__ == '__main__':
    txt = op('Mehweb_2.TextGrid')

    translation, transcription = tg2list(txt)
    make_line(translation, transcription, 'Mehweb_2.csv')
    txt = op('Mehweb_3.TextGrid')

    translation, transcription = tg2list(txt)
    make_line(translation, transcription, 'Mehweb_3.csv')


