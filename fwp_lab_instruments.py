# -*- coding: utf-8 -*-
"""
This module defines classes to manipulate lab instruments via PyVisa.

resources: function
    Returns a list of tuples of connected 'INSTR' resources.
Osci: class
    Allows communication with a Tektronix Digital Oscilloscope.
Osci.measure: method
    Takes a measure of a certain type on a certain channel.
Gen: class
    Allows communication with Tektronix Function Generators.
Gen.output: method
    Turns on/off an output channel. Also configures it if needed.

@author: Vall
"""

import re
import pyvisa as visa

#%%

def resources():
    
    """Returns a list of tuples of connected resources.
    
    Parameters
    ----------
    nothing
    
    Returns
    -------
    resources: list
        List of connected resources.
    
    """
    
    rm = visa.ResourceManager()
    resources = rm.list_resources()
    print(resources)
    
    return resources

#%%

class Osci:
    
    """Allows communication with a Tektronix Digital Oscilloscope.
    
    It allows communication with multiple models, based on the official 
    Programmer Guide (https://www.tek.com/oscilloscope/tds1000-manual).
    
        TBS1000B/EDU, 
        TBS1000, 
        TDS2000C/TDS1000C-EDU,
        TDS2000B/TDS1000B, 
        TDS2000/TDS1000, 
        TDS200,
        TPS2000B/TPS2000.
    
    Attributes
    ----------
    Osci.port: str required
        Computer's port where the oscilloscope is connected.
        i.e.: 'USB0::0x0699::0x0363::C108013::INSTR'
    Osci.osci: pyvisa.ResourceManager.open_resource object
        PyVisa object for communication with instrument.
    Osci.config_measure: dict {'Source': int, 'Type': str}
        Immediate measurement's current configuration.
    
    Methods
    -------
    Osci.measure(): function
        Makes a measurement of a certain type on one channel.
    
    Examples
    --------
    >> osci = Osci(port='USB0::0x0699::0x0363::C108013::INSTR')
    >> result, units = osci.measure('Min', 1, print_result=True)
    1.3241 V
    >> result
    1.3241
    >> units
    'V'   
    
    """

    def __init__(self, port):
        
        """Defines oscilloscope object and opens it as Visa resource.
        
        It also defines the following attributes:
                'Osci.port' (PC's port where it is connected)
                'Osci.osci' (PyVISA object)
                'Osci.config_measure' (Measurement's current 
                configuration)
        
        Parameters
        ---------
        port: str
            Computer's port where the oscilloscope is connected.
            i.e.: 'USB0::0x0699::0x0363::C108013::INSTR'
        
        """
        
        rm = visa.ResourceManager()
        osci = rm.open_resource(port, read_termination="\n")
        print(osci.query('*IDN?'))
        
        # General Configuration
        osci.write('DAT:ENC RPB')
        osci.write('DAT:WID 1') # Binary transmission mode
        
        # Trigger configuration
        osci.write('TRIG:MAI:MOD AUTO') # Option: NORM (waits for trigger)
        osci.write('TRIG:MAI:TYP EDGE')
        osci.write('TRIG:MAI:LEV 5')
        osci.write('TRIG:MAI:EDGE:SLO RIS')
        osci.write('TRIG:MAI:EDGE:SOU CH1') # Option: EXT
        osci.write('HOR:MAI:POS 0') # Makes the complete measure at once
        
        self.port = port
        self.osci = osci
        self.config_measure = self.check_config_measure()
        # This last line saves the current measurement configuration

    def check_config_measure(self):
        
        """Returns the current measurements' configuration.
        
        Parameters
        ----------
        nothing
        
        Returns
        -------
        configuration: dict as {'Source': int, 'Type': str}
            It states the source and type of configured measurement.
            
        """
        
        configuration = {}
        
        configuration.update({'Source': # channel
            re.findall('\d', self.osci.query('MEASU:IMM:SOU?'))})
        configuration.update({'Type': # type of measurement
            self.osci.query('MEASU:IMM:TYP?')})
    
        return configuration

    def re_config_measure(self, measure_type, measure_ch):
        
        """Reconfigures the measurement, if needed.
        
        Parameters
        ---------
        measure_type: str
            Key that configures the measure type.
            i.e.: 'Min', 'min', 'minimum', etc.
        measure_ch=1: int {1, 2}
            Number of the measure's channel.
        
        Returns
        -------
        nothing
        
        See also
        --------
        Osci.measure()
        Osci.check_config_measure()
        
        """
        
        # This has some keys to recognize measurement's type
        dic = {'mean': 'MEAN',
               'min': 'MINI',
               'max': 'MAXI',
               'freq': 'FREQ',
               'per': 'PER',
               'rms': 'RMS',
               'pk2': 'PK2',
               'amp': 'PK2', # absolute difference between max and min
               'ph': 'PHA',
               'crms': 'CRM', # RMS on the first complete period
               'cmean': 'CMEAN',
               'rise': 'RIS', # time betwee  10% and 90% on rising edge
               'fall': 'FALL',
               'low': 'LOW', # 0% reference
               'high': 'HIGH'} # 100% reference

        if measure_ch != 1 and measure_ch != 2:
            print("Unrecognized measure channel ('CH1' as default).")
            measure_ch = 1

        # Here is the algorithm to recognize measurement's type
        if 'c' in measure_type.lower():
            if 'rms' in measure_type.lower():
                measure_option = dic['crms']
            else:
                measure_option = dic['cmean']
        else:
            for key, value in dic.items():
                if key in measure_type.lower():
                    measure_option = value
            if measure_option not in dic.values():
                measure_option = 'FREQ'
                print("Unrecognized measure type ('FREQ' as default).")
        
        # Now, reconfigure if needed
        if self.config_measure('Source') != measure_ch:
            self.osci.write('MEASU:IMM:SOU CH{:.0f}'.format(measure_ch))
            print("Measure channel changed to 'CH{:.0f}'".format(
                    measure_ch))
        if self.config_measure('Type') != measure_option:
            self.osci.write('MEASU:IMM:TYP {}'.format(measure_option))
            print("Measure type changed to '{}'".format(
                    measure_option))
        
        return
        
    def measure(self, measure_type, measure_ch=1, print_result=False):
        
        """Takes a measure of a certain type on a certain channel.
        
        Parameters
        ---------
        measure_type: str
            Key that configures the measure type.
            i.e.: 'Min', 'min', 'minimum', etc.
        measure_ch=1: int {1, 2} optional
            Number of the measure's channel.
        print_result=False: bool optional
            Says whether to print or not the result.
        
        Returns
        -------
        result: int, float
            Measured value.
        
        See also
        --------
        Osci.re_config_measure()
        Osci.check_config_measure()
        
        """
        
        self.re_config_measure(measure_type, measure_ch)
        
        result = float(self.osci.query('MEASU:IMM:VAL?'))
        units = self.osci.query('MEASU:IMM:UNI?')
        
        if print_result:
            print("{} {}".format(result, units))
        
        return result

