from __future__ import print_function, division
import codecs

# -*- coding: utf8 -*-


"""
Simple pitch estimation
"""


import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate
from scipy.signal import medfilt




__author__ = "Jose A. R. Fonollosa"



def autocorr_method(frame,  sfreq):
    """Estimate pitch using autocorrelation
    """
    i = 0
    # Calculate autocorrelation using scipy correlate
    frame = frame.astype(np.float) #trasforma in float i valori dell'array frame
    frame -= frame.mean() #toglie dagli elementi di frame la media degli elementi dell'array
    amax = np.abs(frame).max() #salva in amax il valore assoluto massimo di frame
    if amax > 0:
        frame /= amax #divide i valori di frame per il valore assoluto masssimo
       
    else:
        return 0

    corr = correlate(frame, frame) #autocorrelation
    
    # keep the positive part of the frequency range
    corr = corr[len(corr)//2:]
    
    # Find the first minimum
    dcorr = np.diff(corr) #differenza: valore successivo - valore attuale


    
    rmin = np.where(dcorr > 0)[0] #salva le posizioni dei dcorr>0
    
    if len(rmin) > 0:
        rmin1 = rmin[0]  #salva la prima posizione dell'array in cui si trova la prima differenza >0
       
    
    else:
        return 0

    # Find the next peak
    peak = np.argmax(corr[rmin1:]) + rmin1
    
    rmax = corr[peak]/corr[0]
    f0 = sfreq / peak
    
    if rmax > 0.5 and f0 > 50 and f0 < 400:
        return f0
    else:
        return 0;

    


def wav2f0(options, gui):
    i = 0
    with open(gui) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            filename = os.path.join(options.datadir, line + ".wav")
            f0_filename = os.path.join(options.datadir, line + ".f0")
            print("Processing:", filename, '->', f0_filename)
            sfreq, data = wavfile.read(filename)
            with open(f0_filename, 'wt') as f0file:
                nsamples = len(data)
                # From miliseconds to samples
                ns_windowlength = int(round((options.windowlength * sfreq) / 1000))
                
                ns_frameshift = int(round((options.frameshift * sfreq) / 1000))
                
                ns_padding = int(round((options.padding * sfreq) / 1000))
                
                for ini in range(-ns_padding, nsamples - ns_windowlength + ns_padding + 1, ns_frameshift):
                    first_sample = max(0, ini)
                    last_sample = min(nsamples, ini + ns_windowlength)
                    frame = data[first_sample:last_sample]
                    
                    f0 = autocorr_method(frame, sfreq)
                    print(f0, file=f0file)
                  


def main(options, args):
    wav2f0(options, args[0])

if __name__ == "__main__":
    import optparse
    optparser = optparse.OptionParser(
        usage='python3 %prog [OPTION]... FILELIST\n' + str(__doc__))
    optparser.add_option(
        '-w', '--windowlength', type='float', default=32,
        help='windows length (ms)')
    optparser.add_option(
        '-f', '--frameshift', type='float', default=15,
        help='frame shift (ms)')
    optparser.add_option(
        '-p', '--padding', type='float', default=16,
        help='zero padding (ms)')
    optparser.add_option(
        '-d', '--datadir', type='string', default='data',
        help='data folder')

    options, args = optparser.parse_args()

    if len(args) == 0:
        print("No FILELIST provided")
        optparser.print_help()
        exit(-1)

    main(options, args)
    
