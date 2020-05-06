import parselmouth
import numpy as np
from vowel_class import Vowel


def parse_input_sound(sound_path, text_grid_filepath):
    vowels_list = []
    for sound in range(len(sound_path)):
        snd = parselmouth.Sound(sound_path[sound])
        intervals = extract_intervals(text_grid_filepath[sound])
        for word in intervals:
            i = 0
            for interval in intervals[word]:
                f1, f2 = get_formants(snd, interval[0],  interval[1])
                new_vowel = Vowel(f1, f2)
                new_vowel.word_idx = word
                new_vowel.segment_in_word_idx = i
                vowels_list.append(new_vowel)
                i += 1
    return vowels_list


def extract_intervals(text_grid_filepath):
    """
    important - you must create intervals of the vowels and for word end, call it - "wordend"
    :param text_grid_filepath:
    :return:
    """
    file = open(text_grid_filepath, 'r')
    file_text = file.read()
    split = file_text.split('intervals')
    res = {}
    word_idx = 0
    for sen in split:
        sp = sen.split()
        if "text" in sp:
            if '"wordend"' in sp:
                word_idx += 1
                continue
            elif '""' not in sen:
                res.setdefault(word_idx, []).append((float(sp[3]), float(sp[6])))
    file.close()
    return res


def get_formants(parselmouth_sound, start_time, end_time):
    """
    extract formants from parselmouth sound object, according to start time - end time.
    calculated by the mean of all values in each time stamp.
    :param parselmouth_sound:
    :param start_time:
    :param end_time:
    :return:
    """
    snd_part = parselmouth_sound.extract_part(from_time=start_time, to_time=end_time, preserve_times=True)
    formant = snd_part.to_formant_burg(max_number_of_formants=4)
    res = []
    for i in range(1, 3):
        sum = 0
        none_number = 0
        for ts in formant.t_grid():
            cur_f1 = formant.get_value_at_time(formant_number=i, time=ts)
            if not np.isnan(cur_f1):
                sum += cur_f1
            else:
                none_number += 1
        res.append(sum / (len(formant.t_grid()) - none_number))
    return res[0], res[1]

