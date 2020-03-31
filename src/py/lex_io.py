"""
NAME: lex_io.py
CREATED: 10-JAN-20
LAST EDIT: 23-MAR-20
CREATOR: Author
EMAIL:  62926253+kroot-kaytetye@users.noreply.github.com
PROJECT: kroot
SUMMARY: Contains function relating to the reading and writing of documents relevant to the information theory analysis
        of Kaytetye roots.
FUNCTIONS:
    read_lexicon_file
    read_csv
    write_dict_to_csv
"""
from pathlib import Path
import os
import csv


def read_lexicon_file(directory):
    with open(directory, encoding="utf-8") as f:
        lex_array = f.readlines()
        for i in range(len(lex_array)):
            lex_array[i] = lex_array[i].strip('\n')
    return lex_array


def read_csv(dir):
    file = open(dir, encoding="utf-8-sig")
    output = csv.DictReader(file)
    return list(output)


def write_dict_to_csv(out_dict, output_name, out_dir):
    with open(out_dir + "\\" + output_name + ".csv", 'w', encoding="utf-8", newline='') as output:
        w = csv.DictWriter(output, out_dict[0].keys())
        w.writeheader()
        w.writerows(out_dict)
