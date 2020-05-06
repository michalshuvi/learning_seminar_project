import random
from copy import deepcopy
from vowel_class import Vowel
from simulated_annealing import SimulatedAnnealing

ENVIRONMENT_BEFORE = "before"
ENVIRONMENT_AFTER = "after"
INITIAL_TEMP = 1000
COOLING_RATE = 0.9995
THRESHOLD = 10 ** (-6)


class MdlPhonology:
    def __init__(self, vowels, lexicon, data_input, possible_features):
        self.possible_features = possible_features
        self.UR_features = []
        self.vowels = vowels
        self.original_lexicon = lexicon
        self.cur_lexicon = None
        self.rules = []
        self.data_input = data_input

    def __repr__(self):
        return "current lexicon: " + str(self.cur_lexicon) + "\nrules: " + str(self.rules) + "\ndata input: " + str(
            self.data_input)

    def get_neighbor(self):
        neighbor = deepcopy(self)
        if len(neighbor.rules) == 0:
            neighbor.add_rule()
        else:
            guess = random.randint(0, 2)
            if guess == 0:
                neighbor.add_rule()
            elif guess == 1:
                neighbor.delete_rule()
            else:
                neighbor.change_rule()
        return neighbor

    def add_rule(self):
        rule = Rule(self.possible_features)
        while not rule.is_valid():
            rule.add_to_rule()
        self.rules.append(rule)

    def delete_rule(self):
        chosen = random.choice(self.rules)
        self.rules.remove(chosen)

    def change_rule(self):
        chosen = random.choice(self.rules)  # choose rule to change
        chosen.change()  # change the chosen rule

    def apply_rules(self):
        self.cur_lexicon = deepcopy(self.original_lexicon)
        if len(self.rules) == 0:
            for word in self.cur_lexicon:
                for vowel in word:
                    vowel.needed_features = vowel.features
        else:
            for rule in self.rules:
                self.apply_rule(rule)

    def apply_rule(self, rule):
        lexicon = deepcopy(self.cur_lexicon)
        before = False
        after = False
        if ENVIRONMENT_BEFORE in rule.environment.keys():
            before = True
        if ENVIRONMENT_AFTER in rule.environment.keys():
            after = True
        if before and not after:
            for word in lexicon:
                first_applied = True
                for i in range(0, len(word) - 1):
                    if all(item in word[i].features.items() for item in
                           rule.environment[ENVIRONMENT_BEFORE].items()) and \
                            all(item in word[i + 1].features.items() for item in rule.target_features.items()):
                        if first_applied:
                            word[i].needed_features = word[i].features
                            first_applied = False
                        word[i + 1].needed_features = {k: word[i + 1].features[k] for k in word[i + 1].features.keys()
                                                       if k not in rule.target_features}
                    else:
                        word[i].needed_features = word[i].features
                        if i + 1 == len(word) - 1:
                            word[i + 1].needed_features = word[i + 1].features
        elif after and not before:
            for word in lexicon:
                for i in range(1, len(word)):
                    if all(item in word[i].features.items() for item in
                           rule.environment[ENVIRONMENT_AFTER].items()) and \
                            all(item in word[i - 1].features.items() for item in rule.target_features.items()):
                        word[i - 1].needed_features = {k: word[i - 1].features[k] for k in word[i - 1].features.keys()
                                                       if k not in rule.target_features}
                    else:
                        if i == 1:
                            word[i - 1].needed_features = word[i - 1].features
                    word[i].needed_features = word[i].features
        elif after and before:
            for word in lexicon:
                for i in range(len(word)):
                    if i == 0 or i == (len(word) - 1):
                        word[i].needed_features = word[i].features
                        continue
                    if all(item in word[i - 1].features.items() for item in
                           rule.environment[ENVIRONMENT_BEFORE].items()) and \
                            all(item in word[i + 1].features.items() for item in
                                rule.environment[ENVIRONMENT_AFTER].items()) \
                            and all(item in word[i].features.items() for item in rule.target_features.items()):
                        word[i].needed_features = {k: word[i].features[k] for k in word[i].features.keys()
                                                   if k not in rule.target_features}
                    else:
                        word[i].needed_features = word[i].features
                    word[i - 1].needed_features = word[i - 1].features
                    word[i + 1].needed_features = word[i + 1].features
        self.cur_lexicon = lexicon

    def get_model_size(self):
        self.apply_rules()
        word_cost = {}
        bits_per_feature = 3
        print "current lexicon", self.cur_lexicon
        for word in self.cur_lexicon:
            word_features = []
            for vowel in word:
                cur_prototype = vowel.prototype
                if cur_prototype is None:
                    cur_prototype = vowel
                word_features.append(str(self.vowels.index(cur_prototype)))
            # word_features = "".join([str(self.vowels.index(v.prototype)) for v in word])
            word_features = "".join(word_features)
            word_cost[word_features] = 0
            for vowel in word:
                word_cost[word_features] += len(vowel.needed_features) * (bits_per_feature + bits_per_feature)
        rules_cost = 0
        for rule in self.rules:
            rule_cost = 0
            rule_cost += 3 * bits_per_feature * (len(rule.source_features) + len(rule.target_features))
            if ENVIRONMENT_BEFORE in rule.environment.keys():
                rule_cost += 3 * bits_per_feature * (len(rule.environment[ENVIRONMENT_BEFORE]))
            else:
                rule_cost += bits_per_feature  # rule component
            if ENVIRONMENT_AFTER in rule.environment.keys():
                rule_cost += 3 * bits_per_feature * (len(rule.environment[ENVIRONMENT_AFTER]))
            else:
                rule_cost += bits_per_feature  # rule component
            rules_cost += rule_cost
            print "rule bit cost", rule_cost
        grammar_cost = sum(word_cost.values()) + rules_cost
        data_given_grammar = 0
        for word in self.data_input:
            word_annotation = []
            for vowel in word:
                cur_prototype = vowel.prototype
                if cur_prototype is None:
                    cur_prototype = vowel
                word_annotation.append(str(self.vowels.index(cur_prototype)))
            word_annotation = "".join(word_annotation)
            # word_annotation = "".join([str(self.vowels.index(v.prototype)) for v in word])
            data_given_grammar += word_cost[word_annotation]
        print "data given grammar", data_given_grammar
        return data_given_grammar + grammar_cost


