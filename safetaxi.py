import tkinter as tk
import tkinter.font as tkFont
import win32api, win32con
import sys, os
import threading
import time
from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests
from glob import glob


version = "1.0.1"

kts = 5
ktsmin = 5
ktsmax = 35
active = False
deactivate = False
braketrigger = 30
alwaysontop = True
transparency = 0.9
refreshrate = 0.100     


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def locatemsfs():
    msfsfolder = None
    if os.path.isdir(os.path.expanduser('~')+"\\AppData\\Roaming\\Microsoft Flight Simulator"):
        msfsfolder = os.path.expanduser('~')+"\\AppData\\Roaming\\Microsoft Flight Simulator\\"
    elif os.path.isdir(os.path.expanduser('~')+"\\AppData\\Local\\MSFSPackages"):
        msfolder = os.path.expanduser('~')+"\\AppData\\Local\\MSFSPackages\\"
    else:
        for directories in glob(os.path.expanduser('~')+"\\AppData\\Local\\Packages\\*\\", recursive = False):
            if "Microsoft.FlightSimulator" in directories:
                msfsfolder = directories
                break
    return msfsfolder


def msfsautorun(path):
    xml = open(path+"exe.xml", "r")
    execfg = xml.read()
    xml.close()
    if "<Name>SafeTaxi-MSFS2020</Name>" not in execfg:
        fileimport = open(resource_path("exe.import"), "r")
        exeimport = fileimport.read()
        fileimport.close()
        xml = open(path+"exe.xml", "w")
        xml.write(execfg.replace("</SimBase.Document>", "")+exeimport.replace("<Path>safetaxi.exe</Path>", "<Path>"+resource_path("safetaxi.exe")+"</Path>"))
        xml.close()


def firstruncheck(path):
    check = False
    try:
        data = open(path+"safetaxi.opt", "r")
        opt = data.readlines()
    except:
        if win32api.MessageBox(0, "Do you want SafeTaxi to run automatically when MSFS starts?", "SafeTaxi "+version, win32con.MB_YESNO | win32con.MB_ICONQUESTION) == 6:
            with open(path+"safetaxi.opt", "x") as data:
                data.write(version)
                check = True
    return check


class App:
    def __init__(self, root):
        global gslimit_label
        global activate_button
        #setting title
        root.title("SafeTaxi "+version)
        #setting window size
        width=275
        height=145
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        root.iconbitmap(resource_path("app.ico"))
        # Hide the root window drag bar and close button
        root.overrideredirect(False)
        # Make the root window always on top
        root.wm_attributes("-topmost", alwaysontop)
        root.configure(bg='grey')
        # Turn off the window shadow
        root.attributes("-alpha", transparency)


        gslimit_label=tk.Label(root)
        gslimit_label["anchor"] = "center"
        ft = tkFont.Font(family='Arial',size=26)
        gslimit_label["font"] = ft
        gslimit_label["fg"] = "#f2f2f2"
        gslimit_label["bg"] = "grey"
        gslimit_label["justify"] = "center"
        gslimit_label["text"] = str(kts)+" KTS"
        gslimit_label.place(x=10,y=40,width=115,height=30)

        inckts_button=tk.Button(root)
        ft = tkFont.Font(family='Arial',size=10)
        inckts_button["font"] = ft
        inckts_button["fg"] = "#000000"
        inckts_button["bg"] = "grey"
        inckts_button["justify"] = "center"
        inckts_button["text"] = "+5 KTS"
        inckts_button.place(x=67,y=80,width=50,height=20)
        inckts_button["command"] = self.inckts_button_command

        deckts_button=tk.Button(root)
        ft = tkFont.Font(family='Arial',size=10)
        deckts_button["font"] = ft
        deckts_button["fg"] = "#000000"
        deckts_button["bg"] = "grey"
        deckts_button["justify"] = "center"
        deckts_button["text"] = "-5 KTS"
        deckts_button.place(x=15,y=80,width=50,height=20)
        deckts_button["command"] = self.deckts_button_command

        activate_button=tk.Button(root)
        activate_button["bg"] = "#ed5555"
        ft = tkFont.Font(family='Arial',size=16)
        activate_button["font"] = ft
        activate_button["fg"] = "#000000"
        activate_button["bg"] = "#ed5555"
        activate_button["justify"] = "center"
        activate_button["text"] = "Activate"
        activate_button.place(x=160,y=40,width=92,height=60)
        activate_button["command"] = self.activate_button_command


    def inckts_button_command(self):
        global kts
        global gslimit_label
        kts += 5
        if kts > ktsmax:
            kts = ktsmax
        gslimit_label["text"] = str(kts)+" KTS"
        #print(kts, "KTS")


    def deckts_button_command(self):
        global kts
        global gslimit_label
        kts -= 5
        if kts < ktsmin:
            kts = ktsmin
        gslimit_label["text"] = str(kts)+" KTS"
        #print(kts, "KTS")


    def activate_button_command(self):
        global active
        global activate_button
        global gslimit_label
        global deactivate
        if active == False:
            active = True
            deactivate = False
            activate_button["bg"] = "#5fb878"
            tlimit = threading.Thread(target=limit)
            tlimit.start()
        else:
            active = False
            deactivate = True
            vr.set("0 (>K:THROTTLE_SET)")
            #print("Idle")
            vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
            vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
            #print("Release Brake")
            vr.clear_sim_variables()
            activate_button["bg"] = "#ed5555"
            gslimit_label["fg"] = "#f2f2f2"
        #print(active)


