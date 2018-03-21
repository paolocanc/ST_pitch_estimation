
"pitch and voiced/unvoiced estimation"

##The idea behind this script is implementing different pitch estimation methods
##in order to compare the performances of them in terms of voiced/unvoiced recognition,
##gross voiced error and MSE of fine errors.

from __future__ import print_function, division
import codecs

# -*- coding: utf8 -*-

import os
import numpy as np
from scipy.io import wavfile
from scipy import signal
from scipy.signal import butter, lfilter
from scipy.signal import freqs
from scipy.signal import correlate, kaiser

__author__ = "Paolo Cancello, starting code from  https://github.com/jarfo/st1, by Jose A. R. Fonollosa"


eps=0.0000000001

#LPF implementation, modfying the BPF from http://scipy.github.io/old-wiki/pages/Cookbook/ButterworthBandpass
def butter_lowpass(cutOff, fs, order):
    nyq = 0.5 * fs
    normalCutoff = cutOff / nyq
    b, a = butter(order, normalCutoff, btype='low', analog = True)
    return b, a

def butter_lowpass_filter(frame, cutOff, fs, order):
    b, a = butter_lowpass(cutOff, fs, order=order)
    y = lfilter(b, a, frame)
    return y


#Cepstrum implementation function 
def cepstrum_function(frame,sfreq):

    spectrum = np.fft.rfft(frame)
    spectrum[spectrum == 0] = eps
    log_spectrum = np.log(np.abs(spectrum**2))
    cep = np.fft.irfft(log_spectrum)

    return cep


def autocorr_method(frame,  sfreq):
    """Estimate pitch using autocorrelation
    """
    # Calculate autocorrelation using scipy correlate
    frame = frame.astype(np.float)
    frame -= frame.mean()
    amax = np.abs(frame).max() 
    if amax > 0:
        frame /= amax
       
    else:
        return 0

    corr = correlate(frame, frame) 
    
    # keep the positive part of the frequency range
    corr = corr[len(corr)//2:]
    
    # Find the first minimum
    dcorr = np.diff(corr) #differenza: valore successivo - valore attuale
    
    rmin = np.where(dcorr > 0)[0] 
    
    if len(rmin) > 0:
        rmin1 = rmin[0]      
    
    else:
        return 0

    # Find the next peak
    peak = np.argmax(corr[rmin1:]) + rmin1
    rmax = corr[peak]/corr[0]
    f0 = sfreq / peak

    #voiced/unvoiced
    if rmax > 0.5 and f0 > 50 and f0 < 400:
        return f0
    else:
        return 0;


def autocorr_LPF_method(frame, sfreq):
    """Estimate pitch using autocorrelation
    """
    #Filter parameters
    cutOff = 550
    fs = sfreq
    order = 20 
    windowed = butter_lowpass_filter(frame, cutOff, fs, order)
    
    # Calculate autocorrelation using scipy correlate
    windowed = windowed.astype(np.float) 
    windowed -= windowed.mean()
    amax = np.abs(windowed).max()
    if amax > 0:
        windowed /= amax 
       
    else:
        return 0

    corr = correlate(windowed, windowed)
    
    # keep the positive part
    corr = corr[len(corr)//2:]

    # Find the first minimum
    dcorr = np.diff(corr)
    rmin = np.where(dcorr > 0)[0]
    if len(rmin) > 0:
        rmin1 = rmin[0]
    else:
        return 0

    # Find the next peak
    peak = np.argmax(corr[rmin1:]) + rmin1
    rmax = corr[peak]/corr[0]
    if peak == 0:
        f0 = eps
    else:
        f0 = sfreq / peak

    #voiced/unvoiced
    if rmax > 0.5 and f0 > 50 and f0 < 400:
        return f0
    else:
        return 0;


    
#Cepstrum function
def cepstrum_method(frame,sfreq):

    #Filter parameters
    cutOff = 700
    fs = sfreq
    order = 20

    windowed = butter_lowpass_filter(frame, cutOff, fs, order)
    windowed = windowed.astype(np.float)
    windowed -= windowed.mean()
    amax = np.abs(windowed).max()
    
    if amax > 0:
            windowed /= amax
    else:
            return 0

    cep = cepstrum_function(windowed,sfreq)

    corr = correlate(cep, cep) 
    
    # keep the positive part of the frequency range
    corr = corr[len(corr)//2:]

    #definition of the observation window
    Fmin=50
    Fmax=700

    minimum =int(sfreq/Fmax)
    maximum =int(sfreq/Fmin)

    peak = np.argmax(corr[minimum:maximum]) + minimum
    
    if  peak == 0:
        f0 = eps
    else:
        f0= sfreq / peak

    if  f0 > 50 and f0 < 400:
            return f0
    else:
            return 0;        

def which_method(frame, sfreq, method):
    if(method == "autocorrelation"):
        return(autocorr_method(frame, sfreq))
    elif(method == "cepstrum"):
        return(cepstrum_method(frame, sfreq))
    elif(method == "autocorrelation_LPF"):
        return(autocorr_LPF_method(frame, sfreq))
    else:
        return(autocorr_method(frame, sfreq))


def wav2f0(options, gui):
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
                    f0 = which_method(frame, sfreq, options.method)
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
    optparser.add_option(
        '-m', '--method', type='string', default='autocorr',
        help='available methods: autocorrelation; autocorrelation_LPF; cepstrum. Eligible by writing themafter the -m')

    options, args = optparser.parse_args()

    if len(args) == 0:
        print("No FILELIST provided")
        optparser.print_help()
        exit(-1)

    main(options, args)
    
