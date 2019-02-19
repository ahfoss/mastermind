def update_possibilities_cython(possibilities, history, num_color):
    return([pp for pp in possibilities if history[1] == score_guess_cython_8color(history[0], truth = pp)])

def score_guess_cython_8color(guess, truth):
    cdef unsigned char red_counter = 0
    cdef unsigned char match_counter = 0
    for g,t in zip(guess,truth):
        if g == t: red_counter += 1
    cdef unsigned char guess_color_tally[8]
    cdef unsigned char truth_color_tally[8]
    guess_color_tally[:] = [0,0,0,0,0,0,0,0]
    truth_color_tally[:] = [0,0,0,0,0,0,0,0]
    for elm in guess:
        guess_color_tally[elm] += 1
    for elm in truth:
        truth_color_tally[elm] += 1
    for i in range(8):
        match_counter += min(guess_color_tally[i], truth_color_tally[i])
    return red_counter, match_counter - red_counter
