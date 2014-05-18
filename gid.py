# coding: utf-8
# py3
__author__ = 'odmen'
import glob
import os
import sys
import re
import hashlib
import csv
import shutil
import string
import random
from functools import partial

for arg in sys.argv:
    # перебираем аргументы, переданные скрипту
    currindex = sys.argv.index(arg)
    # запоминаем индекс текущего выбранного аргумента
    if arg == "-p":
        # если текущий элемент - "-p"
        work_dir = sys.argv[currindex + 1]
# то запоминаем текст следующего (по индексу) элемента как "рабочий каталог"

def md5file(filename):
# эта функция считает md5 сумму файла
# на вход принимает полный путь до файла
# возвращает строку
# код фунции сопирован из интернета, как работает пока не смотрел
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
# функция берет последовательность букв и цифр
# берет из этой последовательности случайные символы
# последовательность длинной 6 символов
# возвращает эту последовательность
    return ''.join(random.choice(chars) for _ in range(size))

def create_folder(where_path):
# функция герерирует имя папки для уникальных файлов,
# проверяя нет ли случайно такой папки уже
    interest_folder = where_path + "ufiles_"+id_generator()
# составляем имя папки для уникальных файлов
    if not os.path.exists(interest_folder):
# проверяем нет ли такой папки в рабочем каталоге
        os.makedirs(interest_folder)
# если нету создаем папку
        return interest_folder
# и возвращаем имя
    else:
        create_folder()
# если такая папка уже есть запускаем функцию заново

hash_names = {}
# будет хранить соответствия хеша файла перечню имен одинаковых файлов
img_regex = re.compile("\.(jpg|jpeg|png)$")
# регулярка выборки файлов определенного разрешения
out_folder = create_folder(work_dir)
# получаем имя папки для файлов результата
in_csv = work_dir + "in.csv"
# составляем из переданного скрипту рабочего каталога путь до исходного файла CSV
out_csv = out_folder + "/out.csv"
# аналогично для файла результата
os.chdir(work_dir)
# переходим в рабочий каталог
for filename in glob.glob("*.*"):
# перебираем имена файлов в этом каталоге
    if img_regex.search(filename):
# если текущий выбранный файл нам подходит по регулярке
        filemd5 = md5file(work_dir + filename)
# передаем путь до файла в функцию вычисления md5
        if filemd5 in hash_names:
# если такой хеш уже есть в словаре
            hash_names[filemd5].append(filename)
# добавляем имя файла в список к соотв. хешу
        else:
# если нет, то обновляем словарь, добавив имя текущего выбранного файла
            hash_names.update({filemd5: [filename]})

with open(in_csv, "r") as infile, open(out_csv, "w") as outfile:
# открываем оба CSV. один для чтения, второй для записи
    r = csv.DictReader(infile, delimiter=';')
# поможет удобно читать csv файл. Задаем разделитель полей
    w = csv.DictWriter(outfile, r.fieldnames, delimiter=';')
# поможет удобно записать csv файл. Задаем разделитель полей и заголовки
    w.writeheader()
# пишем заголовки таблицы
    for row in r:
# берем строку из файла
        row_img_list = row["image : Image"].split(',')
# разбиваем строку по запятой
        for img_name in row_img_list:
# обходим все элементы разбитой строки
            for fhash in hash_names:
# для каждого элемента обходим весь словарь с хешами
                if img_name.strip() in hash_names[fhash]:
# если текущее имя изображения найдено в словаре текущего выбранного хеша
                    mtch_img_indx = row_img_list.index(img_name)
# узнаем индекс этого имени в текущей строке
                    row_img_list[mtch_img_indx] = hash_names[fhash][0]
# меняем элемент с таким индексом на первый элемент списка имен файлов по текущему хешу
                    shutil.copy2(work_dir + hash_names[fhash][0], out_folder + '/' + hash_names[fhash][0])
# копируем файл с таким именем в отдельный каталог для загрузки в СУ
        row["image : Image"] = ','.join(row_img_list)
# собираем обратно строку, слепив по запятым и меняем всю колонку в текущей строке на новую
        w.writerow(row)
# пишем в файл построчно