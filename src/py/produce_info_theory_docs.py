"""
NAME: produce_info_theory_docs.py
CREATED: 16-JAN-20
LAST EDIT: 23-MAR-20
CREATOR: Author
EMAIL:  62926253+kroot-kaytetye@users.noreply.github.com
PROJECT: Orthography to Surprisals
SUMMARY: Retrieves the directories of  syllabified roots and a set of all possible segmental configurations as
command line arguments, and outputs various documents. This script relies on two .py documents:
lex_io.py, and info_theory_functions.py
"""
import sys
import lex_io
import info_theory_functions as itf
import os
from pathlib import Path

syl_lex_dir = sys.argv[1]
seg_config_dir = sys.argv[2]
# create output dir for python analysis documents if it does not exist
out_dir = os.path.dirname(syl_lex_dir)

syl_lex = lex_io.read_lexicon_file(syl_lex_dir)
seg_configs = lex_io.read_lexicon_file(seg_config_dir)

# make new phonotactic fqs
freq_dict = itf.get_frequency_of_each_config_in_word_position(syl_lex, seg_configs)
# save document
lex_io.write_dict_to_csv(freq_dict, "phonotactic_fqs", out_dir)
# calculate entropy for syllable positions
phon_ent = itf.get_phontactic_entropies(freq_dict)
lex_io.write_dict_to_csv(phon_ent, "phonological_entropy", out_dir)

# get positional surprisals
phonol_surprisals = itf.get_phonotactic_surprisals(freq_dict)
# save phonological surprisals
lex_io.write_dict_to_csv(phonol_surprisals, "positional_surprisals", out_dir)

# get surprisals of lexicon
lex_sur = itf.get_surprisals_of_lexicon(syl_lex, phonol_surprisals)
# save lexicon surprisals
lex_io.write_dict_to_csv(lex_sur, "lexical_surprisals", out_dir)