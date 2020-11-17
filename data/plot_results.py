#!/usr/bin/python

import sys

import pandas as pd
import matplotlib.pyplot as plt

# A quick script to visualize the results from the csv file produced by the pv_simulator

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('Usage example: plot_results.py results.csv')
    else:
        try:
            df = pd.read_csv(sys.argv[1], index_col=0)

            fig, axes = plt.subplots(
                nrows=3, ncols=1, sharex=True, figsize=(16, 10))

            df.meter_power.plot(
                ax=axes[0], grid='both', title='Home Consumption', ylabel='[W]', color='r')
            df.pv_power.plot(
                ax=axes[1], grid='both', title='PV Production', ylabel='[W]', color='g')
            df.sum_power.plot(
                ax=axes[2], grid='both', title='Sum Power', ylabel='[W]', xlabel='Time', color='b')

            plt.savefig(sys.argv[1].split('.csv')[0] + '.png')
            plt.show()
        except Exception as e:
            print(e)
