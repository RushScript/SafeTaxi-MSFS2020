import sys, os, shutil, win32api, win32con, urllib.request, webbrowser, threading, time, configparser
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests
from glob import glob



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



version = "1.0.2"
urlrelease = "https://flightsim.to/file/42867/safetaxi-msfs2020"

kts = 10
refreshrate = 0.100
active = False
deactivate = False

brkrelease = -16383
brkset = -14383
thtset = 20
ththold = "CUT"
braketrigger = 40



try:
    config = configparser.ConfigParser()
    config.read(resource_path("safetaxi.ini"))
    try:
        ktsmin = int(config['CONFIG']['kts_min'])
    except:
        ktsmin = 5
    try:
        ktsmax = int(config['CONFIG']['kts_max'])
    except:
        ktsmax = 35
    try:
        alwaysontop = bool(int(config['CONFIG']['ui_always_on_top']))
    except:
        alwaysontop = True
    try:
        transparency = float(config['CONFIG']['ui_alpha'])
    except:
        transparency = 0.9
    try:
        forceautorun = bool(int(config['CONFIG']['autorun_with_msfs']))
    except:
        forceautorun = False
    try:
        debug = bool(int(config['CONFIG']['enable_debug']))
    except:
        debug = False
except:
    ktsmin = 5
    ktsmax = 35
    alwaysontop = True
    transparency = 0.9
    forceautorun = False
    debug = False



def locatemsfs():
    global msstore
    msstore = False
    msfsfolder = None
    if os.path.isdir(os.path.expanduser('~')+"\\AppData\\Roaming\\Microsoft Flight Simulator"):
        msfsfolder = os.path.expanduser('~')+"\\AppData\\Roaming\\Microsoft Flight Simulator\\"
    elif os.path.isdir(os.path.expanduser('~')+"\\AppData\\Local\\MSFSPackages"):
        msfolder = os.path.expanduser('~')+"\\AppData\\Local\\MSFSPackages\\"
        msstore = True
    else:
        for directories in glob(os.path.expanduser('~')+"\\AppData\\Local\\Packages\\*\\", recursive = False):
            if "Microsoft.FlightSimulator" in directories:
                msfsfolder = directories
                break
    return msfsfolder


def msfsautorun(path):
    if msstore:
        path = path+"\\LocalCache\\"
    try:
        xml = open(path+"exe.xml", "r")
        execfg = xml.read()
        xml.close()
    except:
        shutil.copyfile(resource_path("data\\exe.xml"), path+"exe.xml")
        xml = open(path+"exe.xml", "r")
        execfg = xml.read()
        xml.close()
    if "<Name>SafeTaxi-MSFS2020</Name>" not in execfg:
        fileimport = open(resource_path("data\\exe.import"), "r")
        exeimport = fileimport.read()
        fileimport.close()
        xml = open(path+"exe.xml", "w")
        xml.write(execfg.replace("</SimBase.Document>", "")+exeimport.replace("<Path>safetaxi.exe</Path>", "<Path>"+resource_path("safetaxi.exe")+"</Path>"))
        xml.close()


def firstruncheck(path):
    check = False
    opt = None
    try:
        data = open(path+"safetaxi.opt", "r")
        opt = data.readlines()
        data.close()
        #print(opt[0])
    except:
        with open(path+"safetaxi.opt", "x") as data:
            if win32api.MessageBox(0, "Do you want SafeTaxi to run automatically when MSFS starts?", "SafeTaxi "+version, win32con.MB_YESNO | win32con.MB_ICONQUESTION) == 6:
                data.write(version)
                check = True
            else:
                data.write(version)
        data.close()
    try:
        if opt[0] != version:
            with open(path+"safetaxi.opt", "w") as data:
                data.write(version)
                data.close()
    except:
        pass
    try:
        chkversion = int(version.replace(".", ""))+1
        if urllib.request.urlopen("https://github.com/RushScript/SafeTaxi-MSFS2020/releases/tag/v"+str(chkversion)).getcode() == 200:
            #print("request ok")
            if win32api.MessageBox(0, "A new version of Safe Taxi is now available. Do you want to download the update files?", "SafeTaxi "+version, win32con.MB_YESNO | win32con.MB_ICONQUESTION) == 6:
                webbrowser.open(urlrelease)
    except:
        pass
    if forceautorun:
        check = True
    return check


def listprofiles():
    plist = ["Default Profile"]
    for file in os.listdir(resource_path("profiles")):
        if file.endswith(".ini"):
            plist.append(file.replace(".ini", ""))
            ##print(os.path.join(resource_path("profiles"), file))
    return plist



