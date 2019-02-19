def update_possibilities_cython(possibilities, history, num_color):
    return([pp for pp in possibilities if history[1] == score_guess_cython(history[0], truth = pp, num_color = num_color)])

def score_guess_cython(guess, truth, num_color):
    red_counter = 0
    for g,t in zip(guess,truth):
        if g == t: red_counter += 1
    guess_color_tally = [0] * num_color
    truth_color_tally = [0] * num_color
    for elm in guess:
        guess_color_tally[elm] += 1
    for elm in truth:
        truth_color_tally[elm] += 1
    num_matches = 0
    for i in range(num_color):
        num_matches += min(guess_color_tally[i], truth_color_tally[i])
    return red_counter, num_matches - red_counter
