import json
import math
from model import MarbleWorld
from random import choices
from sys import argv

# Note: All json files produced and used by the code below aren't actually json
# files. They're files where each line is a json object, separated by newlines.
# You should read them with json.loads(f.readline()) as in the functions below.

# given a trial dictionary, setup the world and simulate the trial
# e.g. an element of trial_config.json
def run_trial(trial, animate=False, outcome_record_bodies=[], path_record_bodies=[],
              image_path='figures/{}.png', save_dir='figures/frames/animation{:03}.png', save_frames=[]):
    w = MarbleWorld(trial['marbles'], trial['extra_walls'], gate=('gate' in trial),
                    outcome_record_bodies=outcome_record_bodies, path_record_bodies=path_record_bodies)
    return w.simulate(image_path, save_dir, save_frames, animate)


# through = True/False --> count how often target made it / did not make it through
# var is the marble whose velocity and delay is varied
# note that in some situations, delay and magnitude will physically not matter;
#   you can set delay_range=[0] and magn_range=[20] or something
def run_all(trial, target, var, through, path='all_simulation_results.json',
            delay_range=range(0, 100, 5), angle_range=range(90, 270, 5), magn_range=range(10, 30)):
    count = 0
    total = 0
    marbles = trial['marbles']
    orig_var = marbles[var].copy()
    marbles[var]['noisy'] = -1

    with open(path, 'w') as f:
        for delay in delay_range:
            print(delay)
            for angle in angle_range:
                for magn in magn_range:
                    marbles[var]['velocity'] = (math.cos(math.radians(angle)) * magn / 10, math.sin(math.radians(angle)) * magn / 10)
                    marbles[var]['delay'] = delay
                    events, _ = run_trial(trial, outcome_record_bodies=[target])
                    events['config'] = marbles
                    f.write(json.dumps(events) + '\n')
                    total += 1
                    if (not through) ^ events['outcome'][target]:
                        count += 1

    marbles[var] = orig_var
    return (count, total)

# ideal_condition is a function that takes (events, target, var)
#   and returns a boolean of whether it is ideal
# some examples are ideal_helper (below) etc.
def get_ideals(target, var, ideal_condition, inpath='all_simulation_results.json', outpath='ideals.json'):
    with open(inpath, 'r') as inf, open(outpath, 'w') as outf:
        delay_posns = {}
        posn = inf.tell()
        line = inf.readline().rstrip()
        while line:
            events = json.loads(line)
            delay = events['config'][var]['delay']
            if delay not in delay_posns:
                delay_posns[delay] = []
            if ideal_condition(events, target, var):
                delay_posns[delay].append(posn)
            posn = inf.tell()
            line = inf.readline().rstrip()

        for delay in delay_posns:
            for pos in delay_posns[delay]:
                inf.seek(pos)
                outf.write(inf.readline().rstrip() + '\n')

def run_ideals_file(target, var, through, samples, ideals_path='ideals.json',
                    extra_walls=[], collide_condition=False):
    with open(ideals_path, 'r') as f:
        total = 0
        count = 0
        ideals = []

        line = f.readline()
        while line:
            ideals.append(json.loads(line)['config'])
            line = f.readline()
        for marbles in choices(ideals, k=samples):
            marbles[var]['noisy'] = marbles[var]['delay']
            events, _ = run_trial({"marbles": marbles, "extra_walls": extra_walls}, outcome_record_bodies=[target])
            if collide_condition:
                collided = False
                for coll in events['collisions']:
                    if coll['objects'] == (target, var) or coll['objects'] == (var, target):
                        collided = True
                        break
                if collided:
                    total += 1
                    if (not through) ^ events['outcome'][target]:
                        count += 1
            else:
                total += 1
                if (not through) ^ events['outcome'][target]:
                    count += 1

        return (count, total)

def ideal_helper(events, target, var, threshold=math.inf):
    return events['outcome'][target] and events['outcome_dists'][target] < threshold**2

def ideal_hinderer(events, target, var, threshold=0):
    return (not events['outcome'][target]) and events['outcome_dists'][target] > threshold**2

def ideal_obstacle(events, target, var, lim_bounces=4, dist_threshold=math.inf):
    if events['outcome'][target]:
        col_step = events['collisions'][0]['step']
        var_bounces = sum((var in e['objects'] and e['step'] < col_step) for e in events['wall_bounces'])
        return events['outcome_dists'][target] < dist_threshold**2 and var_bounces <= lim_bounces
    else:
        return False

def ideal_non_obstacle(events, target, var, lim_bounces=2, dist_threshold=math.inf):
    if events['outcome'][target]:
        col_step = events['collisions'][0]['step']
        var_bounces = sum((var in e['objects'] and e['step'] < col_step) for e in events['wall_bounces'])
        return events['outcome_dists'][target] < dist_threshold**2 and var_bounces <= lim_bounces
    else:
        return False

