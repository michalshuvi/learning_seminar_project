import random
import math


class SimulatedAnnealing:
    def __init__(self, initial_temp, threshold, cooling_rate):
        self.initial_temp = initial_temp
        self.threshold = threshold
        self.cooling_rate = cooling_rate

    def run(self, initial_hyp):
        cur_hypothesis = initial_hyp
        temp = self.initial_temp
        while temp > self.threshold:
            new_hypothesis = cur_hypothesis.get_neighbor()
            en2 = new_hypothesis.get_model_size()
            en1 = cur_hypothesis.get_model_size()
            delta = en2 - en1
            if delta < 0:
                p = 1
            else:
                p = math.exp(-(delta / temp))
            guess = random.random()
            if guess < p:
                cur_hypothesis = new_hypothesis
            temp = self.cooling_rate * temp
            print temp
            print cur_hypothesis
        return cur_hypothesis




