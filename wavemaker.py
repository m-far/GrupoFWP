# -*- coding: utf-8 -*-
""" This module works as a function generator

It includes:
Defined functions for several waveforms incorporating a switcher to make choosing easier.
A frequency sweep function
A class for evaluating the multiple waveforms
"""
import numpy as np
from scipy.signal import sawtooth, square
    
def create_sine(time, freq, *args):
    """ Creates sine wave 
    
    Parameters
    ----------
    time : array
        time vector in which to evaluate the funcion
    
    freq : int or float
        expected frequency of sine wave
    
    args : dummy 
        used to give compatibility with other functions
    
    Returns
    -------
    
    Evaluated sine wave of given frequency
    """
    
    wave =np.sin(2 * np.pi * time * freq)
    return wave        
    
def create_ramps(time, freq, type_of_ramp=1):
    """ Creates ascending and descending sawtooth wave,
    or a tringle wave, depending on the value of type_of_ramp,
    using the function 'sawtooth' from scypy signal module.
    Used by create_sawtooth_up, create_sawtooth_down and 
    create_triangular.
    
    Parameters
    ----------
    time : array
        time vector in which to evaluate the funcion
    
    freq : int or float
        expected frequency of sine wave
    
    type_of_ramp : {0, 1, 2}
        0 returns a sawtooth waveform with positive slope
        1 returns a sawtooth waveform with negative slope
        0 returns a triangle waveform
    
    Returns
    -------
    
    Evaluated sawtooth or triangle wave of given frequency
    """
    
    wave = sawtooth(2 * np.pi * time * freq, type_of_ramp)
    return wave
    
def create_sawtooth_up(time, freq, *args):
    """ Creates sawtooth waveform with positive slope
   
    Parameters
    ----------
    time : array
        time vector in which to evaluate the funcion
    
    freq : int or float
        expected frequency of sine wave

    args : dummy 
        used to give compatibility with other functions

    Returns
    -------
    
    Evaluated sawtooth waveform with positive slope  and given frequency
    """
    
    wave = create_ramps(time ,freq, 1)
    return wave        

def create_sawtooth_down(time, freq, *args):
    """ Creates sawtooth waveform with negative slope
   
    Parameters
    ----------
    time : array
        time vector in which to evaluate the funcion
    
    freq : int or float
        expected frequency of sine wave
        
    args : dummy 
        used to give compatibility with other functions

    Returns
    -------
    
    Evaluated sawtooth waveform with negative slope and given frequency
    """

    wave = create_ramps(time, freq, 0)
    return wave        

def create_triangular(time, freq, *args):
    """ Creates a triangular wave with symmetric ramps
   
    Parameters
    ----------
    time : array
        time vector in which to evaluate the funcion
    
    freq : int or float
        expected frequency of sine wave
        
    args : dummy 
        used to give compatibility with other functions

    Returns
    -------
    
    Evaluated triangular waveform with given frequency
    """
    

    wave = create_ramps(time, freq, .5)
    return wave        
     
def create_square(time, freq, dutycycle = .5, *args):
    """ Creates a square wave. Uses square function from
    scypy signal module

    Parameters
    ----------
    time : array
        time vector in which to evaluate the funcion
    
    freq : int or float
        expected frequency of sine wave
        
    dutycycle=.5 : scalar or numpy array
        Duty cycle. Default is 0.5 (50% duty cycle). If 
        an array, causes wave shape to change over time,
        and must be the same length as time.
        
    args : dummy 
        used to give compatibility with other functions

    Returns
    -------
    
    Evaluated square waveform with given frequency
    """
    
    wave = square(2 * np.pi * time * freq, dutycycle)
    return wave
    
def create_custom(time, freq, custom_func, *args):
    """ Allows used defined wavefom. Not yet implemented.
    """
    wave = custom_func(time, freq, *args)
    return wave
      
def given_waveform(input_waveform):
    """ Switcher to easily choose waveform.
    
    If the given waveform is not in the list, it raises a TypeError and a list
    containing the accepted inputs.
    
    Parameters
    ----------
    input_waveform : string
        name of desired function to generate
   
    Returns
    -------
    Chosen waveform function
    """
    
    switcher = {
        'sine': create_sine,
        'sawtoothup': create_sawtooth_up,
        'sawtoothdown': create_sawtooth_down  ,          
        'ramp': create_sawtooth_up, #redirects to sawtoothup
        'sawtooth': create_sawtooth_up, #redirects to sawtoothup
        'triangular': create_triangular,
        'square': create_square,
        'custom': create_custom,
    }
    func = switcher.get(input_waveform, wrong_input)
    return func
       
def wrong_input(*args):
    raise TypeError('''Given waveform is invalid. Choose from following list:
        sine, triangular, ramp, sawtooth, sawtoothup, sawtoothdown, square, custom''')

        
#%% Clase que genera ondas

class Wave:
    '''Generates an object with a two methods: evaluate(time).
  
    Attributes
    ----------
    waveform : str {'sine', 'sawtoothup', 'sawtoothdown', 'ramp', 'triangular', 'square', 'custom'} optional
        waveform type. If 'custom', function should acept inputs
        (time, frequency, *args). Default = 'sine'
    frequency : float (optional)
        wave frequency
    amplitude : float (optional)
        wave amplitud
        
    Methods
    ----------
    evaluate(time)
        returns evaluated function type

    '''
    
    def __init__(self, waveform='sine', frequency=400, amplitude=1, custom=None):
        self.frequency = frequency
        self.amplitude = amplitude
        self.waveform = given_waveform(waveform)
        self.customfunc = custom
        
    def evaluate(self, time, *args):
        """Takes in an array-like object to evaluate the funcion in.
        
        Parameters
        ----------
        time : array
            time vector in which to evaluate the funcion
        
            
        Returns
        -------
        
        Evaluated waveform 
        """          
            
        wave = self.waveform(time, self.frequency, *args) * self.amplitude
        return wave
    
