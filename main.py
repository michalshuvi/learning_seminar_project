from copy import deepcopy
import mdl_clustering
import phonology_learner
import signal_parser

POSSIBLE_FEATURES = ["high", "low", "back"]


def main():
    """
    The full learner pipeline, from sound to phonological rule and UR representation of vowels.
    :return:
    """
    sound_path = []
    textgrid_path = []
    # change the data to your own recorded sounds, make sure you have wav file and TextGrid file which
    # mark every vowel with some character, and every word end must be marked with "wordend"
    # theses recordings are only [a], [e], [i], [o], [u] sequence to test the pipeline flow,
    # the phonological rule learner tests are in the "phonological_learner" py file.
    for i in range(1, 5):
        sound_path.append("recordings\\aeiou{}.wav".format(str(i)))
        textgrid_path.append("recordings\\aeiou{}.TextGrid".format(str(i)))
    data = signal_parser.parse_input_sound(sound_path, textgrid_path)  # from sound to vowel objects with f1 and f2
    clustered_data = mdl_clustering.mdl_cluster(data)  # cluster into main values
    final_tagged_data = phonology_learner.extract_features(clustered_data.cluster)  # add phonological features
    update_data(data, final_tagged_data)  # update the input data with the phonological features
    lexicon = find_lexicon(data)  # get lexicon from data
    data = separate_data_into_words(data)
    model = phonology_learner.MdlPhonology(final_tagged_data.keys(), lexicon, data, POSSIBLE_FEATURES)
    print model
    model = phonology_learner.mdl_phonology_learner(model)
    print model


def find_lexicon(data):
    lexicon = []
    cur_word = []
    cur_word_idx = 0
    for elem in data:
        if elem.word_idx > cur_word_idx:
            if cur_word not in lexicon:
                lexicon.append(deepcopy(cur_word))
            cur_word = []
            cur_word_idx += 1
        else:
            if elem.prototype is None:
                cur_word.append(deepcopy(elem))
            else:
                cur_word.append(deepcopy(elem.prototype))
    if cur_word not in lexicon:
        lexicon.append(deepcopy(cur_word))
    return lexicon


def separate_data_into_words(data):
    sep_data = []
    cur_word = []
    cur_word_idx = 0
    for elem in data:
        if elem.word_idx > cur_word_idx:
            sep_data.append(deepcopy(cur_word))
            cur_word = []
            cur_word_idx += 1
        else:
            if elem.prototype is None:
                cur_word.append(deepcopy(elem))
            else:
                cur_word.append(deepcopy(elem.prototype))
    sep_data.append(deepcopy(cur_word))
    return sep_data


def update_data(data, final_tagged_data):
    for key in final_tagged_data:
        for i in range(len(data)):
            if data[i] == key:
                data[i] = deepcopy(key)
        if final_tagged_data[key] == 0:
            continue
        for instance in final_tagged_data[key]:
            for i in range(len(data)):
                if data[i] == instance:
                    data[i] = deepcopy(instance)


if __name__ == "__main__":
    main()