class App:
    def __init__(self, root):
        global gslimit_label
        global top_label
        global profile_combobox
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
        root.iconbitmap(resource_path("data\\app.ico"))
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
        inckts_button.place(x=67,y=79,width=50,height=20)
        inckts_button["command"] = self.inckts_button_command

        deckts_button=tk.Button(root)
        ft = tkFont.Font(family='Arial',size=10)
        deckts_button["font"] = ft
        deckts_button["fg"] = "#000000"
        deckts_button["bg"] = "grey"
        deckts_button["justify"] = "center"
        deckts_button["text"] = "-5 KTS"
        deckts_button.place(x=15,y=79,width=50,height=20)
        deckts_button["command"] = self.deckts_button_command

        activate_button=tk.Button(root)
        activate_button["bg"] = "#ed5555"
        ft = tkFont.Font(family='Arial',size=16)
        activate_button["font"] = ft
        activate_button["fg"] = "#000000"
        activate_button["bg"] = "#ed5555"
        activate_button["justify"] = "left"
        activate_button["text"] = "Activate"
        activate_button.place(x=160,y=40,width=92,height=60)
        activate_button["command"] = self.activate_button_command

        profile_combobox=ttk.Combobox(root)
        ft = tkFont.Font(family='Arial',size=10)
        profile_combobox["values"] = listprofiles()
        profile_combobox.current([0])
        profile_combobox["state"] = "readonly"
        profile_combobox["takefocus"] = "False"
        profile_combobox["font"] = ft
        profile_combobox["justify"] = "left"
        profile_combobox.place(x=15,y=110,width=140,height=20)
        ##print(profile.get())