def wasmconnect():
    global datarefresh
    global sm
    global vr
    datarefresh= time.time()
    sm = SimConnectMobiFlight()
    vr = MobiFlightVariableRequests(sm)
    vr.clear_sim_variables()


def limit():
    global datarefresh
    global active
    global activate_button
    global gslimit_label
    global deactivate
    if int(vr.get("(A:SIM ON GROUND, Bool)")) == 1 and int(vr.get("(A:GENERAL ENG RPM:1, rpm)")) >= 100 and vr:
        while deactivate == False:
            if time.time() >= datarefresh:
                brake = int(vr.get("(A:BRAKE LEFT POSITION, percent)"))
                gs = int(vr.get("(A:GPS GROUND SPEED, knots)"))
                throttle = int(vr.get("(A:GENERAL ENG THROTTLE LEVER POSITION:1, percent)"))
                if gs < kts / 2 and throttle != 17:
                    if brake != 0:
                        vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                        vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                        #print("Release Brake")
                    vr.set("5000 (>K:THROTTLE_SET)")
                    gslimit_label["fg"] = "#5fb878"
                    #print("Force Thrust")
                if  kts / 2 <= gs <= kts - 2 and throttle != 1:
                    if brake != 0:
                        vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                        vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                        #print("Release Brake")
                    vr.set("3400 (>K:THROTTLE_SET)")
                    gslimit_label["fg"] = "#5fb878"
                    #print("Thrust")
                if gs >= kts - 1 and throttle != 0:
                    if brake != 0:
                        vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                        vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                        #print("Release Brake")
                    vr.set("0 (>K:THROTTLE_SET)")
                    gslimit_label["fg"] = "#f2f2f2"
                    #print("Idle")
                if gs >= kts and brake != 9:
                    vr.set("-14383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-14383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    gslimit_label["fg"] = "#ed5555"
                    #print("Brake")
                if gs >= kts + 2 and brake != 17:
                    vr.set("-12383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-12383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    gslimit_label["fg"] = "#ed5555"
                    #print("Force Brake")
                if brake >= braketrigger:
                    #print("Limiter forced to disable")
                    active = False
                    activate_button["bg"] = "#ed5555"
                    deactivate = True
                    vr.set("0 (>K:THROTTLE_SET)")
                    #print("Idle")
                    vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    gslimit_label["fg"] = "#f2f2f2"
                    #print("Release Brake")
                    vr.clear_sim_variables()
                datarefresh = time.time() + refreshrate
                if int(vr.get("(A:SIM ON GROUND, Bool)")) == 0:
                    deactivate = True

                                        
    else:
        active = False
        activate_button["bg"] = "#ed5555"
        gslimit_label["fg"] = "#f2f2f2"
                       

def on_closing():
    global deactivate
    deactivate = True
    try:
        vr.set("0 (>K:THROTTLE_SET)")
        #print("Idle")
        vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
        vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
        #print("Release Brake")
        vr.clear_sim_variables()
    except:
        #print("Something failed On Exit!")
        pass
    root.destroy()
    #print("Clean exit")
    sys.exit(0)


if __name__ == "__main__":
    msfsfolder = locatemsfs()
    if firstruncheck(msfsfolder):
        msfsautorun(msfsfolder) 
    datarefresh= time.time()
    sm = SimConnectMobiFlight()
    vr = MobiFlightVariableRequests(sm)
    vr.clear_sim_variables()
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
##    twasmconnect = threading.Thread(target=wasmconnect)
##    twasmconnect.start()
    root.mainloop()
