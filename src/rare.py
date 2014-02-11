#!/usr/bin/env python
'''Tool to generate computationally-rarefied graphs kmer spectra'''

import numpy as np
import matplotlib.pyplot as plt
import sys, os
import scipy.stats
from optparse import OptionParser

def fract(aa, epsilon, threshold):
    '''Evaluates the fraction of theoretically-subsampled spectra
    above a specified threshold.  Dataset abundance is attenuated by
    the factor epsilon.  Returns a float.  aa is a two-column abudnance
    table, epsilon and threshold are floats.'''
    print "E", epsilon, "T", threshold
    xr = aa[:, 0]
    xn = aa[:, 1]
    NO = np.sum(xn * xr)
    p = 0.0
    smallr = xr * epsilon
    for i in range(len(xr)):
        if smallr[i] > 10 * threshold:
            interim = float(xn[i]*xr[i])
        elif smallr[i] < threshold / 10:
            interim = 0
        else:
            interim = float(xn[i] * xr[i]) * (1 - scipy.stats.poisson.cdf(
                threshold + 0.5, smallr[i])) / (1 - scipy.stats.poisson.cdf(
                    0.5, smallr[i]))
        if not np.isnan(interim):
            p += interim
    return p / NO

def calc_resampled_fraction(aa, samplefracs, thresholds):
    '''calculate 2D array of return value of fract by evaluating it
    for each fraction in samplefracs and each threshold in thresholds.
    Returns 2d matrix sith shape = len(samplefracs), len(thresholds)
    aa must be 2d ndarray
    '''
    assert aa.shape[1] == 2
    matrix = np.zeros((len(samplefracs), len(thresholds)))
    for i, frac in enumerate(samplefracs):
        for j, threshold in enumerate(thresholds):
            dummy = fract(aa, frac, threshold)
            matrix[i][j] = dummy
    return matrix

def plotme(b, label, color=None, thresholdlist=None, numplots=4):
    '''performs calculations and calls graphing routines,
    given spectra'''
# define range of subsamples
    N = np.sum(b[:, 0] * b[:, 1])
    samplefractions = 10**np.arange(2, 11, .5)  / N  # CHEAP
    samplefractions = 10**np.arange(2, 11, .1)  / N
# Throw away unecessary samples
    samplefractions = np.hstack((samplefractions[samplefractions < 1], 1))
    if thresholdlist == None:
        thresholdlist = [1]

    matrix = calc_resampled_fraction(b, samplefractions, thresholdlist)
    effort = N * samplefractions

    pex2 = np.hstack((effort[0], effort, effort[-1]))
    pex = effort
    for i in range(matrix.shape[1]):
        aug2 = np.hstack((0, matrix[:, i], 0))
        aug = matrix[:, i]
        lab = label + " " + str(thresholdlist[i])
        if SHADED == 0:
            plt.semilogx(pex, aug, "-", label=lab, color=color)
        else:
            plt.subplot(numplots, 1, n + 1)
            plt.semilogx(pex, aug, "-", label=lab, color=color)
            plt.fill(pex2, aug2, "k", alpha=0.2)
            plt.title(label)
#            label=str(thresholdlist[i]))
#        plt.fill(pex, aug, "k", alpha=0.2)
    plt.ylim((0, 1))
    plt.xlim((1E4, 1E11))
    if SHADED == 0 or n == 3:
        plt.xlabel("Sequencing effort (bp)")
        plt.legend(loc="upper left")
    else:
        frame1 = plt.gca()
        frame1.axes.get_xaxis().set_ticks([])
    if SHADED == 0 or n == 2 or 1:
        plt.ylabel("Fraction of data")
    plt.tight_layout()
    return()

if __name__ == "__main__":
    PARSER = OptionParser("rare.py -- rarefy kmer spectra")
    PARSER.add_option("-i", "--interactive", dest="interactive",
         action="store_true", default=False,
         help="interactive mode--draw window")
    PARSER.add_option("-l", "--list", dest="filelist", default=None,
         help="file containing list of targets and labels")
    (OPTS, ARGS) = PARSER.parse_args()
    SHADED = 1
    n = 0
    COLORS = ["b", "g", "r", "c", "y", "m", "k", "BlueViolet",
            "Coral", "Chartreuse", "DarkGrey", "DeepPink", "LightPink"]
# construct range of thresholds, calculate threshold fraction curves
# not lightning fast but should be
    listofthresholds = [1, 3.3, 10, 33, 100, 330, 1000, 3300, 10000]
    listofthresholds = 10**np.arange(0, 4.5, 0.5)
    listofthresholds = [1]
    listofthresholds = [1, 3, 10, 30]

    if OPTS.filelist:
        listfile = OPTS.filelist
        assert os.path.isfile(listfile), "File {} does not exist".format(
             listfile)
        IN_FILE = open(listfile, "r")
        for line in IN_FILE:
            if line[0] != "#":
                a = line.strip().split("\t")
                if len(a[0]) > 0:
                    if len(a) == 1:
                        a.append(a[0])
                    sys.stderr.write("%s  %s \n" % (a[0], a[1]))
                    filename = a[0]
                    spectrum = np.loadtxt(filename)
                    plotme(spectrum, label=a[1], color=COLORS[n],
                        thresholdlist=listofthresholds)
                    n = n + 1
#        plt.legend(loc="upper left")
        plt.savefig(listfile + ".rare.png")
    else:
        for v in ARGS:
            print v
            filename = v
            spectrum = np.loadtxt(filename)
            plotme(spectrum, filename, thresholdlist=listofthresholds,
               color=COLORS[n])
            n = n + 1
#        plt.legend(loc="upper left")
        print "Warning! printing graphs in test.png!"
        plt.savefig("test.png")
