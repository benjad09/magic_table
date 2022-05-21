import tkinter as tk
#import gpiozero
import configparser
import datetime
import queue
import logging
import Cord_XY_Fake as Cord_XY
import math

import threading
import time

from tkinter.scrolledtext import ScrolledText

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(credentials.Certificate('benscrappydndthing_app_key.json'), {
    'databaseURL': 'https://benscrappydndthing-default-rtdb.firebaseio.com/'
})



logger = logging.getLogger(__name__)
VERSION = 0.01

class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.place(relx = 0,rely = 0,relwidth = 1, relheight = 1)
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = []
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)


        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')

        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)



    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
                
            except queue.Empty:
                break
            else:
                self.display(record)
                
        self.frame.after(100, self.poll_log_queue)





class QueueHandler(logging.Handler):

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)
        
class MoverManager:
    def __init__(self,XY,magnet,squares_step,Map_Paramiters):
        self.XY = XY
        self.magnet = magnet
        self.order_q = queue.Queue()
        self.value_q = queue.Queue()
        self.large_order_q = queue.Queue()
        self.threading = True
        self.squaresize = squares_step
        self.Map_Paramiters = Map_Paramiters
        self.tread = threading.Thread(target=self.Handler, )
        self.tread.start()
        
        
        
    def Handler(self):
        while(self.threading):
            if not self.order_q.empty():
                neworder = self.order_q.get()
                newvalue = self.value_q.get()
                logger.debug("Executing Order" + neworder + str(newvalue))
                #print("Executing Order" + neworder + str(newvalue))
                if(neworder == "NE"):
                    self.XY.NE(int(newvalue))
                elif(neworder == "N"):
                    self.XY.N(int(newvalue))
                elif(neworder == "NW"):
                    self.XY.NW(int(newvalue))
                elif(neworder == "E"):
                    self.XY.E(int(newvalue))
                elif(neworder == "W"):
                    self.XY.W(int(newvalue))
                elif(neworder == "SE"):
                    self.XY.SE(int(newvalue))
                elif(neworder == "S"):
                    self.XY.S(int(newvalue))
                elif(neworder == "SW"):
                    self.XY.SW(int(newvalue))
                elif(neworder == "M"):
                    if newvalue > 0:
                       self.magnet.On()
                    else:
                        self.magnet.Off()
                else:
                    logger.error("invalid command");
            else:
                self.check_master_q()
                time.sleep(.100)
                
                
                #print("no order sleep")
    
    def addorder(self,order,value):
        logger.debug("order added-> "+str(order)+":"+str(value))
        self.order_q.put(str(order))
        self.value_q.put(int(value))

    def push_large_order(self,orders):
        self.large_order_q.put(orders)


    def check_master_q(self):
        if not self.large_order_q.empty():
            order_list = self.large_order_q.get()
            last_order = ""
            value = 0
            for i in order_list:
                print(i)
                if "GOTO" in i:
                    new_position = int(i.split(":")[1])
                    posx =  ((new_position % 15)) - (self.X_Y_To_Square(self.XY.steps_x,self.XY.steps_y)%15)
                    posy = math.floor(self.X_Y_To_Square(self.XY.steps_x,self.XY.steps_y)/15) - (math.floor(new_position / 15))
                    logger.info("X"+str(posx)+"Y"+str(posy))
                    if posx > 0:
                        self.addorder("E",posx * self.squaresize)
                    if posx < 0:
                        self.addorder("W",abs(posx * self.squaresize))
                    if posy > 0:
                        self.addorder("N",posy * self.squaresize)
                    if posy < 0:
                        self.addorder("S",abs(posy * self.squaresize))
                    last_order = None
                    value = 0
                elif i == "MagON":
                    self.addorder("M",1)
                    last_order = None
                    value = 0
                else:
                    if last_order:
                        if last_order != i:
                            self.addorder(last_order,self.squaresize*value*len(last_order))
                            value = 0
                    last_order = i
                    value += 1
                    if i == "MagOFF":
                        self.addorder("M",0)
                        last_order = None
                        value = 0  



    def X_Y_To_Square(self,x,y):
        return((math.floor(x/self.squaresize))+((self.Map_Paramiters["ysize"]-1)*self.Map_Paramiters["xsize"])-(math.floor(y/self.squaresize)*self.Map_Paramiters["xsize"]))




