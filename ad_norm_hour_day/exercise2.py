# -*- coding: utf-8 -*-

import datetime
import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from cycler import cycler

from pmmif import featherpmm

from gen import sim_dist, sim_week, add_actual

BLUE = '#204080'


def get_week():
    df = featherpmm.read_dataframe('data/week.feather').df
    return df.set_index('date')


def get_day():
    return featherpmm.read_dataframe('data/day.feather').df


def get_week_actual():
    df = featherpmm.read_dataframe('data/actual.feather').df
    return df.set_index('date')


def plot_ref_hour_of_day(df, save_path):
    """
    Saves an SVG plot to the path given, showing the distribution
    of values in df by hour of day.
    """
    bounds = list(range(1, 24))
    df['time_of_day_hour_bins'] = np.digitize(df.time, bounds)
    counts = df.groupby('time_of_day_hour_bins')['time'].count()
    plt.figure()
    counts.plot.bar(color=BLUE, title='Average Volume by Hour of Day')
    plt.savefig(save_path)


def plot_week(df, outpath):
    """
    Plots df as a line graph, saving result as SVG to output
    """
    plt.figure()
    df.plot.line(color=BLUE, title='Volume by Hour of Day, 7 days')
    plt.savefig(outpath)


def plot_actual_vs_expected(df, outpath):
    """
    Plots df as a line graph, saving result as SVG to output
    """
    plt.figure()
    plt.rc('axes', prop_cycle=(cycler('color', ['blue', 'orange'])))
    df.plot.line(title='Volume by Hour of Day, 7 days', figsize=(10, 4))
    plt.grid(b=True, which='both', color='0.80', linestyle='-')
    plt.ylim((0, 3000))
    plt.savefig(outpath)


def plot_actual_vs_limits(df, outpath):
    df['upper'] = np.maximum(df['expected'] * 1.5,
                             df['expected'] + 150)
    df['lower'] = np.minimum(df['expected'] * 0.67,
                             np.maximum(df['expected'] - 150, 0))
    del df['expected']

    plt.figure()
    fig, (ax0, ax1) = plt.subplots(nrows=2)
    plt.rc('axes', prop_cycle=(cycler('color', ['blue', 'red', 'green'])))
    df.plot.line(title='Volume by Hour of Day, 7 days', figsize=(10, 4))
    plt.grid(b=True, which='both', color='0.80', linestyle='-')
    plt.ylim((0, 3000))
    plt.savefig(outpath)


def detect_anomalies(df):
    df['upper'] = np.maximum(df['expected'] * 1.5,
                             df['expected'] + 150)
    df['lower'] = np.minimum(df['expected'] * 0.67,
                             np.maximum(df['expected'] - 150, 0))
    df['actual_min_ok'] = df['actual'] >= df['lower']
    df['actual_max_ok'] = df['actual'] <= df['upper']


def print_anomalies(df):
    print(df[np.logical_not(np.logical_and(df['actual_min_ok'],
                                           df['actual_max_ok']))])


def ensure_dir_exists(d):
    if not os.path.isdir(d):
        if os.path.exists(d):
            raise('Output directory %s exists but is not a directory' % d)
        else:
            os.mkdir(d)


def main():
    ensure_dir_exists('graphs')
    df_week_actual = get_week_actual()
    plot_actual_vs_expected(df_week_actual.copy(),
                            'graphs/week-actual-vs-expected.svg')
#    plot_actual_vs_limits(df_week_actual.copy(),
#                          'graphs/week-actual-vs-limits.svg')


if __name__ == '__main__':
    pd.set_option('display.width', 200)
    main()
