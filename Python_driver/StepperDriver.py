
import gpiozero


logger = []

def initlogger(g_logger):
    global logger
    logger = g_logger

class stepper:
    def __init__(self,step_pin,dir_pin,half_period):
        self.delay = half_period
        self.step_dir = gpiozero.DigitalOutputDevice(dir_pin)
        self.step_steps = gpiozero.DigitalOutputDevice(step_pin)
        logger.info("stepper init!")
        
    def CW(self,steps,blocking):
        self.step_dir.value = 0
        self.step_steps.blink(self.delay,self.delay,steps,not blocking)
    def CCW(self,steps,blocking):
        self.step_dir.value = 1
        self.step_steps.blink(self.delay,self.delay,steps,not blocking)
        
class magnet:
    def __init__(self,pin):
        self.pin = gpiozero.DigitalOutputDevice(pin);
    def On(self):
        self.pin = 1;
    def Off(self):
        self.pin = 0;
        
class enabler():
    def __init__(self,pin):
        self.enablepin = gpiozero.DigitalOutputDevice(pin)
        self.enablepin = 1;
    def getenabled(self):
        if self.enablepin:
            return 0
        else:
            return 1
    def enable(self):
        self.enablepin = 0
    def disable(self):
        self.enablepin = 1