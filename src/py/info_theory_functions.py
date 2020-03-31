"""
NAME: info_theory_functions.py
CREATED: 16-JAN-20
LAST EDIT: 23-MAR-20
CREATOR: Author
EMAIL:  62926253+kroot-kaytetye@users.noreply.github.com
PROJECT: kroot
SUMMARY: Contains functions relevant to the information theoretic analysis of Kaytetye syllabified roots.
FUNCTIONS:
    _update_dict
    _get_max_syl_count
    _get_frequency_of_segment_in_list
    _split_syllable_into_phonotactic_positions
    _get_frequency_of_configurations_in_syllable
    _get_phonotactic_entropy
    _get_phonotactic_surprisal
    _get_surprisal_of_syllable
    get_frequency_of_each_config_in_word_position
    get_phontactic_entropies
    get_surprisals_of_lexicon
    get_phonotactic_surprisals
"""
from math import log
import re


##########################################
# Private Functions
##########################################
def _update_dict(dict_1, dict_2):
    """
    Combines the two provided Dictionaries
    """
    new_dict = {}
    for key in dict_1.keys():
        new_dict[key] = dict_1[key] + dict_2[key]
    return new_dict


def _get_max_syl_count(lexicon):
    """
    Counts the length of all words in the input syllabified lexicon, and returns the longest word (in terms of syllables)
    in the lexicon.
    """
    max_syl = 0
    for lex in lexicon:
        if len(lex.split(".")) > max_syl:
            max_syl = len(lex.split("."))
    return max_syl


def _get_frequency_of_segment_in_list(seg, seg_list):
    """
    Counts the frequency of a given segment or token in a list of segments/tokens.
    """
    return seg_list.count(seg)


def _split_syllable_into_phonotactic_positions(syllable):
    """
    Takes an input syllable, and outputs a three-member list. The first member is the onset. The second member is the
    nucleus. The third member is the coda.
    """
    # alternative splitting of syllable into onset and coda, rather than using a syllabic template
    vowel_regex = "[ɐəiu:]"
    p = re.compile(vowel_regex)
    vowel_pos = []
    for match in p.finditer(syllable):
        vowel_pos.append(match.start())

    assert (len(vowel_pos) < 3), "There must only be one or two vowel phonemes in a single " \
                                 "syllable. "
    assert (len(vowel_pos) > 0), "There must only be one or two vowel phonemes in a single " \
                                 "syllable. "
    if len(vowel_pos) == 1:
        cut_points = [vowel_pos[0], vowel_pos[0] + 1]
    else:
        cut_points = [vowel_pos[0], vowel_pos[1] + 1]
    # Split into positions
    onset = syllable[0:cut_points[0]]
    nucleus = syllable[cut_points[0]:cut_points[1]]
    coda = syllable[cut_points[1]:len(syllable)]

    if len(onset) == 0:
        onset = "0"
    if len(coda) == 0:
        coda = "0"
    return [onset, nucleus, coda]


def _get_frequency_of_configurations_in_syllable(lexicon, seg_list, syllable_number, get_final_syllables):
    """
    Gets the frequency of each segment in seg_list for each phonotactic position in the syllable number for each word
    in the lexicon. If syllable_number == 1, the frequency of all the segments in seg_list are retrieved for
    the onset, nucleus, and coda of the first syllable in every lexeme.
    if get_final_syllables is set to true, this ovverrides the syllable_number variable and simply pulls the final
    syllable in each word. The resulting dictionary assigns the onset of these syllables to the corresponding number
    (e.g. if a word is three syllables long, onset_2 will receive the the onset. This results in a dictionary which does
    not correspond to a single row.
    """

    if get_final_syllables is False:

        output_dict = {'syllable': [str(syllable_number) + "_onset",
                                    str(syllable_number) + "_nucleus",
                                    str(syllable_number) + "_coda"]}
        onset = []
        nucleus = []
        coda = []

        for lexeme in lexicon:
            lex_split = lexeme.split('.')
            if syllable_number < len(lex_split):
                # special behaviour if it is the final syllable. Only take onset!
                if syllable_number == len(lex_split) - 1:
                    lex_syl = _split_syllable_into_phonotactic_positions(lex_split[syllable_number])
                    onset.append(lex_syl[0])
                else:
                    lex_syl = _split_syllable_into_phonotactic_positions(lex_split[syllable_number])

                    onset.append(lex_syl[0])
                    nucleus.append(lex_syl[1])
                    coda.append(lex_syl[2])
        for seg in seg_list:
            in_list = [_get_frequency_of_segment_in_list(seg, onset),
                       _get_frequency_of_segment_in_list(seg, nucleus),
                       _get_frequency_of_segment_in_list(seg, coda)]
            output_dict[seg] = in_list
        return output_dict
    # final syllable behaviour. This ignores the onset and only takes final nucleus and coda (coda is always empty)
    else:
        output_dict = {'syllable': ["final_nucleus",
                                    "final_coda"]}

        nucleus = []
        coda = []

        for lexeme in lexicon:
            lex_split = lexeme.split(".")
            lex_syl = _split_syllable_into_phonotactic_positions(lex_split[len(lex_split) - 1])

            nucleus.append(lex_syl[1])
            coda.append(lex_syl[2])

        # for each set of nucleus and coda, get the frequency of each configuration. Coda is expected to only
        # have 0, and this feature can be used for debugging of this function.
        for seg in seg_list:
            in_list = [_get_frequency_of_segment_in_list(seg, nucleus),
                       _get_frequency_of_segment_in_list(seg, coda)]
            output_dict[seg] = in_list
        return output_dict


