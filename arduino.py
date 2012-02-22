#!/usr/bin/env python
# Copyright (c) 2012, Alan Aguiar <alanjas@hotmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
from time import time

from gettext import gettext as _
from plugins.plugin import Plugin

from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import media_blocks_dictionary, primitive_dictionary

import firmata
import commands

VALUE = {_('HIGH'): firmata.HIGH, _('LOW'): firmata.LOW}
MODE = {_('INPUT'): firmata.INPUT, _('OUTPUT'): firmata.OUTPUT,
        _('PWM'): firmata.PWM, _('SERVO'): firmata.SERVO}

ERROR = _('ERROR: Check the Arduino and the number of port')
ERROR_VALUE_A = _('ERROR: Value must be a number between 0 to 255')
ERROR_VALUE_D = _('ERROR: Value must be HIGH or LOW')
ERROR_MODE = _('ERROR: The mode must be: INPUT, OUTPUT, PWM or SERVO')

device = '/dev/ttyUSB0'
speed = 57600

class Arduino(Plugin):

    def __init__(self, parent):
        self.tw = parent


        self._dev = device
        self._baud = speed
        self._arduino = None

        status,output = commands.getstatusoutput("ls /dev/ | grep ttyUSB")
        output=output.split('\n')
        for i in output:
	        status,aux=commands.getstatusoutput("udevinfo -a -p /class/tty/%s | grep ftdi_sio > /dev/null"%i)
	        if (not status):
		        self._dev='/dev/%s'%i
		        break


    def setup(self):
        try:
            self._arduino = firmata.Arduino(port = self._dev, baudrate=self._baud)
        except:
            pass


        palette = make_palette('arduino', ["#00FFFF","#00A0A0"], _('Palette of Arduino blocks'))


        primitive_dictionary['pinmode'] = self._prim_pin_mode
        palette.add_block('pinmode',
                  style='basic-style-2arg',
                  label=[_('pin mode'),_('pin'),_('mode')],
                  help_string=_('selects the pin function (INPUT, OUTPUT, PWM, SERVO)'),
                  prim_name='pinmode')
        self.tw.lc.def_prim('pinmode', 2,
            lambda self, x, y:
            primitive_dictionary['pinmode'](x, y))

        primitive_dictionary['analogwrite'] = self._prim_analog_write
        palette.add_block('analogwrite',
                  style='basic-style-2arg',
                  label=[_('analog write'),_('pin'),_('value')],
                  default=[0, 255],
                  help_string=_('Writes analog value in specified port.'),
                  prim_name='analogwrite')
        self.tw.lc.def_prim('analogwrite', 2,
            lambda self, x, y:
            primitive_dictionary['analogwrite'](x, y))

        primitive_dictionary['analogread'] = self._prim_analog_read
        palette.add_block('analogread',
                  style='basic-style-1arg',
                  label=[_('analog read')],
                  default=[0],
                  help_string=_('Read value from analog port. Value may be between 0 and 1023. Use Vref to determine voltage.\
For USB aprox. volt=((read)*5)/1024)'),
                  prim_name='analogread')
        self.tw.lc.def_prim('analogread', 1,
            lambda self, x:
            primitive_dictionary['analogread'](x))

        primitive_dictionary['digitalwrite'] = self._prim_digital_write
        palette.add_block('digitalwrite',
                  style='basic-style-2arg',
                  label=[_('digital write'),_('pin'),_('value')],
                  default=[13],
                  help_string=_('Writes digital value in specified port.'),
                  prim_name='digitalwrite')
        self.tw.lc.def_prim('digitalwrite', 2,
            lambda self, x, y:
            primitive_dictionary['digitalwrite'](x, y))

        primitive_dictionary['digitalread'] = self._prim_digital_read
        palette.add_block('digitalread',
                  style='basic-style-1arg',
                  label=[_('digital read')],
                  default=[13],
                  help_string=_('Read value from digital port.'),
                  prim_name='digitalread')
        self.tw.lc.def_prim('digitalread', 1,
            lambda self, x:
            primitive_dictionary['digitalread'](x))

        primitive_dictionary['high'] = self._prim_high
        palette.add_block('high',
                  style='box-style',
                  label=_('HIGH'),
                  help_string=_('HIGH value for digital port'),
                  prim_name='high')
        self.tw.lc.def_prim('high', 0,
            lambda self: primitive_dictionary['high']())

        primitive_dictionary['input'] = self._prim_input
        palette.add_block('input',
                  style='box-style',
                  label=_('INPUT'),
                  help_string=_('configure Arduino port as digital input'),
                  prim_name='input')
        self.tw.lc.def_prim('input', 0,
            lambda self: primitive_dictionary['input']())

        primitive_dictionary['servo'] = self._prim_servo
        palette.add_block('servo',
                  style='box-style',
                  label=_('SERVO'),
                  help_string=_('configure Arduino port to drive a Servo'),
                  prim_name='servo')
        self.tw.lc.def_prim('servo', 0,
            lambda self: primitive_dictionary['servo']())

        primitive_dictionary['low'] = self._prim_low
        palette.add_block('low',
                  style='box-style',
                  label=_('LOW'),
                  help_string=_('LOW value for digital port'),
                  prim_name='low')
        self.tw.lc.def_prim('low', 0,
            lambda self: primitive_dictionary['low']())

        primitive_dictionary['output'] = self._prim_output
        palette.add_block('output',
                  style='box-style',
                  label=_('OUTPUT'),
                  help_string=_('configure Arduino port as digital output'),
                  prim_name='output')
        self.tw.lc.def_prim('output', 0,
            lambda self: primitive_dictionary['output']())

        primitive_dictionary['pwm'] = self._prim_pwm
        palette.add_block('pwm',
                  style='box-style',
                  label=_('PWM'),
                  help_string=_('configure Arduino port as pwm (pulse width modulation)'),
                  prim_name='pwm')
        self.tw.lc.def_prim('pwm', 0,
            lambda self: primitive_dictionary['pwm']())




    def start(self):
        pass

    def quit(self):
        pass

    def stop(self):
        pass

    def clear(self):
        pass

    def _check_init(self):
        if self._arduino:
            self._arduino.parse()

    def _prim_pin_mode(self, pin, mode):
        self._check_init()
        if (mode in MODE):
            mode = MODE[mode]
            try:
                self._arduino.pin_mode(int(pin), mode)
            except:
                return ERROR
        else:
            return ERROR_MODE
            
    def _prim_analog_write(self, pin, value):
        self._check_init()
        value = int(value)
        if not((value < 0) or (value > 255)):
            try:
                self._arduino.analog_write(int(pin), value)
            except:
                return ERROR
        else:
            return ERROR_VALUE_A

    def _prim_digital_write(self, pin, value):
        self._check_init()
        if (value in VALUE):
            value = VALUE[value]
            try:
                self._arduino.digital_write(int(pin), value)
            except:
                return ERROR
        else:
            return ERROR_VALUE_D

    def _prim_analog_read(self, pin):
        self._check_init()
        self._arduino.parse()
        res = -1
        try:
            res = self._arduino.analog_read(int(pin))
        except:
            pass
        
        return res

    def _prim_digital_read(self, pin):
        self._check_init()
        self._arduino.parse()
        res = -1
        try:
            res = self._arduino.digital_read(int(pin))
        except:
            pass

        if res == VALUE[_('HIGH')]:
            res = _('HIGH')
        elif res == VALUE[_('LOW')]:
            res = _('LOW')

        return res
            
    def _prim_high(self):
        return _('HIGH')

    def _prim_low(self):
        return _('LOW')

    def _prim_input(self):
        return _('INPUT')

    def _prim_output(self):
        return _('OUTPUT')

    def _prim_pwm(self):
        return _('PWM')

    def _prim_servo(self):
        return _('SERVO')