class Rule:
    def __init__(self, features):
        self.possible_features = features  # with coefficients
        self.source_features = {}
        self.target_features = {}
        self.environment = {}  # before and after, dict inside of dict

    def __repr__(self):
        if ENVIRONMENT_BEFORE in self.environment:
            before = self.environment[ENVIRONMENT_BEFORE]
        else:
            before = ""
        if ENVIRONMENT_AFTER in self.environment:
            after = self.environment[ENVIRONMENT_AFTER]
        else:
            after = ""
        return str(self.source_features) + "-->" + str(self.target_features) + " /" + \
               str(before) + " ___ " + str(after)

    def add_to_rule(self):
        flag = True
        while flag:
            guess = random.randint(0, 2)
            if guess == 0 and not self.is_environment_full():
                self.add_to_environment()
                flag = False
            elif guess == 1 and not (len(self.source_features.keys()) == len(self.possible_features)):
                self.add_source()
                flag = False
            elif guess == 2 and not (len(self.target_features.keys()) == len(self.possible_features)):
                self.add_target()
                flag = False

    def change(self):
        while not (self.is_valid()):
            self.add_to_rule()
        if self.is_rule_full():
            guess = random.randint(0, 1)
            if guess == 0:
                self.delete_from_rule()
            else:
                self.change_some_feature()
        else:
            flag = True
            while flag:
                guess = random.randint(0, 2)
                if guess == 0:
                    self.add_to_rule()
                    flag = False
                elif guess == 1 and not ((len(self.source_features) == 1) and len(self.target_features) == 1
                                         and has_maximum_one_rule(self.environment)):
                    self.delete_from_rule()
                    flag = False
                else:
                    self.change_some_feature()
                    flag = False

    def is_valid(self):
        return not ((len(self.source_features) == 0)
                    or (len(self.target_features) == 0)
                    or (len(self.environment) == 0))

    def delete_from_rule(self):
        self.make_change_using_func(lambda x, y: delete_from_dict(x, y), "delete")

    def change_some_feature(self):
        self.make_change_using_func(lambda x, y: not x[y], "change")

    def make_change_using_func(self, func, key):
        """
        general method for choosing a rule component and do a func on it
        :param func, key:
        :return:
        """
        rule_parts = [self.source_features, self.target_features, self.environment]
        if key == "delete":
            if len(self.source_features) == 1:
                rule_parts.remove(self.source_features)
            if len(self.target_features) == 1:
                rule_parts.remove(self.target_features)
            if has_maximum_one_rule(self.environment):
                rule_parts.remove(self.environment)
        guess = random.choice(rule_parts)
        if guess == self.environment:
            side = random.choice([ENVIRONMENT_AFTER, ENVIRONMENT_BEFORE])
            while side not in guess:
                side = random.choice([ENVIRONMENT_AFTER, ENVIRONMENT_BEFORE])
            if guess[side] is bool or len(guess[side]) > 1:
                chosen_feature = random.choice(guess[side].keys())
                res = func(guess[side], chosen_feature)
                if res is not None:
                    guess[side][chosen_feature] = res
            elif len(guess[side]) == 1:
                res = func(guess[side], guess[side].keys()[0])
                if res is not None:
                    guess[side][guess[side].keys()[0]] = res
        else:
            chosen_feature = random.choice(guess.keys())
            res = func(guess, chosen_feature)
            if res is not None:
                guess[chosen_feature] = res

    def add_to_environment(self):
        guess = None
        if self.is_environment_full():
            return
        elif ENVIRONMENT_BEFORE in self.environment.keys() and \
                len(self.environment[ENVIRONMENT_BEFORE]) == len(self.possible_features):
            guess = ENVIRONMENT_AFTER
        elif ENVIRONMENT_AFTER in self.environment.keys() and \
                len(self.environment[ENVIRONMENT_AFTER]) == len(self.possible_features):
            guess = ENVIRONMENT_BEFORE
        if guess is None:
            guess = random.choice([ENVIRONMENT_BEFORE, ENVIRONMENT_AFTER])
        if guess in self.environment.keys():
            feature, coefficient = find_unused_feature(self.possible_features, self.environment[guess])
            self.environment[guess][feature] = coefficient
        else:
            feature, coefficient = find_unused_feature(self.possible_features, {})
            self.environment[guess] = {}
            self.environment[guess][feature] = coefficient

    def add_source(self):
        feature, coefficient = find_unused_feature(self.possible_features, self.source_features)
        self.source_features[feature] = coefficient

    def add_target(self):
        feature, coefficient = find_unused_feature(self.possible_features, self.target_features)
        self.target_features[feature] = coefficient

    def is_rule_full(self):
        """
        check if rule uses all features in all rule components
        :return:
        """
        is_environment_full = self.is_environment_full()
        if (len(self.source_features) == len(self.possible_features)) and \
                (len(self.target_features) == len(self.possible_features)) and is_environment_full:
            return True
        else:
            return False

    def is_environment_full(self):
        possible_feature_length = len(self.possible_features)
        if ENVIRONMENT_AFTER not in self.environment or ENVIRONMENT_BEFORE not in self.environment:
            return False
        if len(self.environment[ENVIRONMENT_BEFORE]) == possible_feature_length and \
                len(self.environment[ENVIRONMENT_AFTER]) == possible_feature_length:
            return True
        else:
            return False