def _get_phonotactic_entropy(k_row):
    """
    Calculate entropy of a position by summing the probability * positive log probability value of each possible
    configuration.
    """

    # initialise variables
    output_row = {"syl": k_row['syllable']}
    k_keys = []

    # get list of segments from keys
    for key in k_row.keys():
        if key != "syllable":
            k_keys.append(key)

    total_count = 0
    # because empty cells are represented as 0, there is no need for checking for 'empty' cells
    for key in k_keys:
        total_count = total_count + int(k_row[key])

    seq_probs = []
    # if a row has 0, simply append 0 probabiliy. otherwise, calculate probability
    for key in k_keys:
        if total_count == 0:
            seq_probs.append(0)
        else:
            seq_probs.append(int(k_row[key]) / total_count)

    entropy = 0
    for seq_prob in seq_probs:
        # for probabilities greater than zero, add together individual entropy values.
        # entropy is equivalent to the sum of each surprisal times the corresponding probability
        if seq_prob > 0:
            entropy = entropy + (seq_prob * (log(seq_prob, 2) * -1))

    output_row["entropy"] = entropy
    return output_row


def _get_phonotactic_surprisal(fq_row):
    """
    Gets surprisals for each segment in row.
    """
    surprisal_row = {}
    # get sum
    row_sum = 0
    for key in fq_row.keys():
        if key != "syllable":
            row_sum = row_sum + int(fq_row[key])
    for key in fq_row.keys():
        if key == "syllable":
            surprisal_row["syllable"] = fq_row["syllable"]
        else:
            if row_sum == 0:
                surprisal_row[key] = -1
            else:
                prob = int(fq_row[key]) / row_sum
                if prob == 0:
                    surprisal_row[key] = -1
                else:
                    surprisal_row[key] = log(int(fq_row[key]) / row_sum, 2) * -1
    return surprisal_row


def _get_surprisal_of_syllable(syl, num, word_len, sur_dict_list):
    surprisal_in_positions = [0] * 3
    syl_poss = _split_syllable_into_phonotactic_positions(syl)
    for k_row in sur_dict_list:
        # special behaviour if final syllable
        if num == word_len - 1:
            if k_row["syllable"] == str(num) + "_onset":
                surprisal_in_positions[0] = float(k_row[syl_poss[0]])
            elif k_row["syllable"] == "final_nucleus":
                surprisal_in_positions[1] = float(k_row[syl_poss[1]])
            elif k_row["syllable"] == "final_coda":
                # final coda will always be 0, and is factored out of calculation
                surprisal_in_positions[2] = float(k_row[syl_poss[2]])
        else:
            if k_row["syllable"] == str(num) + "_onset":
                surprisal_in_positions[0] = float(k_row[syl_poss[0]])
            elif k_row["syllable"] == str(num) + "_nucleus":
                surprisal_in_positions[1] = float(k_row[syl_poss[1]])
            elif k_row["syllable"] == str(num) + "_coda":
                surprisal_in_positions[2] = float(k_row[syl_poss[2]])

    return sum(surprisal_in_positions)


##########################################
# Public Functions
##########################################

def get_frequency_of_each_config_in_word_position(lexicon, config_list):
    """
    For the input syllabified lexicon and list of segmental configurations, this function counts the occurrences
    of these segments according to phonotactic positions.
    """
    new_dict = None
    for syl_num in range(0, _get_max_syl_count(lexicon)):
        seg_dict = _get_frequency_of_configurations_in_syllable(lexicon, config_list, syl_num, False)
        if syl_num > 0:
            new_dict = _update_dict(new_dict, seg_dict)
        else:
            new_dict = seg_dict
    # assign final syllable
    final_dict = _get_frequency_of_configurations_in_syllable(lexicon, config_list, -1, True)
    new_dict = _update_dict(new_dict, final_dict)
    output_dict_list = [dict(zip(new_dict, t)) for t in zip(*new_dict.values())]
    return output_dict_list


def get_phontactic_entropies(fq_dict):
    """
    This function retrieves the entropy of each row in the output of get_frequency_of_each_config_in_word_position.
    Look at documentation for sub-functions for further details.
    """
    entropys = []
    for row in fq_dict:
        entropys.append(_get_phonotactic_entropy(row))
    return entropys


def get_surprisals_of_lexicon(syl_lex, sur_dict_list):
    """
    Produces the mean surprisal value for each lexeme in syl_lex.
    syl_lex: Syllabified lexicon
    sur_dict_list: output from get_phonotactic_surprisals.
    """
    out_dict_list = []
    for lexeme in syl_lex:
        lex_sylab = lexeme.split(".")
        surprisal_value = 0
        out_dict = {}
        for i, syl in enumerate(lex_sylab):
            surprisal_value = surprisal_value + _get_surprisal_of_syllable(syl, i, len(lex_sylab), sur_dict_list)
        out_dict["lexeme"] = lexeme
        out_dict["mean_surprisal"] = surprisal_value / (
                (len(lex_sylab) * 3) - 1)  # three phonotactic positions for each
        # syllable excluding final coda
        out_dict_list.append(out_dict)
    return out_dict_list


def get_phonotactic_surprisals(fq_dict):
    """
    For each row in dict, gets surprisal of each configuration. This is calculated by getting the probability of the
    configuration in that position, and then calculating the surprisal based on this (the positive base-2 log of the
    probability).
    """
    surprisal_dict = []
    for row in fq_dict:
        surprisal_dict.append(_get_phonotactic_surprisal(row))
    return surprisal_dict
