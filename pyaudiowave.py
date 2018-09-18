# -*- coding: utf-8 -*-
"""
A module containing a single class that takes in Wave objects from the wavemaker
module and outputs a variety of signals from the given wave(s).'''
"""
import numpy as np

#%% The class

class PyAudioWave:
    ''' A class which takes in a wave object and formats it accordingly to the
    requirements of the pyaudio module for playing. It includes two simple 
    methods that return a signal formated to play or a signal formated to plot,
    respectively.
    
    Pyaudio parameters required:
        samplingrate: (int). Sampling (or playback) rate
        buffersize: (int). Writing buffer size
        nchannels: (1 or 2). Number of channels.'''
        
    def __init__(self, samplingrate=44100, buffersize=1024, nchannels=1):
        
        self.sampling_rate = samplingrate
        self.buffer_size = buffersize
        self.nchannels = nchannels

#%% Some helper methods

    def create_time(self, wave, periods_per_chunk=1):
        ''' Creates a time arry for other functions tu use.'''
        
        period = 1/wave.frequency
        time = np.linspace(start = 0, stop = period * periods_per_chunk, 
                           num = period * periods_per_chunk * self.sampling_rate,
                           endpoint = False)
        return time
    
    def encode(self,signal):
        '''Formats signal for pyaudio stream. Deals with one- and two-channel 
        signals.'''
        
        if self.nchannels == 2:
            #Two channel signal requires some extra handling
            signal = np.transpose(np.array(signal))
        
        interleaved = signal.flatten()
        out_data = interleaved.astype(np.float32).tostring()
        return out_data
        
    def resolve_nchannels(self, wave, display_warnings):
        '''Resolve wave or wave tuple for given channel ammount. Return a tuple.'''
        
        if self.nchannels == 1:
            #If user passed one wave objects and requested single-channel signal:
            if not isinstance(wave,tuple):
                if display_warnings: print('Requested a one channel signal but provided more than one wave. Will precede using the first wave.')
                return (wave,)
        
        else:
            ''' Ahora mismo hay un probema de diseño con escrir en dos canales
            y loopear sobre un únic array, porque lo que se quiere escribir en
            los dos canales pede no tener frecuencias compatibles y una de
            ellas queda cortada en cada iteración. Para solucionarlo, habría 
            que rehacer play_callback para que llame a algo que le de una señal
            en cada iteración. Por ahora, devuelve los cachos cortados.'''
            
            #If user passed one wave object, but requested two-channel signal
            if not isinstance(wave,tuple): #should rewrite as warning
                if display_warnings: print('''Requested two channel signal, but only provided one wave object. Will write same signal in both channels.''')
                return (wave,wave)
          
            else: #should rewrite as warning
                if display_warnings: print('''Requested two channel signal. If frequencies are not compatible, second channel wave will be cut off.''')
    
        #If no correction was needed, return as input
        return wave
        
    def eval_wave(self, wave, time):
        '''Simple method evaluating the given wave(s) according to channels.'''
        #Could also be implemented as [wave[i] for i in range(nchannels)]
        if self.nchannels == 1:
            #list is used to have an array of shape (1,N), instad of (N,)
            signal = np.array([np.transpose(wave[0].evaluate(time))])
        else:
            signal = np.array([np.transpose(w.evaluate(time)) for w in wave])
            
        return signal
    
    def yield_a_bit(self, signal):
        '''Yield chunck of the given signal of lenght buffer_size. Signal 
        should be an array of shape (samples, nchannels).''' 
        #Since buffers_per_arrray might be smaller than 
        #len(signal)//self.buffer_size, I'll use the latter:
        for i in range(len(signal)//self.buffer_size):
            yield signal[:,self.buffer_size * i:self.buffer_size * (i+1)]
    
#%% The actual useful methods
            
    def write_signal(self, wave, periods_per_chunk=1, display_warnings=True):
        ''' Creates a signal the pyaudio stream can write (play). If signal is 
        two-channel, output is formated accordingly.'''
    
        #Adequate wave tuple to channels, create time, create signal and encode
        wave = self.resolve_nchannels(wave, display_warnings)
        time = self.create_time(wave[0], periods_per_chunk)  
        signal = self.eval_wave(wave, time)
        
        return self.encode(signal)
        
    
    def write_generator(self, wave, duration=None, buffers_per_array=100 , display_warnings=False):
        ''' Creates a generator to yield chunks of length buffer_size of the 
        generated wave for a total time equal to duration. If duration is
        None, it will generate samples forever.'''
        
        wave = self.resolve_nchannels(wave, display_warnings)
        #Get whole number of periods bigger than given buffer_size
        required_periods = self.buffer_size * wave[0].frequency // self.sampling_rate + 1
        
        #Create a time vector just greater than buffers_per_array*buffer_size
        time = self.create_time(wave[0],
                                periods_per_chunk = required_periods * buffers_per_array)
        signal = self.eval_wave(wave, time)
        yield_signal = signal
        
        #Handle different duration values:
        
        if duration is None:
            # Yield samples indefinitely
            while True:
                yield from self.yield_a_bit(yield_signal)
                last_place = len(yield_signal)//self.buffer_size
                yield_signal = np.append((yield_signal[last_place:],signal))
                        
        elif duration < len(signal) / self.sampling_frequency:
            total_length = duration * self.sampling_frequeny
            yield from self.yield_a_bit(signal[:total_length])
            yield signal[total_length:] #yield las bit
            
        else: #tal vez puede simplificarse la cuenta del range y ajustar el final de la duración
            iterations = duration * wave.frequency // (required_periods * buffers_per_array)
            for _ in range(iterations):
                yield from self.yield_a_bit(yield_signal)
                last_place = len(yield_signal)//self.buffer_size
                yield_signal = np.append((yield_signal[last_place:],signal))
            #Missing line to get exact duration
                
               
    def plot_signal(self, wave, periods_per_chunk=1):
        ''' Returns time and signal arrays ready to plot. If only one wave is
        given, output will be the same as write_signal, but will also return
        time. If a tuple of waves is given, output will be time and a list of
        the signal arrays.'''
        

        if not isinstance(wave,tuple):
            time = self.create_time(wave, periods_per_chunk)
            
            return time, wave.evaluate(time)
      
        else: 
            time = self.create_time(wave[0],periods_per_chunk)
            signal_list = [w.evaluate(time) for w in wave]
            
            return time, signal_list
        