##        bar_canvas = tk.Canvas(root)
##        bar_canvas.create_rectangle(0, 0, 0, 0, fill='#f9cb4e', outline='black')
##        bar_canvas["bg"] = "#f9cb4e"
##        bar_canvas["highlightthickness"] = 0
##        bar_canvas.place(x=0, y=0, width=275,height=25)

        top_label=tk.Label(root)
        top_label["anchor"] = "w"
        ft = tkFont.Font(family='Arial',size=10)
        top_label["font"] = ft
        top_label["fg"] = "black"
        top_label["bg"] = "#f9cb4e"
        top_label["justify"] = "left"
        top_label["text"] = version
        top_label.place(x=0,y=0,width=275,height=25)

        

    def inckts_button_command(self):
        global kts
        global gslimit_label
        kts += 5
        if kts > ktsmax:
            kts = ktsmax
        gslimit_label["text"] = str(kts)+" KTS"
        ##print(kts, "KTS")


    def deckts_button_command(self):
        global kts
        global gslimit_label
        kts -= 5
        if kts < ktsmin:
            kts = ktsmin
        gslimit_label["text"] = str(kts)+" KTS"
        ##print(kts, "KTS")


    def activate_button_command(self):
        global active
        global activate_button
        global profile_combobox
        global top_label
        global gslimit_label
        global deactivate
        if active == False:
            active = True
            deactivate = False
            activate_button["bg"] = "#5fb878"
            profile_combobox["state"] = "disable"
            tlimit = threading.Thread(target=limit)
            tlimit.start()
        else:
            active = False
            deactivate = True
            vr.set("(>K:THROTTLE_CUT)")
            ##print("Idle")
            vr.set(str(brkrelease)+" (>K:AXIS_LEFT_BRAKE_SET)")
            vr.set(str(brkrelease)+" (>K:AXIS_RIGHT_BRAKE_SET)")
            ##print("Release Brake")
            vr.clear_sim_variables()
            activate_button["bg"] = "#ed5555"
            profile_combobox["state"] = "readonly"
            gslimit_label["fg"] = "#f2f2f2"
            top_label["text"] = version
        ##print(active)


    def popup(self):
        top= tk.Toplevel(root)
        top.resizable(width=False, height=False)
        top.configure(bg='grey')
        top.overrideredirect(False)
        top.wm_attributes("-topmost", True)
        top.geometry("247x347")
        top.title("Child Window")
        top.eval('tk::PlaceWindow . center')
        self.img = tk.PhotoImage(file = resource_path("data\\img\\cfg.png"))
        imgwiz = tk.Canvas(top)
        imgwiz.create_image( 0,0, image =self.img , anchor = "nw")
        #imgwiz["image"] = tk.PhotoImage(file = resource_path("data\\img\\cfg.png"))
        imgwiz.place(x=0, y=0, width = 274, height = 347)


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
    global profile_combobox
    global gslimit_label
    global top_label
    global deactivate
    global brkrelease
    global brkset
    global thtset
    global ththold
    global braketrigger
    vr.clear_sim_variables()
    profile = profile_combobox.get()
    if profile == "Default Profile":       
        brkrelease = -16383
        brkset = -14383
        thtset = 20
        ththold = "CUT"
        braketrigger = 40
    else:
        config.read(resource_path("profiles\\"+profile+'.ini'))
        brkrelease = float(config['PROFILE']['brake_release'])
        brkset = float(config['PROFILE']['brake_set'])
        thtset = int(config['PROFILE']['thrust_set'])
        ththold = int(config['PROFILE']['thrust_hold'])
        braketrigger = int(config['PROFILE']['deactivate_brake_trigger'])
        if ththold == 0:
            ththold = "CUT"
    brkhold = brkset
    if int(vr.get("(A:SIM ON GROUND, Bool)")) == 1 and int(vr.get("(A:GENERAL ENG RPM:1, rpm)")) >= 100 and vr:
        while deactivate == False:
            if time.time() >= datarefresh:
                brake = int(vr.get("(A:BRAKE LEFT POSITION, percent)"))
                gs = int(vr.get("(A:GPS GROUND SPEED, knots)"))
                throttle = int(vr.get("(A:GENERAL ENG THROTTLE LEVER POSITION:1, percent)"))
                if gs in range(kts - kts, kts - 4):
                    vr.set(str(brkrelease)+" (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set(str(brkrelease)+" (>K:AXIS_RIGHT_BRAKE_SET)")
                    ##print("Release Brake")
                    vr.set("(>K:THROTTLE_"+str(thtset)+")")
                    gslimit_label["fg"] = "#5fb878"
                    ##print("Force Thrust")
                elif gs in range(kts - 4, kts - 1):
                    vr.set(str(brkrelease)+" (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set(str(brkrelease)+" (>K:AXIS_RIGHT_BRAKE_SET)")
                    ##print("Release Brake")
                    vr.set("(>K:THROTTLE_"+ththold+")")
                    gslimit_label["fg"] = "#f2f2f2"
                    ##print("Idle")
                elif gs < kts:
                    brkset = brkset-50
                    vr.set(str(brkset)+" (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set(str(brkset)+" (>K:AXIS_RIGHT_BRAKE_SET)")
                    vr.set("(>K:THROTTLE_"+ththold+")")
                    gslimit_label["fg"] = "#ed5555"
                    ##print("Brake DEC")
                elif gs == kts:
                    brkset = brkhold
                    vr.set(str(brkset)+" (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set(str(brkset)+" (>K:AXIS_RIGHT_BRAKE_SET)")
                    vr.set("(>K:THROTTLE_"+ththold+")")
                    gslimit_label["fg"] = "#ed5555"
                    ##print("Brake")
                elif gs > kts:
                    brkset = brkset+50
                    vr.set(str(brkset)+" (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set(str(brkset)+" (>K:AXIS_RIGHT_BRAKE_SET)")
                    vr.set("(>K:THROTTLE_"+ththold+")")
                    gslimit_label["fg"] = "#ed5555"
                    ##print("Brake INC")
                if brake >= braketrigger:
                    print("Limiter forced to disable")
                    active = False
                    activate_button["bg"] = "#ed5555"
                    profile_combobox["state"] = "readonly"
                    deactivate = True
                    vr.set("(>K:THROTTLE_CUT)")
                    ##print("Idle")
                    vr.set(str(brkrelease)+" (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set(str(brkrelease)+" (>K:AXIS_RIGHT_BRAKE_SET)")
                    gslimit_label["fg"] = "#f2f2f2"
                    top_label["text"] = version
                    ##print("Release Brake")
                    vr.clear_sim_variables()
                datarefresh = time.time() + refreshrate
                if int(vr.get("(A:SIM ON GROUND, Bool)")) == 0:
                    deactivate = True
                    activate_button["bg"] = "#ed5555"
                    profile_combobox["state"] = "readonly"
                    gslimit_label["fg"] = "#f2f2f2"
                    top_label["text"] = version
                    vr.clear_sim_variables()
                if debug:
                    top_label["text"] = "KTS: "+str(gs), "THT: "+str(throttle)+"%", "BRK: "+str(brake)+"%"
                else:
                    top_label["text"] = "GS: "+str(gs)+" KTS"
        top_label["text"] = version
        vr.clear_sim_variables()                                       
    else:
        active = False
        activate_button["bg"] = "#ed5555"
        profile_combobox["state"] = "readonly"
        gslimit_label["fg"] = "#f2f2f2"
        top_label["text"] = version
        vr.clear_sim_variables()
                       

def on_closing():
    global deactivate
    deactivate = True
    try:
        vr.set("(>K:THROTTLE_CUT)")
        ##print("Idle")
        vr.set(str(brkrelease)+" (>K:AXIS_LEFT_BRAKE_SET)")
        vr.set(str(brkrelease)+" (>K:AXIS_RIGHT_BRAKE_SET)")
        ##print("Release Brake")
        vr.clear_sim_variables()
    except:
        ##print("Something failed On Exit!")
        pass
    root.destroy()
    ##print("Clean exit")
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
##    app.popup()
    root.mainloop()
