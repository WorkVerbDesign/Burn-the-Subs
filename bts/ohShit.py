import time

import serial

from bts import settings

speed = settings.serialSpeed
serialLoc = settings.serialAddy

reset = settings.pwr_cycle
homies = settings.homing
pullout = settings.pulloff_pos

def stopit():
    print("FUCK FUCK FUCK")
    s = serial.Serial(serialLoc, speed)
    s.write(reset.encode())
    time.sleep(2)
    s.write(homies.encode())
    s.write(pullout.encode())
    print("phew")

if __name__ == "__main__":
    stopit()