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
import sys
import commands

from gettext import gettext as _
from plugins.plugin import Plugin

from TurtleArt.tapalette import make_palette
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import palette_blocks
from TurtleArt.tapalette import special_block_colors
from TurtleArt.talogo import primitive_dictionary, logoerror

sys.path.insert(0, os.path.abspath('./plugins/arduino'))
import serial
import firmata


VALUE = {_('HIGH'): firmata.HIGH, _('LOW'): firmata.LOW}
MODE = {_('INPUT'): firmata.INPUT, _('OUTPUT'): firmata.OUTPUT,
        _('PWM'): firmata.PWM, _('SERVO'): firmata.SERVO}

ERROR = _('ERROR: Check the Arduino and the number of port.')
ERROR_VALUE_A = _('ERROR: Value must be a number from 0 to 255.')
ERROR_VALUE_D = _('ERROR: Value must be either HIGH or LOW.')
ERROR_MODE = _('ERROR: The mode must be either INPUT, OUTPUT, PWM or SERVO.')

COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
COLOR_PRESENT = ["#00FFFF","#00A0A0"]


class Arduino(Plugin):

    def __init__(self, parent):
        self.tw = parent

        self._baud = 57600

        self.active_arduino = 0
        self._arduinos = []
        self._arduinos_dev = []

    def setup(self):

        palette = make_palette('arduino', COLOR_NOTPRESENT, _('Palette of Arduino blocks'))

        primitive_dictionary['arduinorefresh'] = self._prim_arduinorefresh
        palette.add_block('arduinorefresh',
                     style='basic-style',
                     label=_('refresh Arduino'),
                     prim_name='arduinorefresh',
                     help_string=_('Search for connected Arduinos.'))
        self.tw.lc.def_prim('arduinorefresh', 0,
            lambda self :
            primitive_dictionary['arduinorefresh']())
        special_block_colors['arduinorefresh'] = COLOR_PRESENT[:]

        primitive_dictionary['arduinoselect'] = self._prim_arduinoselect
        palette.add_block('arduinoselect',
                          style='basic-style-1arg',
                          default = 1,
                          label=_('Arduino'),
                          help_string=_('set current Arduino board'),
                          prim_name = 'arduinoselect')
        self.tw.lc.def_prim('arduinoselect', 1,
            lambda self, n: 
            primitive_dictionary['arduinoselect'](n))

        primitive_dictionary['arduinocount'] = self._prim_arduinocount
        palette.add_block('arduinocount',
                          style='box-style',
                          label=_('number of Arduinos'),
                          help_string=_('number of Arduino boards'),
                          prim_name = 'arduinocount')
        self.tw.lc.def_prim('arduinocount', 0,
            lambda self:
            primitive_dictionary['arduinocount']())

        primitive_dictionary['arduinoname'] = self._prim_arduinoname
        palette.add_block('arduinoname',
                  style='number-style-1arg',
                  label=_('Arduino name'),
                  default=[1],
                  help_string=_('Get the name of an Arduino.'),
                  prim_name='arduinoname')
        self.tw.lc.def_prim('arduinoname', 1,
            lambda self, x:
            primitive_dictionary['arduinoname'](x))

        primitive_dictionary['pinmode'] = self._prim_pin_mode
        palette.add_block('pinmode',
                  style='basic-style-2arg',
                  label=[_('pin mode'),_('pin'),_('mode')],
                  help_string=_('Select the pin function (INPUT, OUTPUT, PWM, SERVO).'),
                  prim_name='pinmode')
        self.tw.lc.def_prim('pinmode', 2,
            lambda self, x, y:
            primitive_dictionary['pinmode'](x, y))

        primitive_dictionary['analogwrite'] = self._prim_analog_write
        palette.add_block('analogwrite',
                  style='basic-style-2arg',
                  label=[_('analog write'),_('pin'),_('value')],
                  default=[0, 255],
                  help_string=_('Write analog value in specified port.'),
                  prim_name='analogwrite')
        self.tw.lc.def_prim('analogwrite', 2,
            lambda self, x, y:
            primitive_dictionary['analogwrite'](x, y))

        primitive_dictionary['analogread'] = self._prim_analog_read
        palette.add_block('analogread',
                  style='basic-style-1arg',
                  label=[_('analog read')],
                  default=[0],
                  help_string=_('Read value from analog port. Value may be between 0 and 1023. Use Vref \
to determine voltage. For USB, volt=((read)*5)/1024) approximately.'),
                  prim_name='analogread')
        self.tw.lc.def_prim('analogread', 1,
            lambda self, x:
            primitive_dictionary['analogread'](x))

        primitive_dictionary['digitalwrite'] = self._prim_digital_write
        palette.add_block('digitalwrite',
                  style='basic-style-2arg',
                  label=[_('digital write'),_('pin'),_('value')],
                  default=[13],
                  help_string=_('Write digital value to specified port.'),
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
                  help_string=_('Set HIGH value for digital port.'),
                  prim_name='high')
        self.tw.lc.def_prim('high', 0,
            lambda self: primitive_dictionary['high']())

        primitive_dictionary['input'] = self._prim_input
        palette.add_block('input',
                  style='box-style',
                  label=_('INPUT'),
                  help_string=_('Configure Arduino port for digital input.'),
                  prim_name='input')
        self.tw.lc.def_prim('input', 0,
            lambda self: primitive_dictionary['input']())

        primitive_dictionary['servo'] = self._prim_servo
        palette.add_block('servo',
                  style='box-style',
                  label=_('SERVO'),
                  help_string=_('Configure Arduino port to drive a servo.'),
                  prim_name='servo')
        self.tw.lc.def_prim('servo', 0,
            lambda self: primitive_dictionary['servo']())

        primitive_dictionary['low'] = self._prim_low
        palette.add_block('low',
                  style='box-style',
                  label=_('LOW'),
                  help_string=_('Set LOW value for digital port.'),
                  prim_name='low')
        self.tw.lc.def_prim('low', 0,
            lambda self: primitive_dictionary['low']())

        primitive_dictionary['output'] = self._prim_output
        palette.add_block('output',
                  style='box-style',
                  label=_('OUTPUT'),
                  help_string=_('Configure Arduino port for digital output.'),
                  prim_name='output')
        self.tw.lc.def_prim('output', 0,
            lambda self: primitive_dictionary['output']())

        primitive_dictionary['pwm'] = self._prim_pwm
        palette.add_block('pwm',
                  style='box-style',
                  label=_('PWM'),
                  help_string=_('Configure Arduino port for PWM (pulse-width modulation).'),
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
        if self._arduinos:
            a = self._arduinos[self.active_arduino]
            a.parse()

    def _prim_pin_mode(self, pin, mode):
        self._check_init()
        if (mode in MODE):
            mode = MODE[mode]
            try:
                a = self._arduinos[self.active_arduino]
                a.pin_mode(int(pin), mode)
            except:
                raise logoerror(ERROR)
        else:
            raise logoerror(ERROR_MODE)
   
    def _prim_analog_write(self, pin, value):
        self._check_init()
        value = int(value)
        if not((value < 0) or (value > 255)):
            try:
                a = self._arduinos[self.active_arduino]
                a.analog_write(int(pin), value)
            except:
                raise logoerror(ERROR)
        else:
            raise logoerror(ERROR_VALUE_A)

    def _prim_digital_write(self, pin, value):
        self._check_init()
        if (value in VALUE):
            value = VALUE[value]
            try:
                a = self._arduinos[self.active_arduino]
                a.digital_write(int(pin), value)
            except:
                raise logoerror(ERROR)
        else:
            raise logoerror(ERROR_VALUE_D)

    def _prim_analog_read(self, pin):
        self._check_init()
        res = -1
        try:
            a = self._arduinos[self.active_arduino]
            res = a.analog_read(int(pin))
        except:
            pass
        
        return res

    def _prim_digital_read(self, pin):
        self._check_init()
        res = -1
        try:
            a = self._arduinos[self.active_arduino]
            res = a.digital_read(int(pin))
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

    def _prim_arduinoselect(self, i):
        n = len(self._arduinos)
        # The list index begin in 0
        i = int(i - 1)
        if (i < n) and (i >= 0):
            self.active_arduino = i
        else:
            raise logoerror('Not found Arduino %s' % int(i + 1))

    def _prim_arduinocount(self):
        return len(self._arduinos)

    def _prim_arduinoname(self, i):
        n = len(self._arduinos)
        # The list index begin in 0
        i = int(i - 1)
        if (i < n) and (i >= 0):
            return self._arduinos_dev[i]
        else:
            raise logoerror('Not found Arduino %s' % int(i + 1))

    def change_color_blocks(self):
        index = palette_name_to_index('arduino')
        arduino_blocks = palette_blocks[index]
        if len(self._arduinos) > 0:
            arduino_present = True
        else:
            arduino_present = False

        for block in self.tw.block_list.list:
            if block.type in ['proto', 'block']:
                if block.name in arduino_blocks:
                    if (arduino_present) or (block.name == 'arduinorefresh'):
                        special_block_colors[block.name] = COLOR_PRESENT[:]
                    else:
                        special_block_colors[block.name] = COLOR_NOTPRESENT[:]
                    block.refresh()

        self.tw.show_toolbar_palette(index, regenerate=True, show=False)

    def _prim_arduinorefresh(self):

        #Close actual Arduinos
        for dev in self._arduinos:
            try:
                dev.close()
            except:
                pass
        self._arduinos = []

        #Search for new Arduinos
        status,output_usb = commands.getstatusoutput("ls /dev/ | grep ttyUSB")
        output_usb_parsed = output_usb.split('\n')
        status,output_acm = commands.getstatusoutput("ls /dev/ | grep ttyACM")
        output_acm_parsed = output_acm.split('\n')    
        output = output_usb_parsed
        output.extend(output_acm_parsed)

        for dev in output:
            if not(dev == ''):
                n = '/dev/%s' % dev
                try:
                    board = firmata.Arduino(port = n, baudrate = self._baud)
                    self._arduinos.append(board)
                    self._arduinos_dev.append(n)
                except:
                    pass

        self.change_color_blocks()

