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

# testing: NUM_SPOT=3, r=1, w=0 on first guess takes about 2.5 seconds
# testing: NUM_SPOT=3, r=0, w=0 on first guess takes about 24.5 seconds

# TODO: Allow guesses not in set of possibilities
# TODO: Monte Carlo sampling of options until specified time length elapses
# TODO: Multicore

NUM_SPOT = 5
MAX_GUESS_TIME = 50 # in seconds
MAX_PAIR_TIME = 10  # in seconds

COLOR_LIST = [ 'black', 'blue', 'green', 'orange', 'pink', 'purple', 'white', 'yellow', ]
NUM_COLOR = len(COLOR_LIST)
COLOR_ABBREVS = list(range(NUM_COLOR)) #['a','u','g','o','i','r','w','y']
COLOR_DICT = dict(zip(COLOR_ABBREVS, COLOR_LIST))

ALL_GUESSES = list(it.product(*[COLOR_ABBREVS]*NUM_SPOT))

COLOR_PAIRS = list(it.product(*[COLOR_ABBREVS]*2))
PAIR_GUESSES = [[elm[0]] * (NUM_SPOT // 2 + NUM_SPOT % 2) + [elm[1]] * (NUM_SPOT // 2) for elm in COLOR_PAIRS]
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
    current_pair = PAIR_GUESSES
    shuffle(current_pair)
    first_guess = True
    while True:
        if first_guess:
            current_guess = current_poss[0]
            # for debugging:
            #current_guess = list(range(NUM_SPOT)) # [0] * NUM_SPOT
            first_guess = False
        else:
            num_choices_remaining = len(current_poss)
            remaining_choice_expectations = [num_choices_remaining] * num_choices_remaining
            print('Number of possibilities remaining: ', str(num_choices_remaining), '/', NUM_COLOR**NUM_SPOT)
            printProgressBar(0,num_choices_remaining, length = 50)
            rc_start = time.time()
            # iterate through hypothetical true answers
            for i in range(num_choices_remaining):
                printProgressBar(i,num_choices_remaining, length = 50)
                remaining_choice_countlist = [0] * num_choices_remaining
                # iterate through plausible guesses
                for j in range(num_choices_remaining):
                    new_history = (current_poss[j], score_guess_cython_8color(guess = current_poss[j], truth = current_poss[i]))
                    reduced_poss = update_possibilities_cython(current_poss, new_history, num_color = NUM_COLOR)
                    remaining_choice_countlist[j] = len(reduced_poss)
                remaining_choice_expectations[i] = sum(remaining_choice_countlist) / num_choices_remaining
                if time.time() - rc_start > MAX_GUESS_TIME:
                    print()
                    print('Breaking early to save time.')
                    break
            print('Now search for useful color pair guesses...')
            num_pair_remaining = len(current_pair)
            pair_expectations = [num_choices_remaining] *num_choices_remaining
            pair_start = time.time()
            # iterate through hypothetical true answers
            for i in range(num_choices_remaining):
                pair_countlist = [0] * num_pair_remaining
                for j in range(num_pair_remaining):
                    pair_new_history = (current_pair[j], score_guess_cython_8color(guess = current_pair[j], truth = current_poss[i]))
                    pair_reduced_poss = update_possibilities_cython(current_poss, pair_new_history, num_color = NUM_COLOR)
                    pair_countlist[j] = len(pair_reduced_poss)
                pair_expectations[i] = sum(pair_countlist) / num_pair_remaining
                if time.time() - pair_start > MAX_PAIR_TIME: break
            # Now pick best guess
            remaining_choice_minval = min(remaining_choice_expectations)
            pair_minval = min(pair_expectations)
            if remaining_choice_minval <= pair_minval:
                remaining_choice_minind = [i for i,x in enumerate(remaining_choice_expectations) if x == remaining_choice_minval][0]
                current_guess = current_poss[remaining_choice_minind]
            else:
                pair_minind = [i for i,x in enumerate(pair_expectations) if x == pair_minval][0]
                current_guess = current_pair[pair_minind]
            playNote(1/4, 3/2 * 440)
            print(str(round(time.time() - rc_start, 1)) + ' seconds elapsed.')
        print('My guess is:')
        print([COLOR_DICT[col] for col in current_guess])
        numred = int(input('Num reds?  '))
        if numred == NUM_SPOT:
            print("Done! Good game!")
            sys.exit()
        numwhite = int(input('Num whites?  '))
        current_poss = update_possibilities_cython(current_poss, (current_guess, (numred, numwhite)), num_color = NUM_COLOR)
        shuffle(current_poss)
        shuffle(current_pair)
        if len(current_poss) < 1:
            print("No possibilities remaining: At least one response you gave must be wrong.")
            sys.exit()


