import argparse
import json
import numpy as np

def compute_turnout(by_party):
    turnout = 0
    for party, votes in by_party.iteritems()    : turnout += votes
    return turnout

def investigate(by_year):
    x, y = [], []
    for year, by_state in by_year.iteritems():
        prev_year = str(int(year)-2)
        if prev_year not in by_year: continue
        for state, by_party in by_state.iteritems():

            # turnout calculation
            turnout_now = compute_turnout(by_party)
            turnout_then = compute_turnout(by_year[prev_year][state])
            turnout_increase = (turnout_now - turnout_then) / float(turnout_then)

            # party calculation
            party = "Democrat"
            democrat_now = by_party[party] / float(turnout_now)
            democrat_then = by_year[prev_year][state][party]/ float(turnout_then)
            democrat_increase = democrat_now - democrat_then

            x.append(turnout_increase)
            y.append(democrat_increase)
    return x, y

def load_json_file(path):
    f = file(path, "r")
    r = json.load(f)
    f.close()
    return r

def draw_scatter(x, y):
    # we import it here so that you can run this without installing mpl
    import matplotlib.pyplot as plt
    plt.scatter(x, y) #, s=area, c=colors, alpha=0.5)
    plt.show()

def main(args):
    data = load_json_file(args.data_file)
    x, y = investigate(data)
    if args.plot:
        draw_scatter(x, y)
    else:
        for x, y in zip(x, y):
            print x,", ",y

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", type=str, help="Path to the json_file")
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    main(args)