def has_maximum_one_rule(environment):
    all_rules = 0
    if ENVIRONMENT_BEFORE in environment.keys():
        all_rules += len(environment[ENVIRONMENT_BEFORE])
    if ENVIRONMENT_AFTER in environment.keys():
        all_rules += len(environment[ENVIRONMENT_AFTER])
    return all_rules < 2


def delete_from_dict(dictionary, y):
    if y in dictionary:
        del dictionary[y]


def find_unused_feature(features_dict, target_dict):
    choose = random.choice(features_dict)
    if len(target_dict) != 0:
        while choose in target_dict.keys():
            choose = random.choice(features_dict)
    value = random.choice([True, False])
    return choose, value


def extract_features(clustered_data):
    # First of all we will find the [+low] vowels
    low_feature_middle_value = find_mean(clustered_data, lambda x: x.f1)
    #  Set the coefficient (+/-) to "low" feature
    #  if a vowel has [+low] than it must have [-high]
    #  if a vowel doesn't have [+low] than we only know that it has [-low] (we know nothing about it's height)
    for prototype in clustered_data.keys():
        if prototype.f1 > low_feature_middle_value:
            prototype.features["low"] = True
            prototype.features["high"] = False
            for vowel in clustered_data[prototype]:
                vowel.features["low"] = True
                vowel.features["high"] = False
        else:
            prototype.features["low"] = False
            for vowel in clustered_data[prototype]:
                vowel.features["low"] = False

    # second we will find the [+high] vowels
    max_f1_prototype = max(clustered_data.keys(), key=lambda x: x.f1 if not x.features["low"] else 0)
    min_f1_prototype = min(clustered_data.keys(), key=lambda x: x.f1 if not x.features["low"] else 3000000)
    highest_bound = min(clustered_data[max_f1_prototype], key=lambda x: x.f1)
    lowest_bound = max(clustered_data[min_f1_prototype], key=lambda x: x.f1)
    high_feature_middle_value = (highest_bound.f1 + lowest_bound.f1) / 2
    for prototype in clustered_data.keys():
        if prototype.features["low"]:
            continue
        else:
            if prototype.f1 > high_feature_middle_value:
                prototype.features["high"] = False
                for vowel in clustered_data[prototype]:
                    vowel.features["high"] = False
            else:
                prototype.features["high"] = True
                for vowel in clustered_data[prototype]:
                    vowel.features["high"] = True

    # Lastly, we will tag the back feature
    back_feature_mean = find_mean(clustered_data, lambda x: (x.f2 - x.f1))
    for prototype in clustered_data.keys():
        delta = prototype.f2 - prototype.f1
        if delta > back_feature_mean:
            prototype.features["back"] = False
            for vowel in clustered_data[prototype]:
                vowel.features["back"] = False
        else:
            prototype.features["back"] = True
            for vowel in clustered_data[prototype]:
                vowel.features["back"] = True
    return clustered_data


