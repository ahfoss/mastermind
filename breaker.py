import sys
import itertools as it
from os import system
from random import choices
from random import sample

# TODO: Allow guesses not in set of possibilities
# TODO: Speedup main routine: use integer coding? cython?
# TODO: Change initial guess

NUM_SPOTS = 3

COLOR_LIST = [ 'black', 'blue', 'green', 'orange', 'pink', 'purple', 'white', 'yellow', ]
COLOR_ABBREVS = ['a','u','g','o','i','r','w','y']
COLOR_DICT = dict(zip(COLOR_ABBREVS, COLOR_LIST))

ALL_GUESSES = list(it.product(*[COLOR_ABBREVS]*NUM_SPOTS))

def playNote (duration, freq):
    system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))

def printProgressBar (iteration, total, prefix = 'Calculating next guess:', suffix = 'Complete', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def expand_color_string(ss):
    as_list = [s for s in ss]
    return [COLOR_DICT[cc] for cc in as_list]

class ColorCounter:
    def __init__(self, guess):
        self.color_counts = dict(zip(COLOR_ABBREVS, [0]*8))
        for elm in guess:
            self.color_counts[elm] += 1
    def countMatches(self, ccounter):
        counter = 0
        for color in COLOR_ABBREVS:
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
    possibility: a color 5-tuple (adjust 5 based on NUM_SPOTS)
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
#    c1 = ColorCounter(expand_color_string('yauga'))
#    c2 = ColorCounter(expand_color_string('aarrr'))
#    print("score_guess(expand_color_string('yauga'),expand_color_string('yauar'))")
#    print(score_guess(expand_color_string('yauga'),expand_color_string('yauar')))
#    sample_poss = [ALL_GUESSES[i] for i in range(100)]#[0,1,2,3,4,5,6,1000,1100]]
#    print("sample_poss")
#    print(sample_poss)
#    sample_history = [
#        (('black', 'black', 'black', 'black', 'black'),(2,0)),
#        (('pink', 'pink', 'pink', 'pink', 'pink'),(0,0)),
#    ]
#    sample_history = [
#        (('a', 'a', 'u', 'g', 'a'),(3,0)),
#    ]
#    print("sample_history")
#    print(sample_history)
#    print("valid_possibility(sample_poss[0], sample_history)")
#    print(valid_possibility(sample_poss[0], sample_history))
#    print("update_possibilities(sample_poss, sample_history)")
#    print(update_possibilities(sample_poss, sample_history))
#    sys.exit()

    current_poss = ALL_GUESSES#[0:100]
    current_history = []
    first_guess = True
    while True:
        if first_guess:
            # with replacement
            current_guess = choices(COLOR_ABBREVS, k = NUM_SPOTS)
            # without replacement
            current_guess = sample(COLOR_ABBREVS, NUM_SPOTS)
            first_guess = False
        else:
            num_choices_remaining = len(current_poss)
            expectations = [0] * num_choices_remaining
            print('Number of possibilities remaining: ', str(num_choices_remaining))
            printProgressBar(0,num_choices_remaining, length = 50)
            for i, ith_guess in enumerate(current_poss):
                printProgressBar(i,num_choices_remaining, length = 50)
                countlist = [0] * num_choices_remaining
                for j, jth_guess in enumerate(current_poss):
                    jth_history = current_history + [(jth_guess, score_guess(ith_guess, jth_guess))]
                    reduced_poss = update_possibilities(current_poss, jth_history)
                    countlist[j] = num_choices_remaining - len(reduced_poss)
                expectations[i] = sum(countlist) / len(countlist)
            printProgressBar(num_choices_remaining,num_choices_remaining, length = 50)
            maxval = max(expectations)
            maxind = [i for i,x in enumerate(expectations) if x == maxval][0]
            current_guess = current_poss[maxind]
#            playNote(1, 440)
            playNote(1/4, 3/2 * 440)
#            playNote(1/6, 4/3 * 440)
#            playNote(1/6, 81/64 * 440)
#            playNote(1/6, 9/8 * 440)
#            playNote(1, 2 * 440)
#            for iter in range(1,100):
#                playNote(1/iter**2, 440 * iter/4)
        print('My guess is:')
        print([COLOR_DICT[col] for col in current_guess])
        numred = int(input('Num reds?  '))
        if numred == NUM_SPOTS:
            print("Done! Good game!")
            sys.exit()
        numwhite = int(input('Num whites?  '))
        current_history.append((current_guess, (numred,numwhite)))
        current_poss = update_possibilities(current_poss, current_history)
        if len(current_poss) < 1:
            print("No possibilities remaining :(")
            sys.exit()


