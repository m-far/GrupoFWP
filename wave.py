# -*- coding: utf-8 -*-
"""
Crea funciones
"""
import numpy as np
from scipy.signal import sawtooth, square
    
def create_sine(time, freq):
    """ Creates sine wave """
    wave =np.sin(2 * np.pi * time * freq)
    return wave        
    
def create_ramps(time, freq, type_of_ramp=1):
    """ Creates ascending and descending sawtooth wave,
    or a tringle wave, depending on the value of type_of_ramp.
    Used by create_sawtooth_up, create_sawtooth_down and 
    create_triangular."""

    wave = sawtooth(2 * np.pi * time * freq, type_of_ramp)
    return wave
    
def create_sawtooth_up(time, freq):
    """ Creates a sawtooth wave with ascending ramps"""
    wave = create_ramps(time ,freq, 1)
    return wave        

def create_sawtooth_down(time, freq):
    """ Creates a sawtooth wave with descending ramps"""
    wave = create_ramps(time, freq, 0)
    return wave        

def create_triangular(time, freq):
    """ Creates a triangular wave with symmetric ramps"""
    wave = create_ramps(time, freq, .5)
    return wave        
     
def create_square(time, freq):
    wave = square(2 * np.pi * time * freq)
    return wave
    
def create_custom(time, freq, custom_func):
    raise Exception('Not yet implemented.')
      
def given_waveform(input_waveform):
    switcher = {
        'sine': create_sine,
        'sawtoothup': create_sawtooth_up,
        'sawtoothdown': create_sawtooth_down  ,          
        'ramp': create_sawtooth_up, #redirects to sawtooth
        'triangular': create_triangular,
        'square': create_square,
        'custom': create_custom,
    }
    func = switcher.get(input_waveform,lambda: 'Invalid waveform.')
    return func
       

def function_creator(waveform, freq=400, duration=1, amp=1, samplig_freq=17000, *arg):
    """
    waveform: str
        String from list declaring type of function to use.
    freq: float
        frequency of signal in Hz. Default: 400HZ
    duration: float
        Sample length in seconds. Default: 1 second
    amp: float
        Amplitude a s a fraction of maximum aplitude. Default: 1
    sampling_freq: int
        Sampling frequency in Hz.
    """
    time = np.arange(samplig_freq * duration)/samplig_freq
    func = given_waveform(waveform)
    wave = func(time, freq) * amp
    return wave
    