def find_mean(clustered_data, function):
    max_prototype = max(clustered_data.keys(), key=function)
    min_prototype = min(clustered_data.keys(), key=function)
    highest_bound = min(clustered_data[max_prototype], key=function)
    lowest_bound = max(clustered_data[min_prototype], key=function)
    return (function(highest_bound) + function(lowest_bound)) / 2


def mdl_phonology_learner(model):
    sa = SimulatedAnnealing(INITIAL_TEMP, THRESHOLD, COOLING_RATE)
    min_mdl_score_model = sa.run(model)
    return min_mdl_score_model


def main():
    # function for testing the phonological rule learner
    # IMPORTANT! f1, f2 values are not real, they are only for the test.
    i = Vowel(2500, 600)
    i.features = {"high": True, "low": False, "back": False}
    i.prototype = deepcopy(i)

    e = Vowel(2500, 600)
    e.features = {"high": False, "low": False, "back": False}
    e.prototype = deepcopy(e)

    o = Vowel(900, 300)
    o.features = {"high": False, "low": False, "back": True}
    o.prototype = deepcopy(o)

    a = Vowel(700, 200)
    a.features = {"high": False, "low": True, "back": True}
    a.prototype = deepcopy(a)

    u = Vowel(500, 300)
    u.features = {"high": True, "low": False, "back": True}
    u.prototype = deepcopy(u)

    lexicon = [[deepcopy(i), deepcopy(i), deepcopy(i)], [deepcopy(u), deepcopy(u), deepcopy(u)],
               [deepcopy(e), deepcopy(i), deepcopy(i)], [deepcopy(e), deepcopy(i)],
               [deepcopy(o), deepcopy(u), deepcopy(u)], [deepcopy(o), deepcopy(u)]]
               # [deepcopy(a), deepcopy(a), deepcopy(i), deepcopy(i)], [deepcopy(i), deepcopy(a)], [deepcopy(e), deepcopy(o), deepcopy(a)]]
    vowels = [deepcopy(i), deepcopy(e), deepcopy(o), deepcopy(u)]# deepcopy(a),
    data_input = [[deepcopy(i), deepcopy(i), deepcopy(i)], [deepcopy(i), deepcopy(i), deepcopy(i)],
                  [deepcopy(i), deepcopy(i), deepcopy(i)], [deepcopy(i), deepcopy(i), deepcopy(i)],
                  [deepcopy(i), deepcopy(i), deepcopy(i)], [deepcopy(u), deepcopy(u), deepcopy(u)],
                  [deepcopy(u), deepcopy(u), deepcopy(u)], [deepcopy(u), deepcopy(u), deepcopy(u)],
                  [deepcopy(u), deepcopy(u), deepcopy(u)], [deepcopy(e), deepcopy(i), deepcopy(i)],
                  [deepcopy(e), deepcopy(i)], [deepcopy(o), deepcopy(u), deepcopy(u)],
                  [deepcopy(o), deepcopy(u)], [deepcopy(o), deepcopy(u)]]
                  # [deepcopy(a), deepcopy(a), deepcopy(i), deepcopy(i)],
                  # [deepcopy(i), deepcopy(a)], [deepcopy(e), deepcopy(o), deepcopy(a)], [deepcopy(i), deepcopy(a)], [deepcopy(e), deepcopy(o), deepcopy(a)]]
    mdl = MdlPhonology(vowels, lexicon, data_input, ["high", "low", "back"])
    for word in mdl.original_lexicon:
        for vowel in word:
            vowel.needed_features = vowel.features
    for word in mdl.data_input:
        for vowel in word:
            vowel.needed_features = vowel.features
    print mdl
    sa = SimulatedAnnealing(INITIAL_TEMP, THRESHOLD, COOLING_RATE)
    model = sa.run(mdl)
    print model



if __name__ == "__main__":
    main()
