import itertools as it

COLOR_LIST = [ 'black', 'blue', 'green', 'orange', 'pink', 'purple', 'white', 'yellow', ]
COLOR_ABBREVS = ['a','u','g','o','i','r','w','y']
COLOR_DICT = dict(zip(COLOR_ABBREVS, COLOR_LIST))

ALL_GUESSES = list(it.product(COLOR_LIST, COLOR_LIST, COLOR_LIST, COLOR_LIST, COLOR_LIST))

def expand_color_string(ss):
    as_list = [s for s in ss]
    return [COLOR_DICT[cc] for cc in as_list]

class ColorCounter:
    def __init__(self, guess):
        self.color_counts = dict(zip(COLOR_LIST, [0]*8))
        for elm in guess:
            self.color_counts[elm] += 1
    def countMatches(self, ccounter):
        counter = 0
        for color in COLOR_LIST:
            num_guess = self.color_counts[color]
            num_truth = ccounter.color_counts[color]
            counter += min(num_guess,num_truth)
        return counter

def score_guess(guess, truth):
    red_counter = 0
    for g,t in zip(guess,truth):
        if g == t: red_counter += 1
    guess_counter = ColorCounter(guess)
    truth_counter = ColorCounter(truth)
    num_matches = guess_counter.countMatches(truth_counter)
    return red_counter, num_matches - red_counter

def valid_possibility(possibility, history):
    """
    possibility: a color 5-tuple
    history: a list of (color 5-tuple, (r,w)) tuples
    """
    return all([hh[1] == score_guess(guess = hh[0], truth = possibility) for hh in history])

def update_possibilities(possibilities, history):
    """
    possibilities: a list of color 5-tuples
    history: a list of (color 5-tuple, (r,w)) tuples
    """
    return [pp for pp in possibilities if valid_possibility(pp, history)]

if __name__ == "__main__":
#    print("expand_color_string('uairwy')")
#    print(expand_color_string('uairwy'))
    c1 = ColorCounter(expand_color_string('yauga'))
    c2 = ColorCounter(expand_color_string('aarrr'))
#    print("c1.color_counts")
#    print(c1.color_counts)
#    print("c1.countMatches(c2)")
#    print(c1.countMatches(c2))
    print("score_guess(expand_color_string('yauga'),expand_color_string('yauar'))")
    print(score_guess(expand_color_string('yauga'),expand_color_string('yauar')))
    sample_poss = [ALL_GUESSES[i] for i in [5,60,600,500]]
    print("sample_poss")
    print(sample_poss)
    sample_history = [
    ]





