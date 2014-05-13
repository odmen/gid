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
from functools import partial

for arg in sys.argv:
  currindex = sys.argv.index(arg)
  if arg == "-p":
    work_dir = sys.argv[currindex+1]

# считает md5 сумму файла
# на вход принимает полный путь до файла
def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

hash_names = {}
img_regex = re.compile("\.(jpg|jpeg|png)$")
in_csv = work_dir+"in.csv"
out_csv = work_dir+"out.csv"

os.chdir(work_dir)
for filename in glob.glob("*.*"):
  if img_regex.search(filename):
    filemd5 = md5sum(work_dir+filename)
    # print(filemd5+" "+filename)
    if filemd5 in hash_names:
      hash_names[filemd5].append(filename)
    else:
      hash_names.update({filemd5:[filename]})

with open(in_csv, "r") as infile, open(out_csv, "w") as outfile:
    r = csv.DictReader(infile, delimiter=';')
    w = csv.DictWriter(outfile, r.fieldnames, delimiter=';')
    w.writeheader()
    for row in r:
# обходим каждую строку
      for fhash in hash_names:
# обходим элементы словаря { 'хеш' : [список, имен, файлов] }
        for file_img in hash_names[fhash]:
# берем каждый список файлов по текушему выбранному хешу
          row_img_list = row["image : Image"].split(',')
# разбиваем колонку с изображениями по запятой
          if file_img in row_img_list:
# если текущее имя файла найдено в текущем имени файла из csv
            mtch_img_indx = row_img_list.index(file_img)
# берем индекс текущего имени в колонке
            row_img_list[mtch_img_indx] = hash_names[fhash][0]
# меняем элемент с таким индексом на первый элемент списка имен файлов по текущему хешу
            shutil.copy2(work_dir+hash_names[fhash][0], work_dir+'fd/'+hash_names[fhash][0])
# копируем файл с таким именем в отдельный каталог для загрузки в СУ
      row["image : Image"] = ','.join(row_img_list)
# собираем обратно строку, слепив по запятым и меняем всю колонку в текущей строке на новую
      w.writerow(row)
# пишем в файл построчно