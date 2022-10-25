from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests
from time import sleep

sm = SimConnectMobiFlight()
vr = MobiFlightVariableRequests(sm)
vr.clear_sim_variables()

refresh = 0.100

def limit(knots):
    if int(vr.get("(A:SIM ON GROUND, Bool)")) == 1:
        while True:
            brake = int(vr.get("(A:BRAKE LEFT POSITION, percent)"))
            gs = int(vr.get("(A:GPS GROUND SPEED, Knots)"))
            throttle = int(vr.get("(A:GENERAL ENG THROTTLE LEVER POSITION:1, percent)"))
            if brake >= 50:
                print("Limiter forced to disable")
                vr.clear_sim_variables()
                break
            if gs < knots / 2 and throttle != 17:
                if brake != 0:
                    vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    print("Release Brake")
                vr.set("5000 (>K:THROTTLE_SET)")
                print("Force Thrust")
            if  knots / 2 <= gs <= knots - 2 and throttle != 1:
                if brake != 0:
                    vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    print("Release Brake")
                vr.set("3400 (>K:THROTTLE_SET)")
                print("Thrust")
            if gs >= knots - 1 and throttle != 0:
                if brake != 0:
                    vr.set("-16383 (>K:AXIS_LEFT_BRAKE_SET)")
                    vr.set("-16383 (>K:AXIS_RIGHT_BRAKE_SET)")
                    print("Release Brake")
                vr.set("0 (>K:THROTTLE_SET)")
                print("Idle")
            if gs >= knots and brake != 9:
                vr.set("-14383 (>K:AXIS_LEFT_BRAKE_SET)")
                vr.set("-14383 (>K:AXIS_RIGHT_BRAKE_SET)")
                print("Brake")
            if gs >= knots + 2 and brake != 17:
                vr.set("-12383 (>K:AXIS_LEFT_BRAKE_SET)")
                vr.set("-12383 (>K:AXIS_RIGHT_BRAKE_SET)")
                print("Force Brake")
            sleep (refresh)

# Example write variable
#vr.set("1 (>L:PUSH_OVHD_CALLS_ALL)")
##
##while True:
##    alt_ground = vr.get("(A:GROUND ALTITUDE,Meters)")
##    alt_plane = vr.get("(A:PLANE ALTITUDE,Feet)")
##    # FlyByWire A320
##    ap1 = vr.get("(L:A32NX_AUTOPILOT_1_ACTIVE)")
##    hdg = vr.get("(L:A32NX_AUTOPILOT_HEADING_SELECTED)")
##    mode = vr.get("(L:A32NX_FMA_LATERAL_MODE)")
##    sleep(1)

##while True:
##    print(int(vr.get("(A:GPS GROUND SPEED, Knots)")))
##    print(vr.get("(A:SIM ON GROUND, Bool)"))
##    sleep (0.100)

## vr.set("3400 (>K:THROTTLE_SET)")    //    Soft
## vr.set("4000 (>K:THROTTLE_SET)")    //    Soft-Medium
## vr.set("5000 (>K:THROTTLE_SET)")    //    Medium-Force


##  vr.set("-14383 (>K:AXIS_LEFT_BRAKE_SET)")    //    Soft
##  vr.set("-14383 (>K:AXIS_RIGHT_BRAKE_SET)")
    
##  vr.set("-13383 (>K:AXIS_LEFT_BRAKE_SET)")    //    Medium
##  vr.set("-13383 (>K:AXIS_RIGHT_BRAKE_SET)")

##  vr.set("-13383 (>K:AXIS_LEFT_BRAKE_SET)")    //    Medium-Force
##  vr.set("-13383 (>K:AXIS_RIGHT_BRAKE_SET)")
