from toolbox2csv import op, wr

def txt2list():
    txt = op('Lak_1.txt')
    lines_list = txt.split('\n')
    new_list = [[line.split(';')[0].replace(' ', '\t'), line.split(';')[1]] for line in lines_list]
    return new_list

def make_lines(new_list):
    for transcription, translation in new_list:
        print(transcription, translation)
        line = 'Transcription:\t' + transcription + '\nNote:\nIndexation:\nTranslation:\t' + translation + '\n\n'
        wr('Lak_1.csv', line)

if __name__ == '__main__':
    make_lines(txt2list())