# coding: utf-8
# py3
__author__ = 'odmen'
import glob, os, sys, re, hashlib, csv
from functools import partial

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
in_csv = "/tmp/test.csv"
out_csv = "/tmp/res_test.csv"

for arg in sys.argv:
  currindex = sys.argv.index(arg)
  if arg == "-p":
    img_dir = sys.argv[currindex+1]

os.chdir(img_dir)
for filename in glob.glob("*.*"):
  if img_regex.search(filename):
    filemd5 = md5sum(img_dir+filename)
    # print(filemd5+" "+filename)
    if filemd5 in hash_names:
      hash_names[filemd5].append(filename)
    else:
      hash_names.update({filemd5:[filename]})

with open(in_csv, "r") as infile, open(out_csv, "w") as outfile:
    r = csv.DictReader(infile, delimiter=';')
    w = csv.DictWriter(outfile, r.fieldnames, delimiter=';')
    w.writeheader()
# обходим каждую строку
    for row in r:
# обходим элементы словаря "хеш : список имен файлов"
      for fhash in hash_names:
# берем каждый список файлов по текушему выбранному хешу
        for file_img in hash_names[fhash]:
# разбиваем колонку с изображениями по запятой
          row_img_list = row["image : Image"].split(',')
# если текущее имя файла найдено в текущем имени файла из csv
          if file_img in row_img_list:
# берем индекс текущего имени в колонке
            mtch_img_indx = row_img_list.index(file_img)
# меняем элемент с таким индексом на первый элемент списка имен файлов по текущему хешу
            row_img_list[mtch_img_indx] = hash_names[fhash][0]
# собираем обратно строку, слепив по запятым и меняем всю колонку в текущей строке на новую
      row["image : Image"] = ','.join(row_img_list)
# пишем в файл построчно
      w.writerow(row)