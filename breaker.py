import sys
import time
import itertools as it
#import numpy as np
from os import system
from random import choices
from random import sample

from mastermind import score_guess_cython_8color
from mastermind import update_possibilities_cython

# testing: r=1, w=0 on first guess takes about 2.5 seconds
# testing: r=0, w=0 on first guess takes about 24.5 seconds

# TODO: Allow guesses not in set of possibilities
# TODO: Speedup main routine: cython?
# TODO: Monte Carlo sampling of options until specified time length elapses
# TODO: Multicore

NUM_SPOTS = 3
MAX_GUESS_TIME = 60 # in seconds

COLOR_LIST = [ 'black', 'blue', 'green', 'orange', 'pink', 'purple', 'white', 'yellow', ]
NUM_COLOR = len(COLOR_LIST)
COLOR_ABBREVS = list(range(NUM_COLOR)) #['a','u','g','o','i','r','w','y']
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

def valid_possibility(possibility, history):
    """
    possibility: a color 5-tuple (adjust 5 based on NUM_SPOTS)
    history: a (color 5-tuple, (r,w)) tuple
    """
    return history[1] == score_guess_cython_8color(guess = history[0], truth = possibility)

if __name__ == "__main__":
    current_poss = ALL_GUESSES#[0:100]
    current_history = []
    first_guess = True
    while True:
        if first_guess:
            # with replacement
            current_guess = choices(COLOR_ABBREVS, k = NUM_SPOTS)
            # without replacement
            current_guess = sample(COLOR_ABBREVS, NUM_SPOTS)
            current_guess = [0] * NUM_SPOTS
            first_guess = False
        else:
            num_choices_remaining = len(current_poss)
            expectations = [0] * num_choices_remaining
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
            printProgressBar(num_choices_remaining,num_choices_remaining, length = 50)
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
        if len(current_poss) < 1:
            print("No possibilities remaining :(")
            sys.exit()


