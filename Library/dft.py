# -*- coding: utf-8 -*-
"""
Created on Tue May 22 23:39:01 2018

@author: Grenceng
"""
import math
import numpy as np
from scipy.fftpack import fft, ifft

def dftModel(x, w, N):
    hN = (N/2)+1
    hM1 = int(math.floor((w.size+1)/2))
    hM2 = int(math.floor(w.size/2))
    fftbuffer = np.zeros(N)
    y = np.zeros(x.size)
    #----analysis--------
    xw = x*w
    fftbuffer[:hM1] = xw[hM2:]
    fftbuffer[-hM2:] = xw[:hM2]
    X = fft(fftbuffer)
    absX = abs(X[:hN])
    absX[absX<np.finfo(float).eps] = np.finfo(float).eps
    mX = 20 * np.log10(absX)
    pX = np.unwrap(np.angle(X[:hN]))
    #-----synthesis-----
    Y = np.zeros(N, dtype = complex)
    Y[:hN] = 10**(mX/20) * np.exp(1j*pX)
    Y[hN:] = 10**(mX[-2:0:-1]/20) * np.exp(-1j*pX[-2:0:-1])
    fftbuffer = np.real(ifft(Y))                            # compute inverse FFT
    y[:hM2] = fftbuffer[-hM2:]                              # undo zero-phase window
    y[hM2:] = fftbuffer[:hM1]
    return y

def dftAnal(x, w, N):
    hN = (N/2)+1                                            # size of positive spectrum, it includes sample 0
    hM1 = int(math.floor((w.size+1)/2))                     # half analysis window size by rounding
    hM2 = int(math.floor(w.size/2))                         # half analysis window size by floor
    fftbuffer = np.zeros(N)                                 # initialize buffer for FFT
    w = w / sum(w)                                          # normalize analysis window
    xw = x*w                                                # window the input sound
    fftbuffer[:hM1] = xw[hM2:]                              # zero-phase window in fftbuffer
    fftbuffer[-hM2:] = xw[:hM2]        
    X = fft(fftbuffer)                                      # compute FFT
    absX = abs(X[:hN])                                      # compute ansolute value of positive side
    absX[absX<np.finfo(float).eps] = np.finfo(float).eps    # if zeros add epsilon to handle log
    mX = 20 * np.log10(absX)                                # magnitude spectrum of positive frequencies in dB         
    pX = np.unwrap(np.angle(X[:hN]))                        # unwrapped phase spectrum of positive frequencies
    return mX, pX

def dftSynth(mX, pX, M):
    hN = mX.size                                            # size of positive spectrum, it includes sample 0
    N = (hN-1)*2                                            # FFT size
    hM1 = int(math.floor((M+1)/2))                          # half analysis window size by rounding
    hM2 = int(math.floor(M/2))                              # half analysis window size by floor
    fftbuffer = np.zeros(N)                                 # initialize buffer for FFT
    y = np.zeros(M)                                         # initialize output array
    Y = np.zeros(N, dtype = complex)                        # clean output spectrum
    Y[:hN] = 10**(mX/20) * np.exp(1j*pX)                    # generate positive frequencies
    Y[hN:] = 10**(mX[-2:0:-1]/20) * np.exp(-1j*pX[-2:0:-1]) # generate negative frequencies
    fftbuffer = np.real(ifft(Y))                            # compute inverse FFT
    y[:hM2] = fftbuffer[-hM2:]                              # undo zero-phase window
    y[hM2:] = fftbuffer[:hM1]
    return y