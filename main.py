import tkinter as tk
import tkinter.font as tkFont
import sys
import threading
import time
from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests


kts = 5
ktsmin = 5
ktsmax = 35
active = False
deactivate = False
braketrigger = 30
alwaysontop = True
transparency = 0.8
refreshrate = 0.100

datarefresh= time.time()
sm = SimConnectMobiFlight()
vr = MobiFlightVariableRequests(sm)
vr.clear_sim_variables()

class App:
    def __init__(self, root):
        global gslimit_label
        global activate_button
        #setting title
        root.title("SafeTaxi-MSFS2020")
        #setting window size
        width=275
        height=145
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
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
        gslimit_label["fg"] = "#5fb878"
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
        activate_button["bg"] = "grey"
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
        print(kts, "KTS")


    def deckts_button_command(self):
        global kts
        global gslimit_label
        kts -= 5
        if kts < ktsmin:
            kts = ktsmin
        gslimit_label["text"] = str(kts)+" KTS"
        print(kts, "KTS")


    def activate_button_command(self):
        global active
        global activate_button
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
            print("Idle")
            vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
            vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
            print("Release Brake")
            vr.clear_sim_variables()
            activate_button["bg"] = "#ed5555"
        print(active)


def limit():
    global datarefresh
    global active
    global activate_button
    global deactivate
    if int(vr.get("(A:SIM ON GROUND, Bool)")) == 1:
        while deactivate == False:
            if time.time() >= datarefresh:
                brake = int(vr.get("(A:BRAKE LEFT POSITION, percent)"))
                gs = int(vr.get("(A:GPS GROUND SPEED, knots)"))
                throttle = int(vr.get("(A:GENERAL ENG THROTTLE LEVER POSITION:1, percent)"))
                if gs < kts / 2 and throttle != 17:
                    if brake != 0:
                        vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                        vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                        print("Release Brake")
                    vr.set("5000 (>K:THROTTLE_SET)")
                    print("Force Thrust")
                if  kts / 2 <= gs <= kts - 2 and throttle != 1:
                    if brake != 0:
                        vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                        vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                        print("Release Brake")
                    vr.set("3400 (>K:THROTTLE_SET)")
                    print("Thrust")
                if gs >= kts - 1 and throttle != 0:
                    if brake != 0:
                        vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                        vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                        print("Release Brake")
                    vr.set("0 (>K:THROTTLE_SET)")
                    print("Idle")
                if gs >= kts and brake != 9:
                    vr.set("-14383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-14383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    print("Brake")
                if gs >= kts + 2 and brake != 17:
                    vr.set("-12383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-12383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    print("Force Brake")
                if brake >= braketrigger:
                    print("Limiter forced to disable")
                    active = False
                    activate_button["bg"] = "#ed5555"
                    deactivate = True
                    vr.set("0 (>K:THROTTLE_SET)")
                    print("Idle")
                    vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    print("Release Brake")
                    vr.clear_sim_variables()
                datarefresh = time.time() + refreshrate
    else:
        active = False
        activate_button["bg"] = "#ed5555"
                

def on_closing():
    global deactivate
    deactivate = True
    try:
        vr.set("0 (>K:THROTTLE_SET)")
        print("Idle")
        vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
        vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
        print("Release Brake")
        vr.clear_sim_variables()
    except:
        print("Something failed On Exit!")
        pass
    root.destroy()
    print("Clean exit")
    sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
