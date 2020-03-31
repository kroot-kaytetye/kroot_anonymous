"""
NAME: produce_segmental_configurations_list.py
CREATED: 22-MAR-20
LAST EDIT: 22-MAR-20
CREATOR: Author
EMAIL: 62926253+kroot-kaytetye@users.noreply.github.com
PROJECT: kroot
SUMMARY: Receives a list of syllabified Kaytetye lexemes, and outputs all possible consonant and vowel configurations
         for each phonotactic position (syllable, nucleus, coda). This output (phon_configs.txt) is required for
        produce_info_theory_docs.py. Uses get_configurations.py, which was created to allow for easy testing.
"""
import sys
import re
import os
from pathlib import Path
from get_configurations import get_configurations

syl_list = open(sys.argv[1], 'r', encoding="utf-8").read().splitlines()
configs = get_configurations(syl_list)
with open(os.path.dirname(sys.argv[1]) + "\\phon_configs.txt", 'w', encoding="utf-8") as f:
    f.writelines("\n".join(configs))
