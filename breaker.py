import sys
import time
import itertools as it
import numpy as np
from os import system
from random import choices
from random import sample

from update_possibilities import score_guess_cython
from update_possibilities import update_possibilities_cython

# TODO: Allow guesses not in set of possibilities
# TODO: Speedup main routine: cython?
# TODO: Monte Carlo sampling of options until specified time length elapses
# TODO: Multicore

NUM_SPOTS = 3
MAX_GUESS_TIME = 60 # in seconds

COLOR_LIST = [ 'black', 'blue', 'green', 'orange', 'pink', 'purple', 'white', 'yellow', ]
NUM_COLORS = len(COLOR_LIST)
COLOR_ABBREVS = list(range(NUM_COLORS)) #['a','u','g','o','i','r','w','y']
COLOR_DICT = dict(zip(COLOR_ABBREVS, COLOR_LIST))

ALL_GUESSES = np.array(np.meshgrid(*[COLOR_ABBREVS]*NUM_SPOTS), dtype = np.uint8).T.reshape(-1,NUM_SPOTS)

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
    history: a list of (color 5-tuple, (r,w)) tuples
    """
    return history[1] == score_guess_cython(guess = history[0], truth = possibility, num_color = NUM_COLORS)

def update_possibilities(possibilities, history):
    """
    possibilities: a list of color 5-tuples
    history: a list of (color 5-tuple, (r,w)) tuples
    """
    return np.array([pp for pp in possibilities if valid_possibility(pp, history)], dtype = np.uint8)

if __name__ == "__main__":
    current_poss = ALL_GUESSES#[0:100]
    current_history = []
    first_guess = True
    while True:
        if first_guess:
            # with replacement
            current_guess = np.array(choices(COLOR_ABBREVS, k = NUM_SPOTS), dtype = np.uint8)
            # without replacement
            current_guess = np.array(sample(COLOR_ABBREVS, NUM_SPOTS), dtype = np.uint8)
            current_guess = np.array([0] * NUM_SPOTS, dtype = np.uint8)
            first_guess = False
        else:
            num_choices_remaining = current_poss.shape[0]
            expectations = [0] * num_choices_remaining
            print('Number of possibilities remaining: ', str(num_choices_remaining))
            printProgressBar(0,num_choices_remaining, length = 50)
            start = time.time()
            for i in range(num_choices_remaining):
                printProgressBar(i,num_choices_remaining, length = 50)
                countlist = [0] * num_choices_remaining
                for j in range(num_choices_remaining):
                    new_history = (current_poss[j,:], score_guess_cython(current_poss[i,:], current_poss[j,:], num_color = NUM_COLORS))
                    reduced_poss = np.array(update_possibilities_cython(current_poss, new_history, num_color = NUM_COLORS))
                    countlist[j] = reduced_poss.shape[0]
                expectations[i] = sum(countlist)
            printProgressBar(num_choices_remaining,num_choices_remaining, length = 50)
            minval = min(expectations)
            minind = [i for i,x in enumerate(expectations) if x == minval][0]
            current_guess = current_poss[minind,:]
            playNote(1/4, 3/2 * 440)
            print(str(round(time.time() - start, 1)) + ' seconds elapsed.')
        print('My guess is:')
        print([COLOR_DICT[col] for col in current_guess])
        numred = int(input('Num reds?  '))
        if numred == NUM_SPOTS:
            print("Done! Good game!")
            sys.exit()
        numwhite = int(input('Num whites?  '))
        current_poss = update_possibilities(current_poss, (current_guess, (numred, numwhite)))
        if current_poss.shape[0] < 1:
            print("No possibilities remaining :(")
            sys.exit()