class MapHandler:
    def __init__(self, frame,Map_Paramiters):
        self.master = frame
        self.square_size = Map_Paramiters["square_px"]
        self.x_dim = Map_Paramiters["xsize"]
        self.y_dim = Map_Paramiters["ysize"]
        self.canvas = tk.Canvas(self.master, bg = "white",width = (self.x_dim*self.square_size)+1,height = self.y_dim*self.square_size+1)
        #self.canvas.place(relx = 0,rely = 0,relheight = 1,relwidth = 0.7)
        self.canvas.place(relx = 0,rely = 0)
        for i in range(0,self.y_dim+1):
            self.canvas.create_line(0,i*self.square_size+2,self.x_dim*self.square_size+2,i*self.square_size+2)
        for i in range(0,self.x_dim+1):
            self.canvas.create_line(i*self.square_size+2,0,i*self.square_size+2,self.y_dim*self.square_size+2)

        self.char = []

        self.char_list = tk.Listbox(self.master)
        self.char_list.place(relx = .66,rely = 0,relheight = 0.5,relwidth = 0.33)



    def get_size(self):
        self.map_w = self.canvas.winfo_width()
        self.map_h = self.canvas.winfo_height()
        logger.debug("Canvas Dimentions:" +str(self.map_w)+","+str(self.map_h))

    def update_map(self,database):
        if database:
            name_list = []
            name_list_s = []
            burn_list = []
            for i in self.char:
                name_list.append(i["name"])
            for i in database:
                if i != None:
                    name_list_s.append(i["name"])
            for i in range(0,len(self.char)):
                if self.char[i]["name"] not in name_list_s:
                    burn_list.append[i]
            for i in burn_list:
                self.char[i].pop(i)
            for i in database:
                if i != None:
                    if i["name"] not in name_list:
                        self.add_char(i["name"],i["location"],i["id"])
                    else:
                        self.update_char(i["name"],i["location"],i["id"])
        else:
            for i in range(0,len(self.char)):
                self.canvas.delete(self.char[i]["canvas_object"])
            self.char = []






    def add_char(self,name,location,identy):
        self.char.append({"name":name,"location":location,"id":identy,"canvas_object":0})
        self.char[-1]["canvas_object"] = self.canvas.create_oval(self.getxy(location),fill = self.getcolor(identy))
        self.char_list.insert(len(self.char),name)
    def update_char(self,name,location,identy):
        i = 0
        for i in range(0,len(self.char)):
            if self.char[i]["name"] == name:
                break;
        self.canvas.coords(self.char[i]["canvas_object"],self.getxy(location))


    def getxy(self,location):
        return((location%self.y_dim)*self.square_size+4,math.floor(location/self.x_dim)*self.square_size+4,(location%self.y_dim)*self.square_size+(self.square_size),math.floor(location/self.x_dim)*self.square_size+(self.square_size))

    def getcolor(self,id_):
        temp_id = id_
        while(temp_id >= 6):
            temp_id -= 6
        colors = ["#00FF00","#FF0000","#0000FF","#00FFFF","#FFFF00","#FF00FF"]
        return colors[temp_id]
                        
                    
                    

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)


        self.master = master

        self.screen_w = int(self.winfo_screenwidth())
        self.screen_h = int(self.winfo_screenheight())

        self.default_geometry = str(int(self.screen_w/2))+"x"+str(int(self.screen_h/2))+"+"+str(int(self.screen_w/4))+"+"+str(int(self.screen_h/4))
        print(self.default_geometry)

        self.master.geometry(self.default_geometry)
        self.master.state('normal')
        self.master.minsize(600,400)

        self.master.wm_title("Python On PI thing")
        
        
        self.load_config()
        #self.step_1 = StepperDriver.stepper(4,3,self.STEP_DELAY)
        #self.step_2 = StepperDriver.stepper(27,17,self.STEP_DELAY)
        self.magnet = Cord_XY.magnet(2)
        #self.enabler = StepperDriver.enabler(22)
        self.cordXY = Cord_XY.Cord_XY_Drive(22,4,3,27,17,0.01,.001,.0005)
        
        
        
        self.MM = MoverManager(self.cordXY,self.magnet,self.squares_step,self.Map_Paramiters)

        self.map_frame = tk.LabelFrame(self.master, text="Map")

        self.map = MapHandler(self.map_frame,self.Map_Paramiters)