def function_generator(waveform, freq=400, duration=None, amp=1,
                       periods_per_chunk=1, samplig_freq=17000, *arg):
    """
    waveform: str
        String from list declaring type of function to use.
    freq: float
        frequency of signal in Hz. Default: 400Hz.
    duration: float
        Sample length in seconds. If duration is None, it will yield
        samples indefinitely. Default: None.
    amp: float
        Amplitude a s a fraction of maximum aplitude. Default: 1.
    periods_per_chunk: int
        Amount of wave periods to include in each yield. Default: 1.
    sampling_freq: int
        Sampling frequency in Hz.
    """

    period = 1/freq
    time = np.arange(period * periods_per_chunk, step=1/samplig_freq) #time vector 1 period long
    func = given_waveform(waveform)
    wave = func(time, freq) * amp
    
    if duration is not None:
        for _ in range(duration//period): 
            yield wave
    else:
        while True: 
            yield wave


def frequency_sweep(freqs_to_sweep=np.arange(100,1000,10), amplitude=1, 
                   waveform='sine', duration_per_freq=1, 
                   silence_between_freq=0, sampling_freq=17000):
    """
    freqs_to_sweep: tuple or array-like
        If tuple: expects (start, stop, step) tuple and generates an array 
        using np.arrange. If array, size should be (n_freqs, ) and contain
        the frequency values to sweep in Hz. Default: sweeps from 100Hz to
        1000Hz every 10Hz.
    amp: float or array-like
        Amplitud of generated wave.  If array-like, length should be equal
        to ammount of frequency values to sweep. Default: 1.
    waveform: str
        Type of waveform to use. Can be 'sine', 'sawtoothup', 'sawtoothdown',
        'ramp', 'triangular', 'square' or 'custom'. Default: sine.
    duration_per_freq: float or array-like
        Duration of each frequency stretch in seconds. If array-like, length 
        should be equal to ammount of frequency values to sweep. 
        Default: 1 second.
    silence_between_freq: float or array-like
        Time to wait between each frequency in seconds. If array-like, length 
        should be equal to ammount of frequency values to sweep. 
        Default: 0 seconds.
    """
#    Crete frequency array, if necessary
    if isinstance(freqs_to_sweep,tuple):
        if not len(freqs_to_sweep)==3:
            raise ValueError('Tuple length must be 3 containing (start, stop, step).')
        freqs_to_sweep = np.arrange(freqs_to_sweep(0), freqs_to_sweep(1),
                                 freqs_to_sweep(2))
                                 
    N_freqs = len(freqs_to_sweep)#ammount of frequencies to sweep
    
    
#    Transform all variables that are not iterables to lists of correct length
    if isinstance(amplitude,float):
        amplitude = [amplitude] * N_freqs
        
    if isinstance(duration_per_freq,float):
        duration_per_freq = [duration_per_freq] * N_freqs
        
    if isinstance(silence_between_freq,float):
        silence_between_freq = [silence_between_freq] * N_freqs
    
    for freq, duration, amp, silence in zip(freqs_to_sweep,
                                            amplitude,
                                            duration_per_freq,
                                            silence_between_freq):
        wave = function_creator(waveform, freq, duration, amp, sampling_freq)
        yield wave
#%% Clase que genera ondas

class wave:
    '''Generates an object with a two methods: evaluate(time) and generate (not implemented).
    Has three atributes: waveform, frequency and amplitude. Waveform can be
    'sine', 'sawtoothup', 'sawtoothdown', 'ramp', 'triangular', 'square' or 
    'custom'. Default: sine.'''
    
    def __init__(self, waveform='sine', frequency=400, amplitude=1):
        self.frequency = frequency
        self.amplitude = amplitude
        self.waveform = given_waveform(waveform)
        
    def evaluate(self, time):
        '''Takes in an array-like object to evaluate the funcion in.'''
        wave = self.waveform(time, self.freq) * self.amp
        return wave
    
#    def generate(self, time, chunk_size):
        
#%% Clase que adecúa las ondas a pyaudio
      
def encode(signal):
import numpy as np

"""
Convert a 2D numpy array into a byte stream for PyAudio

Signal should be a numpy array with shape (chunk_size, channels)
"""
interleaved = signal.flatten()

# TODO: handle data type as parameter, convert between pyaudio/numpy types
out_data = interleaved.astype(np.float32).tostring()
return out_data
    
    
class SoundDeviceGenerator:
    
    def __init__(self, samplingrate=44000, buffer_size, nchannels=1):
        
        self.sampling_rate = samplingrate
        self.buffer_size = buffer_size
        self.nchannels = nchannels
    
    def create_signal(self,wave,periods_per_chunk):
        
        if self.nchannels == 1:
            period = 1/wave.frequency
            time = np.linspace(start = 0, stop = period * periods_per_chunk, 
                               num = period * periods_per_chunk * self.sampling_rate,
                               endpoint = False)
            return wave.evaluate(time)
        
        else:
            ''' Ahora mismo hay un probema de diseño con escrir en dos canales
            y loopear sobre un únic array, porque lo que se quiere escribir en
            los dos canales pede no tener frecuencias compatibles y una de
            ellas queda cortada en cada iteración. Para solucionarlo, habría 
            que rehacer play_callback para que llame a algo que le de una señal
            en cada iteración. Por ahora, devuelve los cachos cortados.'''
            
            if not isinstance(wave,tuple):
                print('''Requested two channel signal, but only provided one wave
                      object. Will write same signal in both channels.''')
                waves = (wave,wave)
          
            else: 
                print('''Requested two channel signal. If frequencies are not
                      compatible, second wave will be cut off.''')
            
            period = 1/waves[0].frequency
            time = np.linspace(start = 0, stop = period * periods_per_chunk, 
                           num = period * periods_per_chunk * self.sampling_rate,
                           endpoint = False)
            sampleslist = [np.transpose(waves[0].evaluate(time)),
                           np.transpose(waves[1].evaluate(time))] # me armo una tupla que tenga en cada columna lo que quiero reproducir por cada canal
                
            samplesarray=np.transpose(np.array(sampleslist)) # la paso a array, y la traspongo para que este en el formato correcto de la funcion de encode
            
            return encode(samplesarray)
            
            