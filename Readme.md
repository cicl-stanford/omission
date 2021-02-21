# Omission 

This project contains the materials for the paper "A counterfactual simulation model of causation by omission" by Tobias Gerstenberg and Simon Stephan. 

https://zenodo.org/badge/211161061.svg

# Project structure 

```
.
├── code
│   ├── R
│   │   └── cache
│   ├── flash
│   │   ├── experiment1
│   │   ├── experiment2
│   │   └── experiment3
│   └── python
│       └── figures
├── data
│   ├── empirical
│   └── simulations
├── docs
├── figures
│   ├── diagrams
│   │   ├── experiment1
│   │   ├── experiment2
│   │   ├── experiment3
│   │   └── model
│   ├── experiment_slides
│   │   ├── experiment1
│   │   ├── experiment2
│   │   └── experiment3
│   └── plots
└── videos
    ├── experiment1
    │   ├── mov
    │   └── swf
    ├── experiment2
    │   ├── mov
    │   └── swf
    └── experiment3
        ├── mov
        └── swf
```

## code 

### R 

Analysis and plotting script. You can view a rendered html file of the analysis [here](https://cicl-stanford.github.io/omission/). 

### flash 

Adobe Animate files that were used to create the video clips in the different experiments. 

### python 

#### dependencies
- tested with pygame v1.9.6, pymunk v5.6.0
- `pip install pygame pymunk` (reminder that this is Python 3)
- quick check: in the `code/python/` directory, `python simulations.py trial_config.json 2`
  should show an animation

#### main files
- `model.py` contains the physics simulation and animation code.
- `simulations.py` contains functions that collect data from running
  `model.py`'s simulations.
- `trial_config.json` contains a list of objects that specify the initial
  configuration of a trial.
- `figures/` contains the image files that `model.py` loads for animations.
- precomputed simulations:
  * `all_trial0.json` and `all_trial1.json` contain results for the first and
    second entries in `trial_config.json`, the hinderer and helper case,
    respectively. Delay ranges over `range(0, 100)`, angle ranges over
    `range(100, 260, 2)`, and magnitude ranges over `range(10, 30)`.
  * `all_obstacle.json` and `all_non_obstacle` contain results for the obstacle
    (marble A) and non-obstacle (marble B) case, respectively, from the fourth
    entry in `trial_config.json`. Delay and magnitude don't matter and are set
    to 0 and 20 respectively; angle ranges over `range(1000, 2600) / 10`.

The python files have inline comments explaining
implementation details!

#### running simulations

(Working directory assumed to be `code/python/`.) To quickly visualize a single
trial from a configuration file such as `trial_config.json`, run `python
simulations.py trial_config.json <config index>` and you should see the
animation.

Alternatively, in the Python interpreter, run
```
>>> import simulations
>>> trials = simulations.load_trials('trial_config.json')
```
The module provides a number of functions to collect data from simulations.
- `run_trial` runs a single trial and returns the outcome for specified marbles,
  i.e. whether it went through the exit and what the minimum distance to the
  exit was, and also the recorded paths for specified marbles.
- `run_all` simulates all possible cases for a given configuration, iterating
  over specified delay, angle, and magnitude ranges for the `var` marble. No
  noise is added regardless of the configuration. It saves the results in a file
  and returns a count of trials in which the `target` marble did or did not go
  through the exit.
- `get_ideals` extracts ideal cases from the output produced by `run_all` and
  saves them to a different file. What to consider as "ideal" is specified by
  passing in a Boolean function, e.g. `ideal_helper` or `ideal_obstacle`.
- `run_ideals_file` uniformly samples from the ideal cases output by
  `get_ideals`, runs the simulations with noise, and returns a count of trials
  in which the `target` marble did or did not go through the exit.
- `noise_vs_failure` repeats `run_ideals_file` for various settings of the noise
  parameter in `model.py`, and saves a tab-separated table of results to a file.
  This is used to produce the noise vs. failure rate plots at the end of
  `code/R/omission.Rmd`.

## data

### empirical 

Raw data files of the three experiments reported in the paper. 

### simulations

Model simulations for Experiment 1 and Experiment 3. 

## figures 

### diagrams

Diagrams illustrating the experiment setup, and how the model works. 

### experiment_slides

Html slides and figures for Experiments 1-3 which were run via qualtrics. 

### plots 

Results plots as shown in the paper. 

## videos 

Video clips from each experiment in `.swf` and `.mov` format. 

