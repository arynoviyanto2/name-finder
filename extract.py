# Copyright 2020 Ary Noviyanto

import sys
import ast
import csv
from operator import itemgetter
from itertools import groupby
from difflib import SequenceMatcher
# import time


# tic = time.perf_counter()
invoice_file_path = sys.argv[1]
supplier_names_file_path = sys.argv[2]
min_confident_score = float(sys.argv[3])

invoice = open(invoice_file_path, 'r')
supplier_names = open(supplier_names_file_path, 'r')

# load words from an invoice
words = []
for line in invoice:
    line_dict = ast.literal_eval(line.rstrip())
    words.append(line_dict)


# extract potential company names
sort_key = itemgetter('page_id', 'line_id', 'cspan_id')
potential_company_names = set()  # ensure no duplication

words.sort(key=sort_key)

for key, values in groupby(words, key=sort_key):
    items = [{'word': v['word'], 'pos_id': v['pos_id']} for v in values]
    items.sort(key=itemgetter('pos_id'))

    # remove spaces and convert to lower case for matching accuracy and matching speed
    potential_company_names.add(' '.join([w['word'].strip().lower() for w in items]))


# convert to list of words to speed up the matching
list_of_potential_company_names = [name.split(' ') for name in potential_company_names]


# similarity score generator
def calculate_score(_supplier_name, _potential_company_names):
    for name in _potential_company_names:
        yield SequenceMatcher(None, name, _supplier_name, True).quick_ratio()


# iterate for each supplier name
next(supplier_names)  # skip first line
reader = csv.reader(supplier_names, delimiter=',')
for supplier in reader:
    supplier_name = supplier[1].strip().lower().split(' ')
    score_generator = calculate_score(supplier_name, list_of_potential_company_names)
    winner_score = max(score_generator)
    if winner_score >= min_confident_score:
        print(f"{supplier[0]} {' '.join(supplier_name)}, confident score {winner_score}")

# toc = time.perf_counter()
# print(f"Finished in {toc - tic:0.4f} s")

invoice.close()
supplier_names.close()
