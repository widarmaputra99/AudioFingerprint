# -*- coding: utf-8 -*-
"""
Created on Sat May 26 00:57:15 2018
@author: Grenceng
"""

import os, sys
import cPickle
import numpy as np
from scipy.io.wavfile import read
import warnings
warnings.filterwarnings("ignore")
import time
from scipy.signal import get_window
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Library/'))
import stft
import peakdetect
import pandas as pd

from Tkinter import *
import tkMessageBox as msgbox
import tkFileDialog
import scipy as scp
from PIL import Image, ImageTk
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import style
style.use('ggplot')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')
import cv2



class Main:
    def __init__(self, parent, title):
        self.parent = parent
        self.parent.title(title)
        self.parent.config(background="#d7efea")
        self.komponen()
        self.path = ""
        global source, file_paths, models, speakers
        #path to training data
        source   = "pupuh_set/"
        modelpath = "pupuh_models_04/"
        test_file = "pupuh_set_test.txt"    
        file_paths = open(test_file,'r')
        
        gmm_files = [os.path.join(modelpath,fname) for fname in os.listdir(modelpath) if fname.endswith('.gmm')]
        
        #Load the Gaussian gender Models
        models    = [cPickle.load(open(fname,'r')) for fname in gmm_files]
        speakers   = [fname.split("/")[-1].split(".gmm")[0] for fname in gmm_files]
        
        
    #GUI
    def resizeImg(self, path):
        img = cv2.imread(path)
        img = cv2.resize(img,(800,200))
        cv2.imwrite(path, img)
    
    def komponen(self):
        self.resizeImg("kosong.png")
        self.TimeDomImg = Image.open("kosong.png")
        self.TimeDomImg = ImageTk.PhotoImage(self.TimeDomImg)
        self.SpectrogramImg = Image.open("kosong.png")
        self.SpectrogramImg = ImageTk.PhotoImage(self.SpectrogramImg)
        self.FreqDomImg = Image.open("kosong.png")
        self.FreqDomImg = ImageTk.PhotoImage(self.FreqDomImg)
        self.AllFreqDomImg = Image.open("kosong.png")
        self.AllFreqDomImg = ImageTk.PhotoImage(self.AllFreqDomImg)
        
        self.opFrame = Frame(self.parent, bg="#d7efea")
        self.opFrame.grid(row=0, column=0,sticky=N)
        self.inputPupuhLbl = Label(self.opFrame, fg="black", text="Input Pupuh",
                                   bg="#d7efea")
        self.inputPupuhLbl.grid(row=0, column=0, padx=5, pady=4, sticky=W)
        self.browseBtn = Button(self.opFrame, text="Browse", command=self.browseWav,
                                width=6, height=1, bg="#e5efd7")
        self.browseBtn.grid(row=0, column=1, padx=3, pady=4)
        self.FnameTxt = StringVar()
        self.inputPupuhEnt = Entry(self.opFrame, width=20, bd=2, textvariable=self.FnameTxt)
        self.inputPupuhEnt.grid(row=0, column=2, padx=3, pady=4)
        self.FnameTxt.set("Belum Ada Pupuh")
        self.WSizeTxt = StringVar()
        self.windowSizeEnt = Entry(self.opFrame, width=15, bd=2, textvariable=self.WSizeTxt)
        self.windowSizeEnt.grid(row=1, column=0, padx=5, sticky=W)
        self.WSizeTxt.set("Window Size")
        self.OvlSizeTxt = StringVar()
        self.overlapSizeEnt = Entry(self.opFrame, width=15, bd=2, textvariable=self.OvlSizeTxt)
        self.overlapSizeEnt.grid(row=1, column=1, columnspan=2, padx=3, sticky=W)
        self.OvlSizeTxt.set("Overlapping Size")
        self.PTreshTxt = StringVar()
        self.peakTresholdEnt = Entry(self.opFrame, width=15, bd=2, textvariable=self.PTreshTxt)
        self.peakTresholdEnt.grid(row=1, column=3, padx=3, sticky=W)
        self.PTreshTxt.set("Peak Treshold")
        self.proccessBtn = Button(self.opFrame, width=10, text="Proccess", bg="#e5efd7",
                                  command=self.proses)
        self.proccessBtn.grid(row=2, column=3, padx=3, sticky=W)
        
        
        self.plotFrame = Frame(self.parent, bg="#d7efea")
        self.plotFrame.grid(row=1, column=0,sticky=N)
        self.detAsLbl = Label(self.plotFrame, fg="black", text="Detected As",
                              bg="#d7efea")
        self.detAsLbl.grid(row=0, column=0, columnspan=8, pady=2, sticky=N)
        self.resultLbl = Label(self.plotFrame, text="none", bg="#d7efea")
        self.resultLbl.grid(row=1, column=0, columnspan=8, pady=3,sticky=N)
        self.logLikeLbl = Label(self.plotFrame, fg="black", text="Log likelihood = ",
                                bg="#d7efea")
        self.logLikeLbl.grid(row=2,column=0,columnspan=4, padx=3, sticky=E)
        self.scoreLbl = Label(self.plotFrame, width=20, bd=2, text="-", bg="#d7efea")
        self.scoreLbl.grid(row=2, column=4, columnspan=4, sticky=W)
        self.timeDomLbl = Label(self.plotFrame,fg="black", text="Time Domain",
                                bg="#d7efea")
        self.timeDomLbl.grid(row=3, column=0, pady=3, padx=4, sticky=W)
        self.timeDomPlt = Label(self.plotFrame, width=500, height=200, 
                                image=self.TimeDomImg, bg="#4ae056")
        self.timeDomPlt.grid(row=4, column=0, columnspan=4, padx=5)
        self.timeDomPlt.image = self.TimeDomImg
        self.spectrogramLbl = Label(self.plotFrame,fg="black", text="Magnitude Spectrogram",
                                bg="#d7efea")
        self.spectrogramLbl.grid(row=3, column=4, pady=3, padx=4, sticky=W)
        self.spectrogramPlt = Label(self.plotFrame, width=500, height=200, 
                                image=self.SpectrogramImg, bg="#4ae056")
        self.spectrogramPlt.grid(row=4, column=4, columnspan=4, padx=5)
        self.spectrogramPlt.image = self.SpectrogramImg
        self.freqDomLbl = Label(self.plotFrame,fg="black", text="Frequency Domain",
                                bg="#d7efea")
        self.freqDomLbl.grid(row=5, column=0, pady=3, padx=4, sticky=W)
        self.freqDomPlt = Label(self.plotFrame, width=500, height=200, 
                                image=self.FreqDomImg, bg="#4ae056")
        self.freqDomPlt.grid(row=6, column=0, columnspan=4, padx=5)
        self.freqDomPlt.image = self.FreqDomImg
        self.allFreqDomLbl = Label(self.plotFrame,fg="black", text="All Frequency Domain",
                                bg="#d7efea")
        self.allFreqDomLbl.grid(row=5, column=4, pady=3, padx=4, sticky=W)
        self.allFreqDomPlt = Label(self.plotFrame, width=500, height=200, 
                                image=self.AllFreqDomImg, bg="#4ae056")
        self.allFreqDomPlt.grid(row=6, column=4, columnspan=4, padx=5)
        self.allFreqDomPlt.image = self.AllFreqDomImg
        self.showPeakBtn = Button(self.plotFrame, width=10, text="Peak", bg="#e5efd7",
                                  command=self.showPeak)
        self.showPeakBtn.grid(row=7, column=1, pady=5)
        self.peakLbl = Label(self.plotFrame, fg="black", 
                             text="click the Peak button to show peak location")
        self.peakLbl.grid(row=7, column=3, columnspan=2, sticky=W)
        self.proTimeLbl = Label(self.plotFrame, fg="black", text="")
        self.proTimeLbl.grid(row=9, column=0, columnspan=4, sticky=W)
    
    def showPeak(self):
        peakfile = open("Peaks/peak.txt","w")
        for e in self.peakloc:
            peakfile.write("%s\n" % e)
        peakfile.close()
    
    def browseWav(self):
        self.path = tkFileDialog.askopenfilename()
        if len(self.path) > 0:
            filename = self.path.split("/")[-1]
            self.FnameTxt.set(filename)
    
    def generateNoise(self,length,rad):
        return np.random.randint(-rad,rad,length)
    def proses(self):
        if len(self.path) > 0:
            start_time = time.time()
            rates, audio = read(self.path)
            noise = self.generateNoise(audio.size,1)
            #audio += noise
            print audio
            newAudio = audio + noise
            print newAudio
            INT16_FAC = (2**15)-1
            INT32_FAC = (2**31)-1
            INT64_FAC = (2**63)-1
            norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
            newAudio = np.float32(newAudio)/norm_fact[newAudio.dtype.name]
            w = get_window('hamming',int(self.WSizeTxt.get()))
            H = int(float(self.WSizeTxt.get())*float(self.OvlSizeTxt.get()))
            N = 2048                #STFT rate
            mX, pX = stft.stftAnal(newAudio, rates, w, N, H)
            minimum = np.min(mX)
            maximum = np.max(mX)
            t = float(self.PTreshTxt.get())
            sebaran = np.arange(minimum, maximum)
            s_index = int(sebaran.size*(1-t))
            treshold = sebaran[-s_index]
            print "treshold:",treshold
            ploc = peakdetect.peakDetection(mX,treshold)
            
            #print "ploc:",ploc
            if ploc.size != 0:
                peak_loc = []
                for i in range(len(ploc)-1):
                    if ploc[i] != ploc[i+1]:
                        peak_loc.append(ploc[i])
                peak_loc.append(ploc[-1])
                peak_loc = np.array(peak_loc)
                #print peak_loc.size,"\n"
                vector   = mX[peak_loc]
                
                log_likelihood = np.zeros(len(models)) 
                
                for i in range(len(models)):
                    gmm    = models[i]  #checking with each model one by one
                    scores = np.array(gmm.score(vector))
                    log_likelihood[i] = scores.sum()
                
                winner = np.argmax(log_likelihood)
            self.resultLbl.config(text=speakers[winner])
            self.scoreLbl.config(text=np.max(log_likelihood))
            self.peakloc = peak_loc
            
            freqaxis = rates*np.arange(N/2)/float(N)
            loc = []
            for m in mX[peak_loc]:
                loc.append(np.argmax(m))
            Freq = freqaxis[loc]
            df = pd.DataFrame(Freq)
            df.to_excel("Frekuensi/Frekuensi Penyusun "+self.path.split("/")[-1].split(".")[0]+".xlsx", index=False)
            maxplotfreq = rates/8.82
            
            plt.figure(figsize=(12, 9))
            plt.plot(np.arange(newAudio.size)/float(rates), newAudio)
            plt.axis([0, newAudio.size/float(rates), min(newAudio), max(newAudio)])
            plt.ylabel('amplitude')
            plt.xlabel('time (sec)')
            plt.autoscale(tight=True)
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                                hspace = 0, wspace = 0)
            plt.savefig("Time Domain Testing Noise.png")
            self.resizeImg("Time Domain Testing Noise.png")
            self.TimeDomImg = Image.open("Time Domain Testing Noise.png")
            self.TimeDomImg = ImageTk.PhotoImage(self.TimeDomImg)
            self.timeDomPlt.config(image=self.TimeDomImg, width=500, height=200)
            self.timeDomPlt.image = self.TimeDomImg
            plt.close()
            N = 2048                                    #STFT rate
            numFrames = int(mX[:,0].size)
            frmTime = H*np.arange(numFrames)/float(rates)
            binFreq = rates*np.arange(N*maxplotfreq/rates)/N
            plt.pcolormesh(frmTime, binFreq, np.transpose(mX[:,:int(N*maxplotfreq/rates+1)]))
            #plt.xlabel('time (sec)')
            #plt.ylabel('frequency (Hz)')
            #plt.title('magnitude spectrogram')
            plt.autoscale(tight=True)
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                                hspace = 0, wspace = 0)
            plt.savefig("Spektrogram Frekuensi Testing Noise.png")
            self.resizeImg("Spektrogram Frekuensi Testing Noise.png")
            self.SpectrogramImg = Image.open("Spektrogram Frekuensi Testing Noise.png")
            self.SpectrogramImg = ImageTk.PhotoImage(self.SpectrogramImg)
            self.spectrogramPlt.config(image=self.SpectrogramImg, width=500, height=200)
            self.spectrogramPlt.image = self.SpectrogramImg
            plt.close()
            plt.plot(mX[peak_loc[0]])                   #menampilkan magnitude frequency di index peak_loc[0]
            #plt.xlabel('frequency (Hz)')
            #plt.ylabel('magnitude')
            plt.axhline(y=treshold)
            plt.autoscale(tight=True)
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                                hspace = 0, wspace = 0)
            plt.savefig("Frekuensi Domain Testing Noise.png")
            self.resizeImg("Frekuensi Domain Testing Noise.png")
            self.FreqDomImg = Image.open("Frekuensi Domain Testing Noise.png")
            self.FreqDomImg = ImageTk.PhotoImage(self.FreqDomImg)
            self.freqDomPlt.config(image=self.FreqDomImg, width=500, height=200)
            self.freqDomPlt.image = self.FreqDomImg
            plt.close()
            plt.plot(mX[peak_loc])
            #plt.xlabel('frequency (Hz)')
            #plt.ylabel('magnitude')
            plt.axhline(y=treshold)
            plt.autoscale(tight=True)
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                                hspace = 0, wspace = 0)
            plt.savefig("All Frekuensi Domain Testing Noise.png")
            self.resizeImg("All Frekuensi Domain Testing Noise.png")
            self.AllFreqDomImg = Image.open("All Frekuensi Domain Testing Noise.png")
            self.AllFreqDomImg = ImageTk.PhotoImage(self.AllFreqDomImg)
            self.allFreqDomPlt.config(image=self.AllFreqDomImg, width=500, height=200)
            self.allFreqDomPlt.image = self.AllFreqDomImg
            plt.close()
            end_time = time.time() - start_time
            self.proTimeLbl.config(text="Identifikasi berakhir dengan total waktu %s detik" 
                                   % end_time)
        else:
            print "belum ada pupuh diinput"
        
    def temp(self):
        # Read the test directory and get the list of test audio files 
        w_sizes = [256,512,1024,2048, 4096]
        ov_sizes = [0.25,0.5,0.75]
        tresholds = np.arange(1,10)*0.1
        paths = []
        for path in file_paths:
            path = path.strip()
            paths.append(path)
            
        for ind_w in range(len(w_sizes)):
            for ind_ov in range(len(ov_sizes)):
                for ind_t in range(len(tresholds)):
                    print "treshold rate =",tresholds[ind_t]
                    x = []                                         #list penampung data
                    for ind_p in range(len(paths)):
                        paths[ind_p] = paths[ind_p].strip()   
                        print paths[ind_p]
                        rates,audio = read(source + paths[ind_p])
                        
                        #Framing
                        framerate = rates                      #menentukan jumlah frame
                        frame = round(len(audio)/framerate)         #mengukur banyak data/frame
                        n_frames = 10                                   #jumlah frame yang diperiksa
                        time_jump = 5                              #lompatan waktu (detik)
                        a = 0                                       #index penunjuk frame
                        while a < len(audio):
                            f_data = audio[int(a):int(a+n_frames*framerate)]
                            f_time = np.arange(a,(a + framerate * n_frames))/float(framerate)
                            a += time_jump*rates
                            INT16_FAC = (2**15)-1
                            INT32_FAC = (2**31)-1
                            INT64_FAC = (2**63)-1
                            norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
                            f_data = np.float32(f_data)/norm_fact[f_data.dtype.name]
                            w = get_window('hamming',w_sizes[ind_w])
                            H = int(w_sizes[ind_w]*ov_sizes[ind_ov])
                            mX, pX = stft.stftAnal(f_data, rates, w, 2048, H)
                            minimum = np.min(mX)
                            maximum = np.max(mX)
                            t = float(self.PTreshTxt.get())
                            sebaran = np.arange(int(round(minimum)),int(round(maximum)))
                            s_index = int(sebaran.size*(1-t))
                            treshold = sebaran[-s_index]
                            ploc = peakdetect.peakDetection(mX,treshold)
                            if ploc.size != 0:
                                peak_loc = []
                                for i in range(len(ploc)-1):
                                    if ploc[i] != ploc[i+1]:
                                        peak_loc.append(ploc[i])
                                peak_loc.append(ploc[-1])
                                peak_loc = np.array(peak_loc)
                                #print peak_loc.size,"\n"
                                vector   = mX[peak_loc]
                                
                                log_likelihood = np.zeros(len(models)) 
                                
                                for i in range(len(models)):
                                    gmm    = models[i]  #checking with each model one by one
                                    scores = np.array(gmm.score(vector))
                                    log_likelihood[i] = scores.sum()
                                
                                winner = np.argmax(log_likelihood)
                                #print "score =",log_likelihood
                                #print "highest score =",np.max(log_likelihood)
                                #print "\tdetected as - ", speakers[winner]
                                #time.sleep(1.0)
                                x.append(paths[ind_p])
                                temp = str(np.min(f_time))
                                '''
                                k = temp.split('.')
                                l = k[0]+','+k[1]
                                '''
                                x.append(temp)
                                temp = str(np.max(f_time))
                                '''
                                k = temp.split('.')
                                l = k[0]+','+k[1]
                                '''
                                x.append(temp)
                                temp = str(np.max(log_likelihood))
                                k = temp.split('.')
                                l = k[0]+','+k[1]
                                x.append(l)
                                x.append(speakers[winner])
                    #time.sleep(2.0)
                    print "len x:",len(x)
                    x = np.array(x)
                    x = np.reshape(x,(len(x)/5,5))
                    print x,"\n\n"
                    time.sleep(2)
                    df = pd.DataFrame(x)
                    df.to_excel("test/Test_"+str(w_sizes[ind_w])+
                                "_"+str(ov_sizes[ind_ov])+"_"+str(tresholds[ind_t])+
                                ".xls", index=False)

#==================== MAIN ====================#
root = Tk()
Main(root,".::Audio Fingerprint - Shazam Pupuh::.")
root.mainloop()