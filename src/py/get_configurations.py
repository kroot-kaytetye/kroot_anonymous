"""
NAME: get_configurations.py
CREATED: 25-MAR-20
AUTHOR: Author (62926253+kroot-kaytetye@users.noreply.github.com)
DETAILS: main function for produce_segmental_configurations_list.py, isolated to allow for testing of function.
"""
import re

def get_configurations(syl_list):
    # create flat syllable list
    syl_list = [line.split(".") for line in syl_list]
    syl_list = [item for sublist in syl_list for item in sublist]

    # create a vector of split syllables using the syllable nucleus as a delimiter
    vowel_regex = "[ɐəiu:]+"
    split_list = []
    for syl in syl_list:
        # throw error if there are two vowel matches in the same syllable
        if len(re.findall(vowel_regex, syl)) > 1:
            print(syl)
            raise RuntimeError
        cons_split = re.split(vowel_regex, syl)
        for cs in cons_split:
            if cs == '':
                split_list.append("0") # treat no consonant as 0
            else:
                split_list.append(cs)
        # add the nucleus
        split_list.append(re.compile(vowel_regex).findall(syl)[0])
    uniq_seqs = set(split_list)
    return uniq_seqs