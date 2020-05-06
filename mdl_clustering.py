import random
import math
from copy import deepcopy
import simulated_annealing

INITIAL_TEMP = 1000
COOLING_RATE = 0.9995
THRESHOLD = 10 ** (-6)


class MdlModel:
    def __init__(self, grammar, data):
        self.grammar = grammar
        self.data = data
        self.cluster = {}

    def __repr__(self):
        return "grammar: " + str(self.grammar) + "\nclustering: " + str(self.cluster) + "\n"

    def get_neighbor(self):
        guess = random.randint(0, 1)
        neighbor = deepcopy(self)
        if len(self.grammar) == len(self.data):
            neighbor.remove_rule()
            return neighbor
        if len(self.grammar) == 0:
            neighbor.add_rule()
            return neighbor
        if guess == 0:
            neighbor.add_rule()
        else:
            neighbor.remove_rule()
        return neighbor

    def get_model_size(self):
        self.cluster = {}
        res = len(self.grammar)
        grammar_size = len(self.grammar)
        if grammar_size == 0:
            res = 0
        else:
            res = grammar_size * (math.log(grammar_size, 2))
        for elem in self.data:
            if elem in self.grammar:
                continue
            min_distance = 100000
            min_mean_point = None
            for rule in self.grammar:
                cur_dist = elem.euclidean_distance(rule)
                if cur_dist < min_distance:
                    min_distance = cur_dist
                    min_mean_point = rule
            res += min_distance * 0.01
            self.cluster.setdefault(min_mean_point, []).append(elem)
        return res

    def add_rule(self):
        added_rule = random.choice(self.data)
        while added_rule in self.grammar:
            added_rule = random.choice(self.data)
        self.grammar.append(added_rule)

    def remove_rule(self):
        self.grammar.remove(random.choice(self.grammar))


def mdl_cluster(data):
    grammar = []
    model = MdlModel(grammar, data)
    sa = simulated_annealing.SimulatedAnnealing(INITIAL_TEMP, THRESHOLD, COOLING_RATE)
    ans = sa.run(model)
    ans.grammar = []
    for key in ans.cluster.keys():
        key.prototype = key
        for instance in ans.cluster[key]:
            instance.prototype = deepcopy(key)
        ans.grammar.append(deepcopy(key))
    return ans
