# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 12:48:15 2018

@author: Marcos
@coauthor: Vall
"""

import fwp_lab_instruments as ins
import fwp_pyaudio as fwp
import fwp_save as sav
import matplotlib.pyplot as plt
import numpy as np
import os, rms
import pyaudiowave as paw
import wavemaker as wmaker

#%% Read an write in two channels using generators to avoid signal cutoff

#Some configurations
after_record_do = fwp.AfterRecording(savewav = False, showplot = True,
                                     saveplot = False, savetext = False)                                     
duration = .5
nchannelsrec = 2
nchannelsplay = 2
signal_freq = 400

#A square and a sine wave
seno1 = wmaker.Wave('sine', frequency=signal_freq)
seno2 = wmaker.Wave('sine',frequency=signal_freq*2)
cuadrada = wmaker.Wave('square',frequency=signal_freq)
fourier_sq = wmaker.Fourier('square', frequency=signal_freq, order=2)

#Create signal to play
signalmaker = paw.PyAudioWave(nchannels=nchannelsplay)
signal_generator = signalmaker.generator_setup(seno1)
#NOTE: to write two different signals in two channels use tuples: (wave1,wave2)

thesignal = fwp.play_rec(signal_generator, 
                          recording_duration=duration,
                          nchannelsrec=nchannelsrec,
                          after_recording=after_record_do)

#%% Example of just_play

duration = 5
nchannelsplay = 2
signal_freq = 2000

#A square and a sine wave
seno1 = wmaker.Wave('sine', frequency=signal_freq)
seno2 = wmaker.Wave('sine', frequency=signal_freq*1.5)
seno3 = wmaker.Wave('sine', frequency=signal_freq, amplitude=.0)
suma = wmaker.Wave('sum', 
                   frequency=np.array((1, 1.25, 1.5, 2)) * signal_freq)
cuadrada = wmaker.Wave('square',frequency=signal_freq)
cuadrada2 = wmaker.Wave('square',frequency=signal_freq*10)
fourier = wmaker.Fourier('square', frequency=signal_freq, order=15)

#Create signal to play
signalmaker = paw.PyAudioWave(nchannels=nchannelsplay)
signal_generator = signalmaker.generator_setup((seno1, seno3), duration=duration)

fwp.just_play(signal_generator)

#%% Frequency sweep using generators

freq_start = 50
freq_stop = 22000
freq_step = 50

# Some configurations
after_record_do = fwp.AfterRecording(savewav = False, showplot = False,
                                     saveplot = False, savetext = True) 
nchannelsrec = 2
nchannelsplay = 2 # Cause of cable issues
name = 'Freq_Sweep'

seno = wmaker.Wave('sine') # Default frequency and amplitude.
signalmaker = paw.PyAudioWave(nchannels=nchannelsplay) # Default srate

# Frequencies and durations
frequencies = np.arange(freq_start, freq_stop, freq_step)
#durations = np.array([100/freq for freq in frequencies]) # 100 periods
duration = 50/frequencies[0] #play 50 periods of slowest wave
durations = [duration] * len(frequencies)

# If non existent, create directory to save to
savedir = sav.new_dir(os.path.join(os.getcwd(), 'Measurements', name))
filename = os.path.join(savedir, name)
makefile = lambda freq : '{}_{:.0f}_Hz'.format(filename, freq)

signalrms = []

for freq, dur in zip(frequencies, durations):
    
    # Set up stuff for this frequency
    seno.frequency = freq
    signal_to_play = signalmaker.generator_setup(seno)
    after_record_do.filename = makefile(freq)
    
    # Play, record and process
    thesignal = fwp.play_rec(
                        signal_to_play, 
                        recording_duration=dur,
                        nchannelsrec=nchannelsrec,
                        after_recording=after_record_do)
    
    signalrms.append(rms.rms(thesignal))

signalrms = np.array(signalrms)
signaldec = 10*np.log10(signalrms/max(signalrms))

plt.figure()
plt.plot(frequencies, signaldec, 'b-')
plt.ylabel('Decibels')
plt.xlabel('Frequency (Hz)')
plt.grid()
plt.show() 

sav.saveplot('{}_Plot.pdf'.format(filename))
sav.savetext(
        np.transpose(np.array([frequencies, signalrms, signaldec])),
        '{}_Data.txt'.format(filename))

#%% Calibrate playing

amp_start = 1
amp_stop = .05
amp_step = -0.05

freq = 400

port = 'USB0::0x0699::0x0363::C102220::INSTR'

name = 'Cal_Play_{:.0f}_Hz'.format(freq)
after_record_do = fwp.AfterRecording(savetext = True)

osci = ins.Osci(port=port)
#seno = wmaker.Wave('sine', frequency=freq)
signalmaker = paw.PyAudioWave(nchannels=2)

savedir = sav.new_dir(os.path.join(os.getcwd(), 'Measurements', name))
filename = os.path.join(savedir, name)
makefile = lambda amp: '{}_{:.2f}'.format(filename, amp)

amplitude = np.arange(amp_start, amp_stop, amp_step)
amp_osci = []

def measure():
    result_left = osci.measure('pk2', 1, print_result=True)
    result_right = osci.measure('pk2', 2, print_result=True)
    return result_left, result_right

for amp in amplitude:
    
    seno = wmaker.Wave('sine', frequency=freq, amplitude=amp)
    #seno.amplitude = amp #update signals ampitude
    signal_to_play = signalmaker.generator_setup((seno,seno), duration=1 ) 
    
    result = fwp.just_play_NB(signal_to_play, measure, wait_time=.3)
    amp_osci.append(list(result))

amp_osci = np.array(amp_osci)
osci.osci.close()

plt.figure()
plt.plot(amplitude, amp_osci, 'o')
plt.xlabel("Factor de amplitud")
plt.ylabel("Amplitud real (Vpp)")
plt.legend(["Izquierda","Derecha"])
plt.grid()
plt.show()

data = np.array([amplitude, amp_osci[:,0], amp_osci[:,1]]).T
sav.saveplot('{}_Plot.pdf'.format(filename))
sav.savetext(data, '{}_Data.txt'.format(filename))

#%% Calibrate recording

amp_stop = 0 # Vpp
amp_step = -0.05
amp_start = 4.5

mic_attenuation = 15/(15+22)

freq = 2000
duration = 1

port = 'USB0::0x0699::0x0346::C036492::INSTR'

nchannelsrec = 2
samplerate = 44100
name = 'Cal_Rec_{:.0f}_Hz'.format(freq)
after_record_do = fwp.AfterRecording(savetext = True, showplot=False)

gen = ins.Gen(port=port, nchannels=1)

savedir = sav.new_dir(os.path.join(os.getcwd(), 'Measurements', name))
filename = os.path.join(savedir, name)
makefile = lambda amp: '{}_{:.2f}'.format(filename, amp)

amplitude = np.arange(amp_start, amp_stop, amp_step)

gen.re_config_output(1, frequency=freq) # 1 output, 2 audio recording CH

amp_rec = []
                  
for amp in amplitude:
    
    after_record_do.filename = makefile(amp)
    
    gen.output(True, 1, amplitude=amp)
    
    signal_rec = fwp.just_rec(duration,
                              nchannelsrec=nchannelsrec,
                              after_recording=after_record_do)
    
    signal_rec = fwp.decode(signal_rec, nchannelsrec)
    
    amp_rec.append([max(signal_rec[:,0])-min(signal_rec[:,0]), # Left
                    max(signal_rec[:,1])-min(signal_rec[:,1])]) # Right

gen.output(0)
gen.gen.close()

amp_rec = np.array(amp_rec)

plt.figure()
plt.plot(amplitude*mic_attenuation, amp_rec, 'o')
plt.xlabel("Amplitud real (Vpp)")
plt.ylabel("Factor de amplitud (pp)")
plt.grid()
plt.legend(["Izquierda","Derecha"])
plt.show()

data = np.array([amplitude*mic_attenuation, amp_rec[:,0], amp_rec[:,1]]).T
sav.saveplot('{}_Plot.pdf'.format(filename))
sav.savetext(data, '{}_Data.txt'.format(filename))

#plt.figure()
#plt.title("Izquierda")
#plt.xlabel("Tiempo (s)")
#plt.ylabel("Señal (V)")
#for amp in amplitude:
#    loc_data = np.loadtxt(makefile(amp)+'.txt')
#    plt.plot(loc_data[:,0])
#    plt.legend(amplitude)
#
#plt.figure()
#plt.title("Izquierda")
#plt.xlabel("Tiempo (s)")
#plt.ylabel("Señal (V)")
#for amp in amplitude:
#    loc_data = np.loadtxt(makefile(amp)+'.txt')
#    plt.plot(loc_data[:,1])
#    plt.legend(amplitude)
#    

#%% Get a diode's IV curve

# PARAMETERS

resistance = 1e3 # ohms
r1 = 1e6
r2 = 5.75e6

amp = 1 # between 0 and 1
freq = 400 # hertz
duration = 1 #in seconds

nchannelsplay = 2
nchannelsrec = 2
samplerate = 44100

name = 'Diode_IV_{:.0f}_Hz_{:.2f}'.format(freq, amp)
after_record_do = fwp.AfterRecording(showplot = True, savetext = True)

# CODE --> ¡OJO! FALTA CALIBRACIÓN

signalmaker = paw.PyAudioWave(nchannels=nchannelsplay,
                              samplingrate=samplerate)

seno = wmaker.Wave('sine', frequency=freq)
signal_to_play = signalmaker.generator_setup(seno)

savedir = sav.new_dir(os.path.join(os.getcwd(), 'Measurements', name))
filename = os.path.join(savedir, name)
after_record_do.filename = filename

signal_rec = fwp.play_rec(signal_to_play, 
                           duration,
                           nchannelsrec=nchannelsrec,
                           after_recording=after_record_do)

if after_record_do.showplot:
    
    chL = signal_rec[:,0]
    chR = signal_rec[:,1]
    
    V0 = (r1 + r2)/r1 * chR
    
    V = V0 + chL
    I = chL/resistance    
    
    plt.figure()
    plt.plot(V, I, '.')
    plt.xlabel("Voltaje V")
    plt.ylabel("Corriente I")
    plt.grid()
    
#    sav.saveplot('{}_Plot.pdf'.format(filename))
#    sav.savetext(np.transpose(np.array([V, I])),
#                 '{}_Data.txt'.format(filename))
