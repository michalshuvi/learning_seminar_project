import math


class Vowel:
    def __init__(self, f1, f2):
        self.f1 = f1
        self.f2 = f2
        self.word_idx = None
        self.segment_in_word_idx = None
        self.features = {
                        "high": None,
                        "low": None,
                        "back": None
        }
        self.needed_features = {}
        self.prototype = None

    def __repr__(self):
        return "(" + str(self.f1) + ", " + str(self.f2) + ", " + str(self.word_idx) + ", " \
               + str(self.segment_in_word_idx) + ", prototype: " + \
               ("it's a prototype " if self.prototype == self else str(self.prototype)) + \
               ", features:" + str(self.features) + ", needed featurs: " + str(self.needed_features) + ")"

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.f1 == other.f1 and self.f2 == other.f2

    def __hash__(self):
        return hash((self.f1, self.f2))

    def euclidean_distance(self, other):
        return math.sqrt(math.pow(self.f2 - other.f2, 2) + math.pow(self.f1 - other.f1, 2))