# As an admin, the app has access to read and write all data, regradless of Security Rules
        self.player_ref = db.reference('Players')
        logger.info(self.player_ref.get())
        self.map.update_map(self.player_ref.get())
        self.player_ref.listen(self.update_player_map)

        self.orders_q = db.reference('Que')
        self.clear_orders()
        print(self.orders_q.get())
        self.orders_q.listen(self.update_orders)
        
        
        
        self.square_steps = tk.LabelFrame(self.master,text = "Manual");
        butt_names = ["NW","N","NE","W","0","E","SW","S","SE"]
        self.manual_butts = []
        for i in range (0,9):
            self.manual_butts.append(tk.Button(self.square_steps,text = butt_names[i],command = lambda m=butt_names[i]: self.Manual_Move(m)))
        for i in range (0,3):
            for ii in range(0,3):
                self.manual_butts[i*3 + ii].place(relx = .33*ii,rely = .2*i,relheight = 0.2,relwidth = 0.33)
        self.manual_steps_entry = tk.DoubleVar()
        self.manual_steps_entry.set(self.squares_step)
        self.manual_steps = tk.Scale(self.square_steps,variable = self.manual_steps_entry,tickinterval = 1,orient = "horizontal",from_ = 0,to = self.squares_step*2)
        self.manual_steps.place(relx=0,rely = .6,relheight = 0.2,relwidth = 1)
        self.mag_on_button = tk.Button(self.square_steps,text = "mag on",command = lambda m= 1: self.Manual_Magnet(m))
        self.mag_off_button = tk.Button(self.square_steps,text = "mag off",command = lambda m= 0: self.Manual_Magnet(m))
        self.mag_on_button.place(relx = 0,rely = .8,relheight = 0.2,relwidth = 0.5)
        self.mag_off_button.place(relx = .5,rely = .8,relheight = 0.2,relwidth = 0.5)
        
        
        self.console_frame = tk.LabelFrame(self.master, text="Console")
        self.console = ConsoleUi(self.console_frame)
        
        self.master.protocol('WM_DELETE_WINDOW', self.stop_all_treads)

        self.infopannel =  tk.LabelFrame(self.master, text="Info")
        self.squarein = tk.Label(self.infopannel,text="square:0")
        self.leftsteps = tk.Label(self.infopannel,text="left:"+str(self.cordXY.steps_l))
        self.rightsteps = tk.Label(self.infopannel,text="right:"+str(self.cordXY.steps_r))
        self.xpos = tk.Label(self.infopannel,text="x:"+str(self.cordXY.steps_x))
        self.ypos = tk.Label(self.infopannel,text="y:"+str(self.cordXY.steps_y))
        self.squarein.place(relx = 0,rely = 0,relheight = 0.33,relwidth = 1)
        self.leftsteps.place(relx = 0,rely = .33,relheight = 0.33,relwidth = .5)
        self.rightsteps.place(relx = .5,rely = .33,relheight = 0.33,relwidth = .5)
        self.xpos.place(relx = 0,rely = .66,relheight = 0.33,relwidth = .5)
        self.ypos.place(relx = 0.5,rely = .66,relheight = 0.33,relwidth = .5)
        self.master.after(100, self.update_info)
        
        self.clear_players_butt = tk.Button(self.master,text = "clear_players",command = self.clear_players)
        self.clear_orders_butt = tk.Button(self.master,text = "clear_orders",command = self.clear_orders)
        self.clear_players_butt.place(relx = 0.66,rely = 0.2,relheight = 0.1,relwidth = 0.165)
        self.clear_orders_butt.place(relx = 0.825,rely = 0.2,relheight = 0.1,relwidth = 0.165)
        self.console_frame.place(relx = 0,rely = .66,relheight = 0.33,relwidth = 0.66)
        self.square_steps.place(relx = 0.66,rely = 0.5,relheight = 0.5,relwidth = 0.33)
        self.infopannel.place(relx = 0.66,rely = 0.3,relheight = 0.2,relwidth = 0.33)
        self.map_frame.place(relx=0,rely = 0,relheight = 0.66,relwidth = .66)

        logger.info("VERSION: "+str(VERSION))
        #self.moveforbutt = tk.Button(text = "ONWARD",command = self.moveforward)
        #self.moveforbutt.pack()
        #self.movebackward = tk.Button(text = "BACKWARD",command = self.moveback)
        #self.movebackward.pack()

    def update_info(self):
        self.squarein.configure(text="square:"+str(self.X_Y_To_Square(self.cordXY.steps_x,self.cordXY.steps_y)))
        self.leftsteps.configure(text="left:"+str(self.cordXY.steps_l))
        self.rightsteps.configure(text="right:"+str(self.cordXY.steps_r))
        self.xpos.configure(text="x:"+str(self.cordXY.steps_x))
        self.ypos.configure(text="y:"+str(self.cordXY.steps_y))
        self.master.after(100, self.update_info)

    def stop_all_treads(self):
        self.MM.threading = False
        self.master.destroy()
        
        
    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.STEP_DELAY = float(self.config['stepper']['stepdelay'])
        self.squares_step = int(self.config['MAP']['cardinalsteps'])
        self.Map_Paramiters = {"square_px": int(self.config['MAP']['square_px']),"xsize": int(self.config['MAP']['xsize']),"ysize": int(self.config['MAP']['ysize'])}


    def X_Y_To_Square(self,x,y):
        return((math.floor(x/self.squares_step))+((self.Map_Paramiters["ysize"]-1)*self.Map_Paramiters["xsize"])-(math.floor(y/self.squares_step)*self.Map_Paramiters["xsize"]))


        
    def Manual_Move(self,order):
        if(order == "0"):   
            self.cordXY.steps_l = 0
            self.cordXY.steps_r = 0
            self.cordXY.steps_x = 0
            self.cordXY.steps_y = 0
        else:
            self.MM.addorder(order,int(self.manual_steps_entry.get()))
        #self.step_1.CCW(1000)
        #logger.debug("Executing Order" + order + str(self.squares_step))
        #logger.info("FIX ME"+str(order))
    def Manual_Magnet(self,order):
        if(order):
            self.MM.addorder("M",1)
        else:
            self.MM.addorder("M",0)    

    def update_player_map(self,temp):
        logger.info("Map update")
        self.map.update_map(self.player_ref.get())

    def update_orders(self,temp):
        logger.info("new_orders")
        temps = self.orders_q.get()
        if(temps):
            for i in temps:
                temp2 = self.orders_q.get(i)
                print(temp2[0][i])
                self.MM.push_large_order(temp2[0][i])
        self.clear_orders()

    def clear_players(self):
        self.player_ref.set([])
    def clear_orders(self):
        self.orders_q.set([])
        
        
        
#pythoncom.CoInitialize()

logging.basicConfig(level=logging.DEBUG)
#StepperDriver.initlogger(logger)
        
root = tk.Tk()
app = Application(master=root)
app.mainloop()
