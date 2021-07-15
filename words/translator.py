import os
import time

from googletrans import Translator


def translate(text_to_translate):
    translator = Translator()
    translation = translator.translate(text_to_translate, dest='ru')
    return translation.text


if __name__ == '__main__':
    with open(os.path.realpath('30k words.txt'), 'r', encoding='utf8') as f:
        with open(os.path.realpath('D://translated.txt'), 'a', encoding='utf8') as f2:
            for line in f.readlines():
                line = line[:len(line)-1]
                translated_word = translate(line)
                line_to_write = f'{line} {translated_word}\n'
                print(line_to_write)
                f2.write(line_to_write)
                time.sleep(0.1)
                f2.flush()
