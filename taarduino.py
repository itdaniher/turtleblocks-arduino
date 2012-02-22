import firmata
import commands

class TAArduino(object):
    def __init__(self, baud=115200):
        object.__init__(self)
        self._dev='/dev/ttyUSB0'
        self._baud = baud
        self._arduino = None # Do not initialize this now

	status,output=commands.getstatusoutput("ls /dev/ | grep ttyUSB")
	output=output.split('\n')
	for i in output:
		status,aux=commands.getstatusoutput("udevinfo -a -p /class/tty/%s | grep ftdi_sio > /dev/null"%i)
		if (not status):
			self._dev='/dev/%s'%i
			break
		    
        self.HIGH = firmata.HIGH
        self.LOW = firmata.LOW
        self.INPUT = firmata.INPUT
        self.OUTPUT = firmata.OUTPUT
        self.PWM = firmata.PWM
        self.SERVO = firmata.SERVO

    def _check_init(self):
        if self._arduino is None:
            self._arduino = firmata.Arduino(port = self._dev, \
                baudrate=self._baud)
        self._arduino.parse()

    def delay(self, secs):
        # Do not use this. The firmata module uses time.sleep() to
        # implement this, which breaks gtk+ (unresponsive window)
        self._check_init()
        self._arduino.delay(secs)

    def pin_mode(self, pin, mode):
        self._check_init()
        self._arduino.pin_mode(int(pin), mode)

    def analog_write(self, pin, value):
        self._check_init()
        self._arduino.analog_write(int(pin), int(value))

    def digital_write(self, pin, value):
        self._check_init()
        self._arduino.digital_write(int(pin), value)

    def analog_read(self, pin):
        self._check_init()
        self._arduino.parse()  
        return self._arduino.analog_read(int(pin))

    def digital_read(self, pin):
        self._check_init()
        self._arduino.parse()  
        return self._arduino.digital_read(int(pin))



self.arduino = TAArduino()

from taarduino import *

'delayard':[_('delay')],
    'pinmode':[_('pin mode'),_('pin'),_('mode')],
    'analogwrite':[_('analog write'),_('pin'),_('value')],
    'digitalwrite':[_('digital write'),_('pin'),_('value')],
    'analogread':[_('analog read')],
    'digitalread':[_('digital read')],
    'high':[_('HIGH')],
    'low':[_('LOW')],
    'input':[_('INPUT')],
    'output':[_('OUTPUT')],
    'pwm':[_('PWM')],
    'servo':[_('SERVO')]}

    'delayard':_("delay program execution for the specified number of seconds (can take fractions, e.g. 0.1)"),
    'pinmode':_("selects the pin function (INPUT, OUTPUT, PWM, SERVO)"),
    'analogwrite':_("Writes analog value in specified port. Value must be a number between 0-255"),
    'digitalwrite':_("Writes digital value in specified port. Value must be HIGH or LOW"),
    'analogread':_("Read value from analog port. Value may be between 0 and 1023. Use Vref to determine voltage. For USB aprox. volt=((read)*5)/1024)"),
    'digitalread':_("Read value from digital port. Value may be HIGH or LOW"),
    'high':_("HIGH value for digital port"),
    'low':_("LOW value for digital port"),
    'input':_("configure Arduino port as digital input"),
    'output':_("configure Arduino port as digital output"),
    'pwm':_("configure Arduino port as pwm (pulse width modulation)"),
    'servo':_("configure Arduino port to drive a Servo")}



	# arduino primitives
	'delayard':[1, self.prim_wait, True],
	'pinmode':[2, lambda self, x, y: self.tw.arduino.pin_mode(x, y)],
	'analogwrite':[2, lambda self, x, y: \
	    self.tw.arduino.analog_write(x, y)],
	'digitalwrite':[2, lambda self, x, y: \
	    self.tw.arduino.digital_write(x, y)],
	'analogread':[1, lambda self, x: self.tw.arduino.analog_read(x)],
	'digitalread':[1, lambda self, x: self.tw.arduino.digital_read(x)],
	'high':[0, lambda self: self.tw.arduino.HIGH],
	'low':[0, lambda self: self.tw.arduino.LOW],
	'input':[0, lambda self: self.tw.arduino.INPUT],
	'output':[0, lambda self: self.tw.arduino.OUTPUT],
	'pwm':[0, lambda self: self.tw.arduino.PWM],
	'servo':[0, lambda self: self.tw.arduino.SERVO]}

            ['delayard', 'pinmode', 'analogwrite', 'digitalwrite', 'analogread', 'digitalread',
             'high', 'low', 'input', 'output', 'pwm', 'servo']]

'purple':["#FF00FF","#A000A0"]}

