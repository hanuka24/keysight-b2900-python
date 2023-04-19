# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 14:37:44 2023

@author: Hannah Brunner
Based on: http://lampx.tugraz.at/~hadley/semi/ch9/instruments/Keithley26xx/Keithley26xx.php
"""
import pyvisa

class SMUChannel:
    
    def __init__(self, channel, smu):
        self.channel = channel
        self.smu = smu
        
        self.__voltage_range = 20
        self.__current_range = 2
        
        
    def set_mode_voltage_source(self):
        """
        Sets the channel into voltage source mode.
        In this mode you set the voltage and can measure current, resistance and power.
        """
        self.smu._set_source_mode(self.channel, KeysightB2900.VOLTAGE_MODE)

    def set_mode_current_source(self):
        """
        Sets the channel into current source mode.
        In this mode you set the current and can measure voltage, resistance and power.
        """
        self.smu._set_source_mode(self.channel, KeysightB2900.CURRENT_MODE)

    def set_voltage_limit(self, value):
        """
        Limits the voltage output of the current source.
        If you are in voltage source mode the voltage limit has no effect.
        """
        if value <= self.__voltage_range:
            self.smu._set_limit(self.channel, KeysightB2900.CURRENT_MODE, value)
        else:
            raise ValueError("The limit is not within the range. Please set the range first")

    def set_current_limit(self, value):
        """
        Limits the current output of the voltage source.
        If you are in current source mode the current limit has no effect.
        """
        if value <= self.__current_range:
            self.smu._set_limit(self.channel, KeysightB2900.VOLTAGE_MODE, value)
        else:
            raise ValueError("The limit is not within the range. Please set the range first")

    
    def set_voltage(self, value):
        """
        Sets the output level of the voltage source.
        """
        self.smu._set_level(self.channel, KeysightB2900.VOLTAGE_MODE, value)

    def set_current(self, value):
        """
        Sets the output level of the current source.
        """
        self.smu._set_level(self.channel, KeysightB2900.CURRENT_MODE, value)

    def enable_output(self):
        """
        Sets the source output state to on.

        Note:
           When the output is switched on, the SMU sources either voltage or current, as set by
           set_mode_voltage_source() or set_mode_current_source()
        """
        self.smu._set_output_state(self.channel, KeysightB2900.STATE_ON)

    def disable_output(self):
        """
        Sets the source output state to off.

        Note:
           When the output is switched off, the SMU goes in to High Z mode (meaning: the output is opened).
        """
        self.smu._set_output_state(self.channel, KeysightB2900.STATE_OFF)
        
        
    def measure_voltage(self):
        """
        Perform spot measurement and retrieve voltage.

        Note:
           When the output is switched off, the SMU turns on output automatically and performs a measurement.
        """
        return self.smu._measure(self.channel, KeysightB2900.VOLTAGE_MODE)
    
    def measure_current(self):
        """
        Perform spot measurement and retrieve current.

        Note:
           When the output is switched off, the SMU turns on output automatically and performs a measurement.
        """
        return self.smu._measure(self.channel, KeysightB2900.CURRENT_MODE)
      
    

class KeysightB2900: 
    
    dev = None
    dev_id = ""
    
    # define strings that are used in the LUA commands
    CHAN1 = "2"
    CHAN2 = "1"

    CURRENT_MODE = "CURR"
    VOLTAGE_MODE = "VOLT"

    STATE_ON = "ON"
    STATE_OFF = "OFF"

    SPEED_FAST = 0.01
    SPEED_MED = 0.1
    SPEED_NORMAL = 1
    SPEED_HI_ACCURACY = 10
    
    
    
    def __init__(self, dev_addr = "USB0::2391::12345::XY00001234::0::INSTR"):
        rm = pyvisa.ResourceManager()

        self.dev = rm.open_resource(dev_addr) 
        self.dev_id = self.dev.query("*IDN?")
        
        assert "B2902B" in self.dev_id, "Error: Unexpected device found."
        
        self.chan1 = SMUChannel("1", self)
        self.chan2 = SMUChannel("2", self)
        

    def close(self):
        if self.dev != None:
            self.dev.close()
            self.dev = None
    
    def reset(self):
        
        if self.dev == None:
            raise RuntimeError("Device not connected.")
            
        self.dev.write("*RST")
        
    def set_display(self):
        #todo
        pass
        
    def write_command(self, command):
        
        if self.dev == None:
            raise RuntimeError("Device not connected.")
            
        self.dev.write(command)
        
    def write_query(self, query):
        
        if self.dev == None:
            raise RuntimeError("Device not connected.")
            
        data = self.dev.query(query)  
        return data
    
    
    """
    #####################################################################################
    commands for setting the parameters of channels
    those should not be accessed directly but through the channel class
    #####################################################################################
    """


    def _set_measurement_speed(self, channel, speed, sense_mode):
        """defines how many PLC (Power Line Cycles) a measurement takes"""
        cmd = f':SENS{channel}:{sense_mode}:NPLC {speed}'
        self.write_command(cmd)

    def _set_source_mode(self, channel, source_mode):
        cmd = f':SOUR{channel}:FUNC:MODE {source_mode}'
        self.write_command(cmd)

    def _set_sense_wire_mode(self, channel, four_wire_on):
        """set 2-wire or 4-wire sense mode"""
        cmd = f':SENS{channel}:REM {four_wire_on}'
        self.write_command(cmd)

    def _set_limit(self, channel, sense_mode, value):
        """command used to set the limits for voltage or current"""
        cmd = f':SENS{channel}:{sense_mode}:PROT {value}'
        self.write_command(cmd)

    def _set_level(self, channel, source_mode, value):
        cmd = f':SOUR{channel}:{source_mode} {value}'
        self.write_command(cmd)

    def _set_output_state(self, channel, on_off):
        cmd = f':OUTP{channel} {on_off}'
        self.write_command(cmd)  
        
    """
    #####################################################################################
    commands for reading values from the channels
    those should not be accessed directly but through the channel class
    #####################################################################################
    """
    
    def _measure(self, channel, mode):
        query = f'MEAS:{mode}? (@{channel})'
        return self.dev.query(query)
        
    def _time_domain_sweep(self, channel, source_mode, source_value, num_points, time):
        #setup constant source 'sweep'
        
        
        #setup time trigger
        
        
        #enable and trigger output
        
        #retrieve data
        pass
            