def load_trials(path):
    with open(path) as f:
        data_str = f.read()
        return json.loads(data_str)

# ideals_config = [(target, var, through, ideals_path, extra_walls), ...]
def noise_vs_failure(ideals_config, samples, data_path='noise_vs_failure.dat', collide_condition=False):
    noises = [x/1000 for x in range(0, 10)] + [x/100 for x in range(1, 10)] + [x/10 for x in range(1, 20)]
    # noises = [x/10 for x in range(1, 21)]
    with open(data_path, 'a') as f:
        for noise in noises:
            print(noise)
            MarbleWorld.velocity_noise = noise
            f.write(str(noise))
            for target, var, through, path, walls in ideals_config:
                count, total = run_ideals_file(target, var, through, samples,
                                               ideals_path=path, extra_walls=walls,
                                               collide_condition=collide_condition)
                f.write('\t{:.1%}'.format(count/total))
            f.write('\n')

# warning: many hard-coded literals below
def noise_vs_failure_thresholds_exp1(output_path):
    config = []
    with open(output_path, 'w') as f:
        f.write('noise')

        for thres in [30, 50, 100]:
            def ideal(events, target, var): return ideal_helper(events, target, var, threshold=thres)
            path = 'ideal_helper_lim{}.json'.format(thres)
            get_ideals('E', 'A', ideal, inpath='all_trial0.json', outpath=path)
            config.append(('E', 'A', False, path, []))
            f.write('\thelp_lim{}'.format(thres))

        for thres in [0, 100, 150]:
            def ideal(events, target, var): return ideal_hinderer(events, target, var, threshold=thres)
            path = 'ideal_hinderer_lim{}.json'.format(thres)
            get_ideals('E', 'A', ideal, inpath='all_trial1.json', outpath=path)
            config.append(('E', 'A', True, path, []))
            f.write('\thind_lim{}'.format(thres))

        f.write('\n')
    noise_vs_failure(config, 1000, output_path, collide_condition=True)

# warning: many hard-coded literals below
def noise_vs_failure_thresholds_exp3(output_path):
    # wall from 2ball_trials
    walls = [{'name': 'obstacle', 'position': [595, 155], 'length': 410, 'height': 20, 'color': 'black'}]
    config = []

    with open(output_path, 'w') as f:
        f.write('noise')

        for thres in [3, 4, 5, math.inf]:
        # for thres in [2, 3, 4, 5, math.inf]:
            def ideal(events, target, var): return ideal_obstacle(events, target, var, lim_bounces=thres)
            path = 'ideal_obstacle_lim{}.json'.format(thres)
            get_ideals('E', 'A', ideal, inpath='all_obstacle.json', outpath=path)
            config.append(('E', 'A', False, path, walls))
            f.write('\tobs_lim{}'.format(thres))

        for thres in [2, 1, 0, math.inf]:
        # for thres in [0, 1, 2, 3, 4, 5, math.inf]:
            def ideal(events, target, var): return ideal_non_obstacle(events, target, var, lim_bounces=thres)
            path = 'ideal_non_obstacle_lim{}.json'.format(thres)
            get_ideals('E', 'B', ideal, inpath='all_non_obstacle.json', outpath=path)
            config.append(('E', 'B', False, path, walls))
            f.write('\tnon_lim{}'.format(thres))

        f.write('\n')
    noise_vs_failure(config, 1000, output_path, collide_condition=False)

def experiment1_simulations():
    # function for running experiment 1 simulations
    # it creates a table with columns for noise, hinderer, and helper probabilities
    walls = []
    config = []
    trials = [0, 1]

    for trial in trials:
        if trial == 0:
            def ideal(events, target, var): return ideal_hinderer(events, target, var, threshold=0)
        elif trial == 1:
            def ideal(events, target, var): return ideal_helper(events, target, var, threshold=math.inf)
        get_ideals('E', 'A', ideal, inpath='all_trial' + str(trial) + '.json', outpath='ideal_trials_' + str(trial) + '.json')
        config.append(('E', 'A', True, 'ideal_trials_' + str(trial) + '.json', walls))

    noise_vs_failure(config, 1000, data_path='experiment1_simulations.dat', collide_condition=True)

if __name__ == '__main__':
    if len(argv) > 2:
        try:
            trials = load_trials(argv[1])
            run_trial(trials[int(argv[2])], animate=True)
            # example: python simulations.py trial_config.json 2
        except:
            raise ValueError("please pass a valid trials file and a valid index into the trials file")
    else:
        print('usage: python simulation.py <trial_info>.json <trial index>')
    # experiment1_simulations()
    # noise_vs_failure_thresholds_exp3('experiment3_simulations.dat')
