

import gpiozero
import time

class Cord_XY_Drive:
    def __init__(self,enable_pin,step_pin_l,dir_pin_l,step_pin_r,dir_pin_r,max_period,min_period,accel):
        self.enable_pin = gpiozero.DigitalOutputDevice(enable_pin)
        self.dir_pin_l = gpiozero.DigitalOutputDevice(dir_pin_l)
        self.step_pin_l = gpiozero.DigitalOutputDevice(step_pin_l)
        self.dir_pin_r = gpiozero.DigitalOutputDevice(dir_pin_r)
        self.step_pin_r = gpiozero.DigitalOutputDevice(step_pin_r)
        self.max_period_h = max_period/2
        self.min_period_h = min_period/2
        self.accel = accel
        self.left_enabled = 0
        self.right_enabled = 0
        
    def Start(self,Steps):
        halfsteps = Steps/2
        self.step_pin_l.value = 0
        self.step_pin_r.value = 0
        self.dir_pin_r = self.dir_r
        self.dir_pin_l = self.dir_l
        pause = self.max_period_h
        pot_pause = pause
        time.sleep(self.max_period_h)
        for i in range(0,Steps):
            self.step_pin_l.value ^= self.left_enabled
            self.step_pin_r.value ^= self.right_enabled
            time.sleep(pot_pause)
            self.step_pin_l.value ^= self.left_enabled
            self.step_pin_r.value ^= self.right_enabled
            time.sleep(pot_pause)
            if(i > halfsteps):
                pause += self.accel
            else:
                pause -= self.accel
            pot_pause = max(pause,self.min_period_h)
        if(self.left_enabled):
            self.steps_l += Steps * ((2 * self.dir_l)-1)
        if(self.right_enabled):
            self.steps_r += Steps * ((2 * self.dir_r)-1)
        self.steps_x = .5*(self.steps_l + self.steps_r)
        self.steps_y = .5*(self.steps_l - self.steps_r)
            
        
    def NE(self,steps):
        self.left_enabled = 0
        self.right_enabled = 1
        self.dir_r = 0
        self.Start(steps)
        
    def N(self,steps):
        self.left_enabled = 1
        self.right_enabled = 1
        self.dir_l = 1
        self.dir_r = 0
        self.Start(steps)
        
    def NW(self,steps):
        self.left_enabled = 1
        self.right_enabled = 0
        self.dir_l = 1
        self.Start(steps)
        
    def E(self,steps):
        self.left_enabled = 1
        self.right_enabled = 1
        self.dir_l = 0
        self.dir_r = 0
        self.Start(steps)
        
    def W(self,steps):
        self.left_enabled = 1
        self.right_enabled = 1
        self.dir_l = 1
        self.dir_r = 1
        self.Start(steps)
        
    def SE(self,steps):
        self.left_enabled = 1
        self.right_enabled = 0
        self.dir_l = 0
        self.Start(steps)
        
    def S(self,steps):
        self.left_enabled = 1
        self.right_enabled = 1
        self.dir_l = 0
        self.dir_r = 1
        self.Start(steps)
        
            
    def SW(self,steps):
        self.left_enabled = 0
        self.right_enabled = 1
        self.dir_r = 1
        self.Start(steps)


class magnet:
    def __init__(self,pin):
        self.pin = gpiozero.DigitalOutputDevice(pin);
        self.isOn = 0;
    def On(self):
        self.pin.value = 1;
        self.isOn = 1;
    def Off(self):
        self.pin.value = 0;
        self.isOn = 0;