#%%

class Gen:
    
    """Allows communication with Tektronix Function Generators.
    
    It allows communication with multiple models, based on the official 
    programming manual 
    (https://www.tek.com/signal-generator/afg3000-manual/afg3000-series-2)
    
        AFG3011;
        AFG3021B;
        AFG3022B;
        AFG3101;
        AFG3102;
        AFG3251;
        AFG3252.

    """
    
    def __init__(self, port):

        """Defines oscilloscope object and opens it as Visa resource.
        
        Variables
        ---------
        port: str
            Computer's port where the oscilloscope is connected.
            i.e.: 'USB0::0x0699::0x0346::C036493::INSTR'
        
        """
        
        rm = visa.ResourceManager()
        gen = rm.open_resource(port, read_termination="\n")
        print(gen.query('*IDN?'))
        
        self.port = port
        self.gen = gen
    
    def output(self, output, output_waveform='sin', 
               output_frequency=1e3, output_amplitude=1, 
               output_offset=0, output_phase=0, 
               output_ch=1, reconfig=True):
        
        """Turns on/off an output channel. Also configures it if needed.
                
        Variables
        ---------
        output: bool
            Says whether to turn on (True) or off (False).
        output_waveform='sin': str
            Output's waveform.
        output_frequency=1e3: int, float
            Output's frequency in Hz.
        output_amplitude=1: int, float
            Output's amplitude in Vpp.
        output_offset=0: int, float
            Output's offset in V.
        output_phase=0: int, flot
            Output's phase in multiples of pi.
        output_ch=1: int {1, 2}
            Output channel.
        reconfig=True: bool
            Indicates whether the output must be reconfigured or not.
        
        Returns
        -------
        nothing
        
        Examples
        --------
        >> gen = Gen()
        >> gen.output(True, output_amplitude=2)
        {turns on channel 1 and plays a sinusoidal 1kHz and 2Vpp wave}
        >> gen.output(0, reconfig=False)
        {turns off channel 1}
        >> gen.output(1, reconfig=False)
        {turns on channel 1 with the same wave as before}
        >> gen.output(True, 'squ75')
        {turns on channel 1 with asymmetric square 1kHz and 1Vpp wave}
        >> gen.output(True, 'ram50')
        {turns on channel 1 with triangular 1kHz and 1Vpp wave}
        >> gen.output(True, 'ram0')
        {turns on channel 1 with positive ramp}
        
        """
        
        if output and reconfig:
            self.config_output(output_waveform=output_waveform, 
                               output_frequency=output_frequency,
                               output_amplitude=output_amplitude,
                               output_offset=output_offset,
                               output_phase=output_phase, 
                               output_ch=output_ch)
        
        self.gen.write('OUTP{}:STAT {}'.format(output_ch, output))
        # if output=True, turns on
        # if output=False, turns off
        
        if output:
            print('Channel {} turn on'.format(output_ch))
        else:
            print('Channel {} turn off'.format(output_ch))
    
    def config_output(self, output_waveform='sin', output_frequency=1e3,
                      output_amplitude=1, output_offset=0, 
                      output_phase=0, output_ch=1):

        """Configures an output channel.
                
        Variables
        ---------
        output: bool
            Says whether to turn on (True) or off (False).
        output_waveform='sin': str
            Output's waveform.
        output_frequency=1e3: int, float
            Output's frequency in Hz.
        output_amplitude=1: int, float
            Output's amplitude in Vpp.
        output_offset=0: int, float
            Output's offset in V.
        output_phase=0: int, flot
            Output's phase in multiples of pi.
        output_ch=1: int {1, 2}
            Output channel.
        reconfig=True: bool
            Indicates whether the output must be reconfigured or not.
        
        Returns
        -------
        nothing
        
        See also
        --------
        Gen.output()
        
        """

        dic = {'sin': 'SIN',
               'squ': 'SQU',
               'ram': 'RAMP', # ramp and triangle
               'lor': 'LOR', # lorentzian
               'sinc': 'SINC', # sinx/x
               'gau': 'GAUS'} # gaussian
        
        if output_ch != 1 and output_ch != 2:
            print("Unrecognized output channel ('CH1' as default).")
            output_ch = 1
        
        if 'c' in output_waveform.lower():
            output_form = dic['sinc']
        else:
            for key, value in dic.items():
                if key in output_waveform.lower():
                    output_form = value
            if output_form not in dic.values():
                output_form = 'SIN'
                print("Unrecognized waveform ('SIN' as default).")
            
        self.gen.write('SOUR{}:FUNC:SHAP {}'.format(output_ch,
                                                    output_form))
        
        if output_form == 'RAMP':
            aux = re.findall(r"[-+]?\d*\.\d+|\d+",
                             output_waveform.lower())
            try:
                aux = aux[0]
                self.gen.write('SOUR{}:FUNC:RAMP:SYMM {}'.format(
                    output_ch,
                    aux)) # percentual
            except IndexError:
                print('Default ramp symmetry')
        
        if output_form == 'SQU':
            aux = re.findall(r"[-+]?\d*\.\d+|\d+",
                             output_waveform.lower())
            try:
                aux = aux[0]
                self.gen.write('SOUR{}:PULS:DCYC {:.1f}'.format(
                    output_ch,
                    aux)) # percentual
            except IndexError:
                print('Default square duty cycle')
        
        self.gen.write('SOUR{}:VOLT:LEV:IMM:OFFS {}'.format(
                output_ch,
                output_offset)) # in V
        
        self.gen.write('SOUR{}:VOLT:LEV:IMM:AMPL {}'.format(
                output_ch,
                output_amplitude)) # in Vpp
        
        self.gen.write('SOUR{}:FREQ {}'.format(
                output_ch,
                output_frequency)) # Hz
        
        self.gen.write('SOUR{}:PHAS {} PI'.format(
                output_ch,
                output_phase)) # in multiples of pi
        

            