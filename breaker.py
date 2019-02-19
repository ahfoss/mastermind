import sys
import time
import itertools as it
#import numpy as np
from os import system
from random import choices
from random import sample
from random import shuffle

from mastermind import score_guess_cython_8color
from mastermind import update_possibilities_cython

# testing: NUM_SPOTS=3, r=1, w=0 on first guess takes about 2.5 seconds
# testing: NUM_SPOTS=3, r=0, w=0 on first guess takes about 24.5 seconds

# TODO: Allow guesses not in set of possibilities
# TODO: Monte Carlo sampling of options until specified time length elapses
# TODO: Multicore

NUM_SPOTS = 5
MAX_GUESS_TIME = 50 # in seconds
MAX_PAIR_TIME = 10
PROP_TIME_PAIRS = 0.1

COLOR_LIST = [ 'black', 'blue', 'green', 'orange', 'pink', 'purple', 'white', 'yellow', ]
NUM_COLOR = len(COLOR_LIST)
COLOR_ABBREVS = list(range(NUM_COLOR)) #['a','u','g','o','i','r','w','y']
COLOR_DICT = dict(zip(COLOR_ABBREVS, COLOR_LIST))

ALL_GUESSES = list(it.product(*[COLOR_ABBREVS]*NUM_SPOTS))

COLOR_PAIRS = list(it.product(*[COLOR_ABBREVS]*2))
PAIR_GUESSES = [[elm[0]] * (NUM_SPOTS // 2 + NUM_SPOTS % 2) + [elm[1]] * (NUM_SPOTS // 2) for elm in COLOR_PAIRS]
NUM_PAIR_GUESSES = len(PAIR_GUESSES)

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

if __name__ == "__main__":
    current_poss = ALL_GUESSES
    shuffle(current_poss)
    shuffle(PAIR_GUESSES)
    first_guess = True
    while True:
        if first_guess:
#            # with replacement
#            current_guess = choices(COLOR_ABBREVS, k = NUM_SPOTS)
#            # without replacement
#            current_guess = sample(COLOR_ABBREVS, NUM_SPOTS)
            current_guess = current_poss[0]
            # for debugging:
            #current_guess = [0] * NUM_SPOTS
            first_guess = False
        else:
            num_choices_remaining = len(current_poss)
            expectations = [num_choices_remaining] * num_choices_remaining
            print('Number of possibilities remaining: ', str(num_choices_remaining))
            printProgressBar(0,num_choices_remaining, length = 50)
            start = time.time()
            for i in range(num_choices_remaining):
                printProgressBar(i,num_choices_remaining, length = 50)
                countlist = [0] * num_choices_remaining
                for j in range(num_choices_remaining):
                    new_history = (current_poss[j], score_guess_cython_8color(current_poss[i], current_poss[j]))
                    reduced_poss = update_possibilities_cython(current_poss, new_history, num_color = NUM_COLOR)
                    countlist[j] = len(reduced_poss)
                expectations[i] = sum(countlist)
                if time.time() - start > MAX_GUESS_TIME: break
#            pair_expectations = [NUM_PAIR_GUESSES] * NUM_PAIR_GUESSES
#            start = time.time()
#            for i in range(len(PAIR_GUESSES)):
#                pair_countlist = [0] * NUM_PAIR_GUESSES
#                for j in range(NUM_PAIR_GUESSES):
#                    pair_new_history = (
            minval = min(expectations)
            minind = [i for i,x in enumerate(expectations) if x == minval][0]
            current_guess = current_poss[minind]
            playNote(1/4, 3/2 * 440)
            print(str(round(time.time() - start, 1)) + ' seconds elapsed.')
        print('My guess is:')
        print([COLOR_DICT[col] for col in current_guess])
        numred = int(input('Num reds?  '))
        if numred == NUM_SPOTS:
            print("Done! Good game!")
            sys.exit()
        numwhite = int(input('Num whites?  '))
        current_poss = update_possibilities_cython(current_poss, (current_guess, (numred, numwhite)), num_color = NUM_COLOR)
        shuffle(current_poss)
        if len(current_poss) < 1:
            print("No possibilities remaining :(")
            sys.exit()


